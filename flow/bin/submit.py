#!/usr/bin/env python
"""
Highly inspired from https://github.com/SMART-Lab/smartdispatch
"""

import argparse
import asyncio
import logging
import os
import re
import sys
import uuid

from flow.utils.commandline import execute
from flow.utils.time import walltime_to_seconds


logger = logging.getLogger(__name__)


TEMPLATE = """\
#!/usr/bin/env bash

{options}

# Prolog # 

{prolog}

# Command #

{command}

# Epilog #

{epilog}\
"""

OPTION = """\
#SBATCH --{option}={value}\
"""

PROLOG = """\
TIMEOUT_EXIT_CODE=124
VERBOSE=true
WORKER_PIDS=""
SBATCH_TIMELIMIT={timelimit}
"""

COMMAND = """\
timeout -s TERM $(($SBATCH_TIMELIMIT - 300)) flow-execute {container} {command} & WORKER_PIDS+=" $!"
"""

EPILOG = """\
NEED_TO_RESUME=false
if [ $VERBOSE = true ]; then
    echo NEED_TO_RESUME=$NEED_TO_RESUME
    echo WORKER_PIDS=$WORKER_PIDS
fi
for WORKER_PID in $WORKER_PIDS; do
    if [ $VERBOSE = true ]; then
        echo WORKER_PID=$WORKER_PID
    fi
    wait "$WORKER_PID"
    RETURN_CODE=$?
    if [ $VERBOSE = true ]; then
        echo "RETURN_CODE is $RETURN_CODE while timeout_exit_code is 124"
    fi
    if [ $RETURN_CODE -eq 124 ]; then
        NEED_TO_RESUME=true
    fi
    if [ $VERBOSE = true ]; then
        echo NEED_TO_RESUME=$NEED_TO_RESUME
    fi
done

if [ $VERBOSE = true ]; then
    echo NEED_TO_RESUME=$NEED_TO_RESUME
fi

if [ "$NEED_TO_RESUME" = true ]; then
    if [ -z $SLURM_ARRAY_JOB_ID ] || [ "$SLURM_ARRAY_JOB_ID" = "$SLURM_JOB_ID" ]; then
        if [ $VERBOSE = true ]; then
            echo "Resubmitting {file_path}"
        fi
        sbatch {file_path}
    elif [ $VERBOSE = true ]; then
        echo "Job $SLURM_ARRAY_TASK_ID from array $SLURM_ARRAY_JOB_ID"
        echo "Not submitting."
    fi
elif [ $VERBOSE = true ]; then
    echo "Job completed, no need to resubmit"
fi\
"""


def get_unique_file_numbered(file_path):
    basefilename, fileext = os.path.splitext(os.path.abspath(file_path))

    FILE_NUMBER_REGEX = re.compile(
        "{file_path}.[0-9]{{5}}.sh$".format(file_path=os.path.basename(basefilename)))

    dirname = os.path.dirname(basefilename)
    number = sum(bool(FILE_NUMBER_REGEX.match(filename)) for filename in os.listdir(dirname))

    numbered_file_path = "{file_path}.{number:05d}{ext}".format(
        file_path=basefilename, number=number, ext=fileext)

    try:
        open(numbered_file_path, 'x').close()
    except FileExistsError as e:
        numbered_file_path = get_unique_file_numbered(file_path)

    return numbered_file_path


def verify_env(options):
    if "GPU_SLURM_ACCOUNT" not in os.environ and 'gpu' in options.get('gres', ''):
        raise SystemExit('Error: Requesting gpu, but gpu slurm account not defined. '
                         'Please set $GPU_SLURM_ACCOUNT')
    elif "SLURM_ACCOUNT" not in os.environ:
        raise SystemExit('Error: slurm account not defined. Please set $SLURM_ACCOUNT')

    if "SCRATCH" not in os.environ:
        raise SystemExit('Error: scratch space not defined. Please set $SCRATCH')


OPTION_REGEX = re.compile("^#SBATCH --?([a-zA-Z]+.*?)=(.*?)$")

