# SPDX-License-Identifier: Apache-2.0
# This script updates the shuttle index for a given shuttle ID.
# Copyright (C) 2024 Tiny Tapeout LTD
# Author: Uri Shaked

import argparse
import json
import logging
import sys
import time
import urllib.parse
import urllib.request
from jsonschema import validate
from pathlib import Path

import yaml

SCANCHAIN_SHUTTLES = ["tt02", "tt03"]
# In legacy shuttles, the info.yaml files were committed after the fact, to a different path
LEGACY_SHUTTLES = ["tt02", "tt03", "tt03p5"]
# The following shuttles do not have a danger_level.yaml file:
NO_DANGER_LEVEL_SHUTTLES = ["tt02", "tt03", "tt03p5", "tt04", "tt05", "ttihp0p2"]

VALID_PINOUT_KEYS = [
    "ui[0]",
    "ui[1]",
    "ui[2]",
    "ui[3]",
    "ui[4]",
    "ui[5]",
    "ui[6]",
    "ui[7]",
    "uo[0]",
    "uo[1]",
    "uo[2]",
    "uo[3]",
    "uo[4]",
    "uo[5]",
    "uo[6]",
    "uo[7]",
    "uio[0]",
    "uio[1]",
    "uio[2]",
    "uio[3]",
    "uio[4]",
    "uio[5]",
    "uio[6]",
    "uio[7]",
    "ua[0]",
    "ua[1]",
    "ua[2]",
    "ua[3]",
    "ua[4]",
    "ua[5]",
]

SCANCHAIN_VALID_PINOUT_KEYS = [
    "io_in[0]",
    "io_in[1]",
    "io_in[2]",
    "io_in[3]",
    "io_in[4]",
    "io_in[5]",
    "io_in[6]",
    "io_in[7]",
    "io_out[0]",
    "io_out[1]",
    "io_out[2]",
    "io_out[3]",
    "io_out[4]",
    "io_out[5]",
    "io_out[6]",
    "io_out[7]",
]

parser = argparse.ArgumentParser(description="Update shuttle index")
parser.add_argument("shuttle_id", type=str, help="Shuttle ID")

args = parser.parse_args()


def normalize_pin_name(macro: str, name: str):
    if isinstance(name, int):
        return str(name)
    if isinstance(name, dict) or isinstance(name, list) or name is None:
        logging.warning(f"{macro}: invalid pin name {name}")
        return ""
    if name.lower() in ["-", "none", "unused", "not used"]:
        return ""
    return name


def convert_legacy_pinout(macro: str, is_mux: bool, project_info):
    pinout = {}
    inputs = project_info.get("inputs", [])
    outputs = project_info.get("outputs", [])
    bidirectional = project_info.get("bidirectional", [])
    if not isinstance(bidirectional, list):
        bidirectional = []
    input_name = "ui" if is_mux else "io_in"
    output_name = "uo" if is_mux else "io_out"
    for i in range(8):
        pinout[f"{input_name}[{i}]"] = (
            normalize_pin_name(macro, inputs[i]) if i < len(inputs) else ""
        )
    for i in range(8):
        pinout[f"{output_name}[{i}]"] = (
            normalize_pin_name(macro, outputs[i]) if i < len(outputs) else ""
        )
    if is_mux:
        for i in range(8):
            pinout[f"uio[{i}]"] = (
                normalize_pin_name(macro, bidirectional[i])
                if i < len(bidirectional)
                else ""
            )
    return pinout


def shuttle_index_url(repo: str, shuttle_id: str):
    url_map = {
        "tt02": "https://raw.githubusercontent.com/TinyTapeout/tinytapeout-02/tt02/project_info/index.json",
        "tt03": "https://raw.githubusercontent.com/TinyTapeout/tinytapeout-03/main/project_info/index.json",
        "tt03p5": "https://raw.githubusercontent.com/TinyTapeout/tinytapeout-03p5/main/project_info/mux_index.json",
    }
    default_url = f"https://tinytapeout.github.io/{repo}/shuttle_index.json"

    return url_map.get(shuttle_id, default_url)


root = Path(__file__).resolve().parents[1]
with open(root / "index" / "index.json") as f:
    shuttle_index = json.load(f)

shuttle = next(filter(lambda x: x["id"] == args.shuttle_id, shuttle_index["shuttles"]))
if not shuttle:
    print(f"Shuttle {args.shuttle_id} not found")
    sys.exit(1)

