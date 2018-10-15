[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/917)

# <sup><sub><sup><sub>[ebb &]</sub></sup></sub></sup> Flow

Experiment pipeline

TODO

# Tools

## Deploy code to singularity-hub

Include it in .travis.yml files for automatic deployment after successful tests.

```bash
flow-deploy ...
```

## Submit jobs on clusters

Using SmartDispatch as a backend

```bash
flow-submit [SCHEDULER OPTIONS] [COMMAND] ...
```

Can be combined with `flow-execute`

```bash
flow-submit [SCHEDULER OPTIONS] flow-execute shub://bouthilx/my-experiment:version [COMMAND] ...
```

## Execute jobs using singularity containers

```bash
flow-execute shub://bouthilx/my-experiment:version [COMMAND] ...
```

# Install

TODO

# Configuration

In .bashrc or similar,

```bash
SINGULARITY_DIR=/some/path/to/singularity
export SREGISTRY_STORAGE=$SINGULARITY_DIR
export SINGULARITY_CACHEDIR=$SINGULARITY_DIR/cache
export SREGISTRY_DATABASE=$SINGULARITY_DIR
export SREGISTRY_NVIDIA_TOKEN=<SECRET>

export DATA_FOLDER=/some/path/to/data
```

If using mongodb secured with a certificate,

```bash
export CERTIFICATE_FOLDER=/some/path/to/certs
```
TODO

# Containers

[![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/917)

## Pytorch 0.3.1
