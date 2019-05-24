import asyncio


@asyncio.coroutine
def log_stream(stream):
    while not stream.at_eof():
        data = yield from stream.readline()
        if data:
            line = data.decode('ascii').rstrip()
            print(line)


@asyncio.coroutine 
def execute(commandline, print_only=False):
    if print_only:
        print(commandline)
        return

    # To make sure we have no discrepency between std{out,err} and logged data from clients process
    create = asyncio.create_subprocess_exec(*commandline.split(" "), 
                                            stdout=asyncio.subprocess.PIPE,
                                            stderr=asyncio.subprocess.PIPE)

    proc = yield from create

    create_task = getattr(asyncio, 'ensure_future')

    tasks = [create_task(log_stream(proc.stdout)),
             create_task(log_stream(proc.stderr)),
             create_task(proc.wait())]

    yield from asyncio.wait(tasks)
