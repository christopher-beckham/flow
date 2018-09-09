import re


TIME_REGEX = re.compile(
    "^(?:(?:(?:(\d*):)?(\d*):)?(\d*):)?(\d*)$")


def walltime_to_seconds(walltime):
    if not TIME_REGEX.match(walltime):
        raise ValueError(
            "Invalid walltime format: %s\n"
            "It must be either DD:HH:MM:SS, HH:MM:SS, MM:SS or S" %
            walltime)

    split = walltime.split(":")

    while len(split) < 4:
        split = [0] + split

    days, hours, minutes, seconds = map(int, split)

    return (((((days * 24) + hours) * 60) + minutes) * 60) + seconds
