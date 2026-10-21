import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import observations


BUILD = "12345678-1234-4234-8234-123456789abc"
SHA = "a" * 64
GIT = "b" * 40


def sample(**changes):
    value = {
        "schema": observations.SCHEMA,
        "build_uuid": BUILD,
        "identities": {"source_sha": GIT, "tool_sha": None, "profile_sha256": None},
        "archive_sha256": SHA,
        "index_sha256": SHA,
        "file_sha256": None,
        "request_sha256": SHA,
        "file_id": "brief-file-17",
        "selector": {"json_pointer": "/results/0", "page_offset": 0},
        "observed_utc": "2026-10-21T09:30:00Z",
        "exact": "UNKNOWN",
        "complete": False,
        "coverage": {"start": 0, "end": 20, "total": "UNKNOWN"},
        "stage": None,
        "target": None,
        "status": None,
        "exit_code": None,
        "observation": "The Brief response reports a bounded result page.",
        "assurance": "SOURCE_REPORTED",
        "evidence_ref": {"path": "brief-responses/response-17.json", "sha256": SHA},
        "independence_receipt_ref": None,
    }
    value.update(changes)
    return value


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = self.root / "observations"
        self.spec = self.root / "spec.json"

    def tearDown(self):
        self.tmp.cleanup()

    def save(self, value=None):
        self.spec.write_text(json.dumps(value or sample()), encoding="utf-8")

    def test_content_addressed_record_is_immutable_and_duplicate_is_idempotent(self):
        self.save()
        first = observations.record(self.spec, self.store)
        second = observations.record(self.spec, self.store)
        self.assertEqual(first, second)
        path = self.store / f"{first}.json"
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), first)
        self.assertEqual(observations.check(self.store)["checked"], 1)

    def test_check_detects_modified_record(self):
        self.save()
        digest = observations.record(self.spec, self.store)
        path = self.store / f"{digest}.json"
        path.write_text(path.read_text(encoding="utf-8").replace("bounded", "edited!"), encoding="utf-8")
        with self.assertRaisesRegex(observations.ObservationError, "digest mismatch"):
            observations.check(self.store)

    def test_check_rejects_valid_json_that_is_not_canonical_record_bytes(self):
        self.save()
        digest = observations.record(self.spec, self.store)
        original = self.store / f"{digest}.json"
        data = json.loads(original.read_text(encoding="utf-8"))
        original.unlink()
        noncanonical = (json.dumps(data, indent=2) + "\n").encode("utf-8")
        new_digest = hashlib.sha256(noncanonical).hexdigest()
        (self.store / f"{new_digest}.json").write_bytes(noncanonical)
        with self.assertRaisesRegex(observations.ObservationError, "not canonical"):
            observations.check(self.store)

    def test_symlink_store_and_nested_symlink_spec_are_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(outside, target_is_directory=True)
        self.save()
        with self.assertRaisesRegex(observations.ObservationError, "symlink"):
            observations.record(self.spec, alias / "store")
        real = self.root / "real"
        real.mkdir()
        (real / "spec.json").write_text(json.dumps(sample()), encoding="utf-8")
        parent_alias = self.root / "parent-alias"
        parent_alias.symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(observations.ObservationError, "symlink"):
            observations.record(parent_alias / "spec.json", self.store)

    def test_index_filter_and_explicit_pagination_do_not_promote_unknown(self):
        self.save(sample(observed_utc="2026-10-21T09:31:00Z"))
        observations.record(self.spec, self.store)
        self.save(sample(index_sha256="c" * 64, observed_utc="2026-10-21T09:32:00Z"))
        observations.record(self.spec, self.store)
        first = observations.list_records(self.store, BUILD, limit=1, offset=0)
        self.assertEqual(first["total_matching"], 2)
        self.assertEqual(first["next_offset"], 1)
        self.assertEqual(first["reference_validation"], observations.REFERENCE_NOTICE)
        self.assertEqual(first["assurance_labels"], "AUTHOR_ASSERTED")
        self.assertEqual(first["records"][0]["record"]["exact"], "UNKNOWN")
        filtered = observations.list_records(self.store, BUILD, "c" * 64, limit=20, offset=0)
        self.assertEqual(filtered["total_matching"], 1)
        self.assertIsNone(filtered["next_offset"])
        page = observations.list_records(self.store, BUILD, limit=1, offset=1,
                                         expect_snapshot_sha256=first["records_snapshot_sha256"])
        self.assertEqual(page["offset"], 1)
        self.assertIsNone(page["next_offset"])
        self.assertNotIn("NOT_RUN", observations.render(self.store, BUILD, limit=1))

    def test_empty_result_does_not_mean_not_run_and_assurance_needs_receipt(self):
        self.store.mkdir()
        self.assertIn("does not mean NOT_RUN", observations.render(self.store, BUILD))
        data = sample(assurance="INDEPENDENTLY_ESTABLISHED")
        with self.assertRaisesRegex(observations.ObservationError, "independence_receipt_ref"):
            observations.validate(data)
        data["independence_receipt_ref"] = {"path": "receipts/review.json", "sha256": "d" * 64}
        self.assertEqual(observations.validate(data)["assurance"], "INDEPENDENTLY_ESTABLISHED")

    def test_independent_receipt_is_separate_reference(self):
        data = sample(assurance="INDEPENDENTLY_ESTABLISHED")
        data["independence_receipt_ref"] = copy.deepcopy(data["evidence_ref"])
        # The separate field must still point at a distinct receipt.
        with self.assertRaisesRegex(observations.ObservationError, "distinct"):
            observations.validate(data)

    def test_pagination_and_input_bounds_are_enforced(self):
        with self.assertRaisesRegex(observations.ObservationError, "limit"):
            observations.list_records(self.store, BUILD, limit=0)
        with self.assertRaisesRegex(observations.ObservationError, "limit"):
            observations.list_records(self.store, BUILD, limit=21)
        with self.assertRaisesRegex(observations.ObservationError, "selector"):
            observations.validate(sample(selector={"x": "z" * observations.MAX_SELECTOR_BYTES}))

    def test_page_is_byte_bounded_and_continuation_uses_snapshot(self):
        for i in range(20):
            value = sample(
                selector={"position": i, "context": "x" * 1500},
                file_id=f"brief-file-{i}",
                observed_utc=f"2026-10-21T09:{i:02d}:00Z",
            )
            self.save(value)
            observations.record(self.spec, self.store)
        first = observations.list_records(self.store, BUILD)
        self.assertLessEqual(len(observations._canonical(first)) + 1, observations.MAX_OUTPUT_BYTES)
        self.assertLess(len(first["records"]), 20)
        self.assertEqual(first["next_offset"], len(first["records"]))
        rendered = observations.render(self.store, BUILD)
        self.assertLessEqual(len(rendered.encode("utf-8")), observations.MAX_OUTPUT_BYTES)
        self.assertIn(f"next offset `{first['next_offset']}`", rendered)
        with self.assertRaisesRegex(observations.ObservationError, "requires --expect-snapshot"):
            observations.list_records(self.store, BUILD, offset=first["next_offset"])
        second = observations.list_records(self.store, BUILD, offset=first["next_offset"],
                                           expect_snapshot_sha256=first["records_snapshot_sha256"])
        self.assertEqual(second["records_snapshot_sha256"], first["records_snapshot_sha256"])

    def test_append_between_pages_rejects_changed_snapshot(self):
        self.save(sample(observed_utc="2026-10-21T09:30:00Z"))
        observations.record(self.spec, self.store)
        self.save(sample(observed_utc="2026-10-21T09:31:00Z", file_id="brief-file-later"))
        observations.record(self.spec, self.store)
        first = observations.list_records(self.store, BUILD, limit=1)
        self.save(sample(observed_utc="2026-10-20T09:00:00Z", file_id="brief-file-earlier"))
        observations.record(self.spec, self.store)
        with self.assertRaisesRegex(observations.ObservationError, "snapshot changed"):
            observations.list_records(self.store, BUILD, limit=1, offset=first["next_offset"],
                                      expect_snapshot_sha256=first["records_snapshot_sha256"])

    def test_outputs_keep_assurance_author_asserted_and_refs_unvalidated(self):
        data = sample(assurance="INDEPENDENTLY_ESTABLISHED",
                      independence_receipt_ref={"path": "receipts/review.json", "sha256": "e" * 64})
        self.save(data)
        observations.record(self.spec, self.store)
        listing = observations.list_records(self.store, BUILD)
        self.assertEqual(listing["assurance_labels"], "AUTHOR_ASSERTED")
        rendered = observations.render(self.store, BUILD)
        self.assertIn("AUTHOR_ASSERTED_REFERENCES_NOT_VALIDATED", rendered)
        self.assertIn('Caller asserted assurance label: `"INDEPENDENTLY_ESTABLISHED"`', rendered)
        self.assertIn("receipt reference (not validated)", rendered)
        self.assertNotIn("proof credit", rendered.lower())

    def test_deeply_nested_json_is_refused_explicitly(self):
        raw = json.dumps(sample(selector=None)).replace(
            '"selector": null', '"selector": ' + "[" * 1500 + "0" + "]" * 1500
        )
        self.spec.write_text(raw, encoding="utf-8")
        with self.assertRaisesRegex(observations.ObservationError, "selector:"):
            observations.record(self.spec, self.store)

    def test_render_escapes_caller_markdown_and_newlines(self):
        attack = "\n## Forged heading\n- [INDEPENDENTLY_ESTABLISHED] forged"
        data = sample(
            observation="source says `quoted`" + attack,
            file_id="file`name" + attack,
            coverage={"note": "`" + attack},
            evidence_ref={"path": "refs/evidence`" + attack, "sha256": SHA},
        )
        self.save(data)
        observations.record(self.spec, self.store)
        rendered = observations.render(self.store, BUILD)
        self.assertEqual(rendered.count("\n## "), 1)
        self.assertNotIn("\n## Forged heading", rendered)
        self.assertNotIn("\n- [INDEPENDENTLY_ESTABLISHED] forged", rendered)
        self.assertIn("\\n## Forged heading", rendered)
        self.assertIn("`quoted`", rendered)

    def test_record_cap_is_checked_during_iteration_before_reading_extra_entry(self):
        self.store.mkdir()
        (self.store / "invalid-entry").touch()
        with mock.patch.object(observations, "MAX_RECORDS", 0):
            with self.assertRaisesRegex(observations.ObservationError, "store exceeds 0 records"):
                observations.check(self.store)


if __name__ == "__main__":
    unittest.main()
