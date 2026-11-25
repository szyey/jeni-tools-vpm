import hashlib
import io
import json
import unittest
from unittest.mock import patch
import zipfile

from check_catalog import (
    RELEASES,
    catalog_entries,
    release_fields,
    verify_archive,
    verify_history,
    verify_manifest,
)


NAME = "com.jenitool.example"


def release(version="1.0.0"):
    package = {"name": NAME, "version": version, "unity": "2022.3", "vpmDependencies": {}}
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("package.json", json.dumps(package))
    tag = f"{NAME}-{version}"
    data = archive.getvalue()
    entry = dict(package, url=f"{RELEASES}/{tag}/{tag}.zip",
                 zipSHA256=hashlib.sha256(data).hexdigest())
    return entry, data


def index(*entries):
    return {"packages": {NAME: {"versions": {entry["version"]: entry for entry in entries}}}}


def manifest(*entries):
    return {"packages": [release_fields(entry) for entry in entries]}


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.entry, self.data = release()
        self.entries = catalog_entries(index(self.entry))

    def test_consistent_release(self):
        verify_manifest(self.entries, manifest(self.entry))
        verify_archive(self.entry, self.data)

    def test_catalog_rejects_unexpected_download_url(self):
        with self.assertRaisesRegex(ValueError, "Unexpected release URL"):
            catalog_entries(index(dict(self.entry, url="https://example.invalid/artifact.zip")))

    def test_manifest_rejects_duplicate_missing_or_mismatched_rows(self):
        for candidate in (manifest(self.entry, self.entry), manifest(),
                          manifest(dict(self.entry, zipSHA256="0" * 64))):
            with self.subTest(candidate=candidate), self.assertRaisesRegex(ValueError, "manifest row|Manifest omits"):
                verify_manifest(self.entries, candidate)

    def test_archive_rejects_wrong_digest(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verify_archive(self.entry, self.data + b"changed")

    def test_archive_rejects_different_dependencies_even_with_right_hash(self):
        with self.assertRaisesRegex(ValueError, "differs on vpmDependencies"):
            verify_archive(dict(self.entry, vpmDependencies={"nadena.dev.ndmf": "1.15.1"}), self.data)

    @patch("check_catalog.read_at")
    def test_history_only_checks_tags_for_new_versions(self, read_at):
        new, _ = release("1.0.1")
        read_at.side_effect = [index(self.entry), index(new), manifest(new)]
        verify_history(catalog_entries(index(self.entry, new)), "base")
        self.assertEqual(read_at.call_count, 3)

    @patch("check_catalog.read_at")
    def test_history_rejects_removed_or_modified_release(self, read_at):
        read_at.return_value = index(self.entry)
        for changed in ({}, catalog_entries(index(dict(self.entry, unity="6000.0")))):
            with self.subTest(changed=changed), self.assertRaisesRegex(ValueError, "Published version removed or changed"):
                verify_history(changed, "base")

    @patch("check_catalog.read_at")
    def test_history_rejects_tag_without_the_new_release(self, read_at):
        new, _ = release("1.0.1")
        read_at.side_effect = [index(self.entry), index(self.entry)]
        with self.assertRaisesRegex(ValueError, "does not contain its catalog and manifest"):
            verify_history(catalog_entries(index(self.entry, new)), "base")

    @patch("check_catalog.read_at")
    def test_history_rejects_tag_with_different_manifest(self, read_at):
        new, _ = release("1.0.1")
        read_at.side_effect = [index(self.entry), index(new), manifest(dict(new, zipSHA256="0" * 64))]
        with self.assertRaisesRegex(ValueError, "different manifest entry"):
            verify_history(catalog_entries(index(self.entry, new)), "base")
