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

## Render results

```bash
flow-analyze
```

```bash
flow-compare
```

# Install

TODO

# Configuration

TODO