output_path = root / "index" / f"{shuttle['id']}.json"

# extract owner/repo from repo url, using a url parser module:
[owner, repo] = urllib.parse.urlparse(shuttle["repo"]).path[1:].split("/")
with urllib.request.urlopen(shuttle_index_url(repo, args.shuttle_id)) as f:
    index_json = json.load(f)

branch = "main" if args.shuttle_id != "tt02" else "tt02"
projects_dir = "projects" if args.shuttle_id not in LEGACY_SHUTTLES else "project_info"
cache_buster = int(time.time())
danger_level_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{projects_dir}/danger_level.yaml?token={cache_buster}"
if args.shuttle_id not in NO_DANGER_LEVEL_SHUTTLES:
    with urllib.request.urlopen(danger_level_url) as f:
        danger_level_info = yaml.safe_load(f) or {}
else:
    danger_level_info = {}

projects = []
macro_addresses = {}
project_index = []
if "projects" in index_json:
    project_index = zip(
        map(lambda p: p["address"], index_json["projects"]), index_json["projects"]
    )
elif "mux" in index_json:
    project_index = index_json["mux"].items()
elif "scanchain" in index_json:
    project_index = index_json["scanchain"].items()
for address, project_entry in project_index:
    macro = project_entry["macro"]
    if macro in macro_addresses:
        logging.warning(
            f"Duplicate macro {macro} at {address} (first at {macro_addresses[macro]})"
        )
        continue
    macro_addresses[macro] = address
    logging.info(f"Updating {macro} at {address}...")
    yaml_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{projects_dir}/{macro}/info.yaml?token={cache_buster}"
    with urllib.request.urlopen(yaml_url) as f:
        project_yaml = yaml.safe_load(f)
    version = project_yaml.get("yaml_version", 1)
    project_info = (
        project_yaml["documentation"]
        if "documentation" in project_yaml
        else project_yaml["project"]
    )
    pinout = project_yaml.get("pinout", None)
    valid_pinout_keys = VALID_PINOUT_KEYS
    if not pinout:
        is_mux = args.shuttle_id not in SCANCHAIN_SHUTTLES
        if not is_mux:
            valid_pinout_keys = SCANCHAIN_VALID_PINOUT_KEYS
        pinout = convert_legacy_pinout(macro, is_mux, project_info)

    # Report and remove invalid keys from pinout
    invalid_keys = set(pinout.keys()) - set(valid_pinout_keys)
    if invalid_keys:
        logging.warning(f"{macro}: invalid pinout keys: {', '.join(invalid_keys)}")
    pinout = {k: v for k, v in pinout.items() if k in valid_pinout_keys}

    project_data = {
        "macro": macro,
        "address": int(address),
        "title": project_info["title"],
        "author": project_info["author"],
        "description": project_info["description"],
        "clock_hz": (
            project_info["clock_hz"]
            if isinstance(project_info.get("clock_hz", ""), int)
            else 0
        ),
        "tiles": project_entry.get("tiles", "1x1"),
        "analog_pins": project_entry.get("analog_pins", []),
        "repo": project_entry["repo"],
        "commit": project_entry.get("commit", ""),
        "pinout": pinout,
    }

    if macro in danger_level_info:
        project_danger_level = danger_level_info[macro]
        level_value = project_danger_level["level"]
        assert level_value in ['safe', 'medium', 'high', 'unknown']
        project_data["danger_level"] = level_value
        if "reason" in project_danger_level:
            project_data["danger_reason"] = project_danger_level["reason"]

    projects.append(project_data)

projects.sort(key=lambda x: x["macro"])

result = {
    "version": 3,
    "id": shuttle["id"],
    "name": shuttle["name"],
    "repo": shuttle["repo"],
    "commit": index_json["commit"],
    "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "projects": projects,
}

with open(root / "schemas" / "shuttle.schema.json") as f:
    schema = json.load(f)

validate(result, schema)

# Only write output if there's been a change:
if Path(output_path).exists():
    with open(output_path) as f:
        old_content = json.load(f)
    old_content["updated"] = result["updated"]
    if old_content == result:
        logging.info(f"No changes detected, skipping write to {output_path}")
        sys.exit(0)

logging.info(f"Writing {output_path}")
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)
