import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('rea_summary', Path(__file__).resolve().parents[1] / 'tools/rea-summary.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReaSummaryTests(unittest.TestCase):
    def test_partial_inventory_is_never_reported_complete(self):
        evidence = {'evidence_id': 'ev_fixture', 'limitations': ['no relationships'], 'normalized_result': {'source_selection': {'unselected_files': 10}}}
        result = module.summarize({'error': 'failed', 'message': 'ps unavailable', 'code': 'capability_unavailable', 'details': {'partial_observation': evidence}})
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['evidence_id'], 'ev_fixture')
        self.assertEqual(result['source_selection']['unselected_files'], 10)

    def test_known_evidence_keeps_its_limits(self):
        result = module.summarize({'evidence_id': 'ev_fixture', 'confidence': 'derived', 'limitations': ['static only']})
        self.assertEqual(result['status'], 'evidence-returned')
        self.assertEqual(result['limitations'], ['static only'])

    def test_blocked_without_evidence_is_not_success(self):
        self.assertEqual(module.summarize({'error': 'no provider'})['status'], 'blocked')

    def test_unknown_envelope_is_rejected(self):
        for value in [[], {}, {'success': True}]:
            with self.assertRaises(ValueError):
                module.summarize(value)