def read_options_from_file(file_options):
    if file_options is None or not os.path.exists(file_options):
        return {}

    options = {}
    with open(file_options, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            match = OPTION_REGEX.match(line)
            if match:
                key, value = match.groups()
                logger.info("Found ({key}, {value})".format(key=key, value=value))
                options[key] = value
            else:
                logger.debug("Ignoring: {}".format(line))

    return options


def read_options_from_cmdline(cmdline_options):
    options = {}

    for option in cmdline_options.split(";"):
        split = option.strip().split("=")
        key = split[0]
        value = "=".join(split[1:])

        options[key] = value

    return options


def gather_options(file_options, cmdline_options):
    options = read_options_from_file(file_options)
    options.update(read_options_from_cmdline(cmdline_options))

    return options


def update_options(file_path, options):

    if "job-name" not in options:
        options["job-name"] = fetch_default_job_name(file_path)

    if "account" not in options and "gpu" in options.get('gres', ''):
        options['account'] = os.environ.get('GPU_SLURM_ACCOUNT', '')
    elif "account" not in options:
        options['account'] = os.environ.get('SLURM_ACCOUNT', '')

    if "mem" not in options:
        raise SystemExit("ERROR: Option mem is not set and cannot be infered")

    if "cpus-per-task" not in options:
        options['cpus-per-task'] = 1

    if "export" not in options:
        options['export'] = 'ALL'

    if "output" not in options:
        options['output'] = file_path + ".%A.%a.out"

    if "error" not in options:
        options['error'] = file_path + ".%A.%a.err"

    return options


def format_commandline(commandline):

    args = []

    for arg in commandline:

        if ";" in arg:
            arg = "'{}'".format(arg)

        args.append(arg)

    return " ".join(args)


def fetch_default_job_name(file_path):

    basename = os.path.basename(os.path.splitext(file_path)[0])
    base = [directory for directory in file_path.split(os.path.sep)[-3:-1] if directory]
    return ".".join(base + [basename])


def main(argv=None):

    parser = argparse.ArgumentParser(description="Submit commands with sbatch")

    parser.add_argument('container', help='Singularity container to execute within the script')

    parser.add_argument('--root', help='Root directory for SBATCH configuration script file')

    parser.add_argument('--config', help='SBATCH configuration script file')

    parser.add_argument('--options', type=str, help='SBATCH configuration from cmdline')

    parser.add_argument('--resume', action='store_true',
                        help='Resubmit job at end of execution. Note that for arrays only the job '
                             '0 will resubmit, and it will resubmit the entire array')

    parser.add_argument('--prolog', type=str, help='Commands to execute before the script')

    parser.add_argument('--print-only', action="store_true",
                        help=('Print script that would be submitted without submitting it. '
                              'The file is deleted at end of execution.'))

    parser.add_argument('--generate-only', action="store_true",
                        help='Generate file that would be submitted without submitting it.')

    subparsers = parser.add_subparsers(dest="mode")

    launch_parser = subparsers.add_parser('launch', help="Launch job execution")

    launch_parser.add_argument('commandline', nargs=argparse.REMAINDER,
                               help='Commandline to execute with the sbatch script')

    args = parser.parse_args(argv)

    if args.root is None:
        root = os.environ['SCRATCH']
    else:
        root = args.root

    if args.config is None:
        if not os.path.isdir(root):
            os.makedirs(root)
        file_path = os.path.join(root, uuid.uuid4().hex + ".sh")
    else:
        file_path = args.config

    print("Submitting {}".format(file_path))
    print("With container {}".format(args.container))
    print("With arguments {}".format(args.commandline))

    file_path = get_unique_file_numbered(file_path)
    print("Creating new file: {}".format(file_path))

    try:
        script = generate_script(args, file_path)
    finally:
        if args.print_only and os.path.exists(file_path):
            os.remove(file_path)
    
    if args.print_only:
        print(script)
        sys.exit(0)

    with open(file_path, 'w') as f:
        f.write(script)

    if args.generate_only:
        sys.exit(0)

    commandline = 'sbatch {}'.format(file_path)
    print("Executing: {}".format(commandline))
    asyncio.get_event_loop().run_until_complete(execute(commandline))


def generate_script(args, file_path):
    options = gather_options(args.config, args.options)

    update_options(file_path, options)

    options_str = "\n".join(OPTION.format(option=key, value=value)
                            for key, value in sorted(options.items()))
    prolog = PROLOG.format(timelimit=walltime_to_seconds(options['time']))

    if args.prolog:
        prolog += '\n' + "\n".join(line for line in args.prolog.split("\n") if line) + '\n'

    command = COMMAND.format(container=args.container, command=format_commandline(args.commandline))
    if args.resume:
        epilog = EPILOG.format(file_path=file_path)
    else:
        epilog = ''

    return TEMPLATE.format(options=options_str, prolog=prolog, command=command, epilog=epilog)


if __name__ == "__main__":
    main()
