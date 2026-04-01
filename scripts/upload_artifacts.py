#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Download artifacts from a GitHub Actions run and upload them to the matching release.
# Copyright (C) 2026 Tiny Tapeout LTD
# Author: Uri Shaked

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from gh_utils import find_release_for_commit, gh, parse_run_url


def format_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class _NoRedirectHandler(urllib.request.HTTPErrorProcessor):
    def http_response(self, request, response):
        if response.code == 302:
            return response
        return super().http_response(request, response)

    https_response = http_response


def download_artifact(url, dest, token, total_size):
    # GitHub API returns a 302 to Azure Blob Storage; we must not forward
    # the Bearer token to the redirect target (it has its own auth in the URL).
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    opener = urllib.request.build_opener(_NoRedirectHandler)
    resp = opener.open(req)
    redirect_url = resp.headers["Location"]

    with urllib.request.urlopen(redirect_url) as resp, open(dest, "wb") as f:
        downloaded = 0
        while chunk := resp.read(1024 * 1024):
            f.write(chunk)
            downloaded += len(chunk)
            pct = downloaded * 100 // total_size if total_size else 0
            print(
                f"\r  {format_size(downloaded)} / {format_size(total_size)} ({pct}%)",
                end="",
                flush=True,
            )
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Upload artifacts from a GitHub Actions run to the matching release"
    )
    parser.add_argument("run_url", help="GitHub Actions run URL")
    args = parser.parse_args()

    owner, repo_name, run_id = parse_run_url(args.run_url)
    repo_slug = f"{owner}/{repo_name}"

    run_info = json.loads(gh(["api", f"repos/{repo_slug}/actions/runs/{run_id}"]))
    if run_info["name"] != "gds":
        print(
            f"Error: expected 'gds' workflow, got '{run_info['name']}'",
            file=sys.stderr,
        )
        sys.exit(1)
    head_sha = run_info["head_sha"]
    print(f"Run commit: {head_sha[:8]}")

    release = find_release_for_commit(owner, repo_name, head_sha)
    if not release:
        print("Error: no release found matching the run commit", file=sys.stderr)
        sys.exit(1)
    release_tag = release["tag_name"]
    print(f"Release: {release_tag}")

    artifacts = json.loads(
        gh(["api", f"repos/{repo_slug}/actions/runs/{run_id}/artifacts"])
    )["artifacts"]

    active = [a for a in artifacts if not a["expired"]]
    if not active:
        print("Error: no active (non-expired) artifacts found", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(active)} artifacts")

    token = gh(["auth", "token"])

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, artifact in enumerate(active, 1):
            name = artifact["name"]
            size = artifact["size_in_bytes"]
            zip_path = Path(tmpdir) / f"{name}.zip"

            print(f"\n[{i}/{len(active)}] Downloading {name} ({format_size(size)})...")
            download_artifact(
                f"https://api.github.com/repos/{repo_slug}/actions/artifacts/{artifact['id']}/zip",
                zip_path,
                token,
                size,
            )

            print(f"[{i}/{len(active)}] Uploading {name}.zip to release {release_tag}...")
            subprocess.run(
                [
                    "gh", "release", "upload", release_tag,
                    str(zip_path),
                    "-R", repo_slug,
                    "--clobber",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )

    run_url = f"https://github.com/{repo_slug}/actions/runs/{run_id}"
    notes = f"Commit: {head_sha}\nWorkflow run: {run_url}"
    subprocess.run(
        [
            "gh", "release", "edit", release_tag,
            "-R", repo_slug,
            "--notes", notes,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )

    print(f"\nDone! Uploaded {len(active)} artifacts to release {release_tag}")


if __name__ == "__main__":
    main()
