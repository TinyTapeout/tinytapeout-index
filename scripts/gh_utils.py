# SPDX-License-Identifier: Apache-2.0
# Shared utilities for scripts that interact with GitHub via the gh CLI.
# Copyright (C) 2026 Tiny Tapeout LTD

import json
import re
import subprocess
import sys


def parse_run_url(url):
    match = re.match(
        r"https://github\.com/([^/]+)/([^/]+)/actions/runs/(\d+)", url
    )
    if not match:
        print(f"Error: Invalid run URL: {url}", file=sys.stderr)
        sys.exit(1)
    return match.group(1), match.group(2), match.group(3)


def gh(args):
    result = subprocess.run(["gh"] + args, capture_output=True)
    if result.returncode != 0:
        print(
            f"Error: gh {' '.join(args)} failed: {result.stderr.decode()}",
            file=sys.stderr,
        )
        sys.exit(1)
    return result.stdout.decode().strip()


def find_release_for_commit(owner, repo, commit):
    """Returns the release dict whose tag points at the given commit, or None."""
    releases = json.loads(gh(["api", f"repos/{owner}/{repo}/releases"]))
    for release in releases:
        tag = release["tag_name"]
        tag_info = json.loads(
            gh(["api", f"repos/{owner}/{repo}/git/ref/tags/{tag}"])
        )
        if tag_info["object"]["sha"] == commit:
            return release
    return None
