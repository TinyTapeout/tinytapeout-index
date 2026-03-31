#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Update index/index.json from a GitHub Actions run URL.
# Copyright (C) 2026 Tiny Tapeout LTD
# Author: Uri Shaked

import argparse
import base64
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml


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


def download_shuttle_index(owner, repo, run_id):
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [
                "gh", "run", "download", run_id,
                "-n", "shuttle_index",
                "-R", f"{owner}/{repo}",
                "-D", tmpdir,
            ],
            check=True,
        )
        with open(Path(tmpdir) / "shuttle_index.json") as f:
            return json.load(f)


def get_repo_config(owner, repo):
    content = gh(
        ["api", f"repos/{owner}/{repo}/contents/config.yaml", "--jq", ".content"]
    )
    decoded = base64.b64decode(content).decode()
    return yaml.safe_load(decoded)


def get_total_tiles(shuttle_id):
    url = f"https://app.tinytapeout.com/api/shuttles/{shuttle_id}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "tinytapeout-index/1.0")
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    return data["tiles"]["total"]


def main():
    parser = argparse.ArgumentParser(
        description="Update index.json from a GitHub Actions run"
    )
    parser.add_argument("run_url", help="GitHub Actions run URL")
    args = parser.parse_args()

    owner, repo_name, run_id = parse_run_url(args.run_url)

    print(f"Downloading shuttle_index from {owner}/{repo_name} run {run_id}...")
    shuttle_data = download_shuttle_index(owner, repo_name, run_id)

    print("Reading config.yaml...")
    config = get_repo_config(owner, repo_name)
    shuttle_id = config.get("id")
    if not shuttle_id:
        print("Error: could not determine shuttle id from config.yaml", file=sys.stderr)
        sys.exit(1)
    pdk = config.get("pdk", "unknown")

    num_projects = len(shuttle_data["projects"])
    commit_short = shuttle_data["commit"][:8]
    rom_data = (
        f"shuttle={shuttle_id}\nrepo={owner}/{repo_name}\ncommit={commit_short}\n"
    )

    total_tiles = get_total_tiles(shuttle_id)

    root = Path(__file__).resolve().parents[1]
    index_path = root / "index" / "index.json"
    with open(index_path) as f:
        index = json.load(f)

    existing_idx = next(
        (i for i, s in enumerate(index["shuttles"]) if s["id"] == shuttle_id), None
    )

    if existing_idx is not None:
        entry = index["shuttles"][existing_idx]
        entry["rom_data"] = rom_data
        entry["tiles"] = total_tiles
        entry["projects"] = num_projects
        print(f"Updated existing entry for {shuttle_id}")
    else:
        entry = {
            "id": shuttle_id,
            "name": shuttle_data["name"],
            "repo": shuttle_data["repo"],
            "gds_url": None,
            "rom_data": rom_data,
            "project_gds_url_template": f"https://raw.githubusercontent.com/{owner}/{repo_name}/main/projects/{{macro}}/{{macro}}.oas",
            "pdk": pdk,
            "tiles": total_tiles,
            "projects": num_projects,
        }
        index["shuttles"].append(entry)
        print(f"Added new entry for {shuttle_id}")

    now = datetime.now(timezone.utc)
    index["updated"] = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"

    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
        f.write("\n")

    print(f"  {num_projects} projects, {total_tiles} tiles, commit {commit_short}")


if __name__ == "__main__":
    main()
