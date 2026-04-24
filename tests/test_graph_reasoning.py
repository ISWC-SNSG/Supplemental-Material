from __future__ import annotations

import unittest

import networkx as nx

from tsrisk.graph_reasoning import enumerate_candidate_paths, score_path, select_local_subgraph


class GraphReasoningTest(unittest.TestCase):
    def test_singleton_paths_are_generated(self) -> None:
        g = nx.DiGraph()
        g.add_node('E1', case_id='C1', risk_dimension='technology_access_risk', is_key_event=True)
        paths = enumerate_candidate_paths(g, seed_event_ids=['E1'], include_singletons=True)
        self.assertTrue(any(p['event_ids'] == ['E1'] for p in paths))

    def test_case_restricted_subgraph_filters_other_cases(self) -> None:
        g = nx.DiGraph()
        g.add_node('E1', case_id='C1')
        g.add_node('E2', case_id='C1')
        g.add_node('X1', case_id='C2')
        g.add_edge('E1', 'E2', relation_confidence=0.9)
        g.add_edge('E1', 'X1', relation_confidence=0.9)
        subgraph, kept = select_local_subgraph(g, ['E1'], max_hops=1, min_relation_confidence=0.5, case_id='C1')
        self.assertEqual(set(kept), {'E1', 'E2'})

    def test_risk_identification_prefers_compact_singleton(self) -> None:
        g = nx.DiGraph()
        g.add_node('E1', case_id='C1', risk_dimension='technology_access_risk', is_key_event=True, is_turning_point=False, actor='BIS', target_entity='SMIC', event_title='SMIC listed', event_summary='', event_date='2020-12-22')
        g.add_node('E2', case_id='C1', risk_dimension='technology_access_risk', is_key_event=False, is_turning_point=False, actor='BIS', target_entity='SMIC', event_title='follow on', event_summary='', event_date='2022-10-07')
        g.add_edge('E1', 'E2', relation_type='impact_propagation', relation_confidence=0.9)
        query_info = {
            'query_text': 'What was the primary technology-access consequence of adding SMIC to the Entity List in December 2020?',
            'query_type': 'risk_identification',
            'risk_dimension': 'technology_access_risk',
            'target_actor': 'SMIC',
            'years': [2020],
            'query_terms': ['technology', 'access', 'smic', 'entity', 'list'],
        }
        singleton_score = score_path(g, {'event_ids': ['E1'], 'relation_ids': []}, query_info=query_info)
        chain_score = score_path(g, {'event_ids': ['E1', 'E2'], 'relation_ids': ['R1']}, query_info=query_info)
        self.assertGreater(singleton_score, chain_score)


if __name__ == '__main__':
    unittest.main()
