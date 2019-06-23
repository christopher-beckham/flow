# <sup><sub><sup><sub>[ebb &]</sub></sup></sub></sup> Flow

Experiment pipeline.

## Instructions

Clone this repo, and install it by running `python setup.py develop`. Then, add this blurb to your `~/.bashrc`:

```
FLOW_DIR=<path to your flow github repo>/flow/bin
export FLOW_DIR
alias flow-submit="python $FLOW_DIR/flow/submit.py"
```

Then, for whatever research repository you'd like to use this for, make a script which invokes `flow-submit`. For example, for one of my projects, I have a script on the Compute Canada cluster called `flow_submit_celeba_8g.sh`:

```
#!/bin/bash

echo "Submitting script: " $1

flow-submit \
--prolog="source ../envs/env_celeba.sh cc" `# copy celeba dataset to tmp dir` \
--resume \
--options "mem=8G;time=12:00:00;account=rpp-bengioy;ntasks=1;cpus-per-task=4;gres=gpu:1" \
--root=`pwd` \
launch $1
```
