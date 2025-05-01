#!/usr/bin/env python

from collections.abc import Iterable
import sys
import itertools


def _all_whitespace(s: str) -> bool:
    return all(c.isspace() for c in s)


def _split_normal_and_saved(config: str, identifier: str) -> tuple[list[str], list[str]]:
    normal = []
    saved = []
    in_saved = False

    for i, line in enumerate(config.splitlines(keepends=True)):
        is_saved_line = line.startswith("#*#")
        if in_saved:
            if is_saved_line or _all_whitespace(line):
                saved.append(line)
            else:
                raise Exception(f"Normal lines mixed with saved lines ({identifier}:{i + 1}: {line!r})")
        else:
            if is_saved_line:
                in_saved = True
                saved.append(line)
            else:
                normal.append(line)

    print(identifier, len(normal), len(saved))
    return (normal, saved)


def _trim_trailing_whitespace_lines(lines: list[str]):
    while len(lines):
        if _all_whitespace(lines[-1]):
            lines.pop()
        else:
            break


def merge_klipper_config(local_lines: str, remote_lines: str) -> str:
    (local_normal, _local_saved) = _split_normal_and_saved(local_lines, "local")
    (_remote_normal, remote_saved) = _split_normal_and_saved(remote_lines, "remote")

    _trim_trailing_whitespace_lines(remote_saved)

    if len(remote_saved) and not _all_whitespace(local_normal[-1]):
        local_normal.append("\n")

    return "".join(itertools.chain(local_normal, remote_saved))


def main():
    with open(sys.argv[1], "r") as local_config:
        local_config = local_config.read()
    remote_config = sys.stdin.read()

    merged = merge_klipper_config(local_config, remote_config)
    merged = "".join(merged)

    if merged == local_config:
        sys.exit(254)
    else:
        with open(sys.argv[1], "w") as local_config:
            local_config.write(merged)
        sys.exit(0)


if __name__ == "__main__":
    main()
