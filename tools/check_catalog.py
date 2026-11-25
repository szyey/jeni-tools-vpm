"""Verify this repository's VPM catalog and release artifacts."""

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import urlopen
import zipfile


ROOT = Path(__file__).resolve().parent.parent
RELEASES = "https://github.com/szyey/jeni-tools-vpm/releases/download"
NUMBER = r"(?:0|[1-9][0-9]*)"
PRERELEASE = rf"(?:{NUMBER}|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
SEMVER = re.compile(
    rf"{NUMBER}\.{NUMBER}\.{NUMBER}"
    rf"(?:-{PRERELEASE}(?:\.{PRERELEASE})*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)


def tag_for(key):
    name, version = key
    return f"{name}-{version}"


def release_fields(entry):
    return {field: entry[field] for field in ("name", "version", "url", "zipSHA256")}


def catalog_entries(index):
    entries = {}
    for name, package in index["packages"].items():
        if not re.fullmatch(r"com\.jenitool\.[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"Invalid package ID: {name}")
        if not package["versions"]:
            raise ValueError(f"No versions for {name}")
        for version, entry in package["versions"].items():
            key = name, version
            if not SEMVER.fullmatch(version):
                raise ValueError(f"Invalid version: {tag_for(key)}")
            if (entry["name"], entry["version"]) != key:
                raise ValueError(f"Catalog key differs from its entry: {tag_for(key)}")
            tag = tag_for(key)
            if entry["url"] != f"{RELEASES}/{tag}/{tag}.zip":
                raise ValueError(f"Unexpected release URL: {tag}")
            if not re.fullmatch(r"[0-9a-f]{64}", entry["zipSHA256"]):
                raise ValueError(f"Invalid SHA-256: {tag}")
            entries[key] = entry
    if not entries:
        raise ValueError("Catalog contains no versions")
    return entries


def verify_manifest(entries, manifest):
    remaining = {key: release_fields(entry) for key, entry in entries.items()}
    for row in manifest["packages"]:
        key = row["name"], row["version"]
        if remaining.pop(key, None) != release_fields(row):
            raise ValueError(f"Missing, duplicate, or mismatched manifest row: {tag_for(key)}")
    if remaining:
        raise ValueError("Manifest omits: " + ", ".join(map(tag_for, remaining)))


def read_at(ref, path):
    return json.loads(subprocess.check_output(
        ["git", "show", "--end-of-options", f"{ref}:{path}"],
        cwd=ROOT, stderr=subprocess.DEVNULL,
    ))


def verify_history(entries, base):
    previous = catalog_entries(read_at(base, "index.json"))
    for key, old in previous.items():
        if entries.get(key) != old:
            raise ValueError(f"Published version removed or changed: {tag_for(key)}")
    for key in entries.keys() - previous.keys():
        tag = tag_for(key)
        ref = f"refs/tags/{tag}"
        try:
            tagged = read_at(ref, "index.json")["packages"][key[0]]["versions"][key[1]]
            manifest = read_at(ref, "release-manifest.json")
        except (subprocess.CalledProcessError, KeyError) as exc:
            raise ValueError(f"Release tag {tag} does not contain its catalog and manifest") from exc
        if tagged != entries[key]:
            raise ValueError(f"Release tag {tag} has a different catalog entry")
        rows = [release_fields(row) for row in manifest["packages"]
                if (row["name"], row["version"]) == key]
        if rows != [release_fields(tagged)]:
            raise ValueError(f"Release tag {tag} has a different manifest entry")


def verify_archive(entry, contents):
    label = tag_for((entry["name"], entry["version"]))
    if hashlib.sha256(contents).hexdigest() != entry["zipSHA256"]:
        raise ValueError(f"SHA-256 mismatch: {label}")
    with zipfile.ZipFile(io.BytesIO(contents)) as archive:
        if archive.namelist().count("package.json") != 1:
            raise ValueError(f"Expected one root package.json: {label}")
        package = json.loads(archive.read("package.json"))
        for field in ("name", "version", "unity", "vpmDependencies"):
            default = {} if field == "vpmDependencies" else None
            if package.get(field, default) != entry.get(field, default):
                raise ValueError(f"ZIP package.json differs on {field}: {label}")
        if bad_member := archive.testzip():
            raise ValueError(f"Corrupt ZIP member {bad_member}: {label}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Compare published versions and validate new tags against this Git ref")
    parser.add_argument("--zip-dir", type=Path, help="Prefer ZIPs from this directory over GitHub downloads")
    args = parser.parse_args()
    try:
        if args.zip_dir is not None and not args.zip_dir.is_dir():
            raise ValueError(f"ZIP directory was not found: {args.zip_dir}")
        entries = catalog_entries(json.loads((ROOT / "index.json").read_text(encoding="utf-8")))
        verify_manifest(entries, json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8")))
        if args.base:
            verify_history(entries, args.base)
        for key, entry in entries.items():
            tag = tag_for(key)
            local = args.zip_dir / f"{tag}.zip" if args.zip_dir is not None else None
            if local is not None and local.is_file():
                contents = local.read_bytes()
            else:
                try:
                    with urlopen(entry["url"], timeout=30) as response:
                        contents = response.read()
                except OSError as exc:
                    raise ValueError(f"Could not fetch {tag}: {exc}") from exc
            verify_archive(entry, contents)
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(f"Catalog check failed: {exc}", file=sys.stderr)
        return 1
    print(f"Verified {len(entries)} releases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
