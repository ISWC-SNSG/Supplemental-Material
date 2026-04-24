from __future__ import annotations

import unittest

from tsrisk.uncertainty import calibrate_uncertainty_label


class UncertaintyCalibrationTest(unittest.TestCase):
    def test_no_path_becomes_insufficient(self) -> None:
        label, reason = calibrate_uncertainty_label(
            query_type='risk_identification',
            predicted_label='fully-supported',
            selected_path_event_ids=[],
            notes='No supporting path was returned.',
        )
        self.assertEqual(label, 'insufficient-evidence')
        self.assertIn('No selected path', reason)

    def test_counterfactual_with_inference_stays_partial(self) -> None:
        label, _ = calibrate_uncertainty_label(
            query_type='counterfactual_risk',
            predicted_label='fully-supported',
            selected_path_event_ids=['E1'],
            notes='The counterfactual conclusion is inferred from the observed escalation path.',
        )
        self.assertEqual(label, 'partially-supported')

    def test_direct_path_support_can_upgrade_to_full(self) -> None:
        label, _ = calibrate_uncertainty_label(
            query_type='policy_escalation_reasoning',
            predicted_label='partially-supported',
            selected_path_event_ids=['E1', 'E2'],
            notes='Direct path evidence supports the conclusion.',
        )
        self.assertEqual(label, 'fully-supported')


if __name__ == '__main__':
    unittest.main()
