#! /usr/bin/env python3

# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import sys
import time
from enum import Enum
from subprocess import PIPE, run

logger = logging.getLogger(__name__)


class VersionPart(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


def is_current_branch_releasable() -> bool:
    result = run(
        ["/usr/bin/git", "rev-parse", "--abrev-ref", "HEAD"],
        stdout=PIPE,
        check=True,
        text=True,
    )
    current_branch = result.stdout.strip()
    return current_branch in ["staging", "production"]


def get_current_version() -> str:
    result = run(["hatch", "version"], stdout=PIPE, check=True, text=True)  # noqa: S607
    return result.stdout.strip()


def get_next_dev_version(
    current_version: str, part: VersionPart | None, timestamp: int
) -> str:
    base_version = (current_version).split(".", maxsplit=4)
    logger.info("Base version: %s", base_version)

    major, minor, patch = map(int, base_version[:3])

    if part == VersionPart.MAJOR:
        major += 1
    if part == VersionPart.MINOR:
        minor += 1
    if part == VersionPart.PATCH:
        patch += 1

    return f"{major}.{minor}.{patch}-dev+{timestamp}"


def parse_args():
    parser = argparse.ArgumentParser(description="Tag script")
    parser.add_argument(
        "--part",
        type=str,
        choices=[p.value for p in VersionPart],
        default=None,
        help="The part to tag",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Create a dev version instead of a release version",
    )
    return parser.parse_args()


def main():
    current_version = get_current_version()
    current_version_is_release = "dev" not in current_version

    args = parse_args()
    next_version_is_release = args.part is not None and not args.dev
    """
    If no part is specified then the new version is a dev version.

    release -> release: we need to increment the specified part.
    dev -> release: increment the specified part (must be specified always)

    release -> dev: we need to increment any specified part or the patch number
        and add the dev suffix.
    dev -> dev: we need to increment the dev suffix, increment any part if specified,
        otherwise keep the same major, minor, and patch numbers and just
        update the dev suffix.

    """

    if next_version_is_release:
        logger.info("{dev, release} -> release")
        run(  # noqa: S603
            ["hatch", "version", VersionPart(args.part).value],  # noqa: S607
            check=True,
        )
        return 0

    logger.info("{dev, release} -> dev")
    part = (
        VersionPart(args.part)
        if args.part
        else (VersionPart.PATCH if current_version_is_release else None)
    )
    new_version = get_next_dev_version(
        current_version=current_version, part=part, timestamp=int(time.time())
    )

    logger.info("Setting version to %s", new_version)
    run(["hatch", "version", new_version], check=True)  # noqa: S603,S607
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
