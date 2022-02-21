import pytest

from construction_finder import codelets


class TestSingleCandidateChecker:
    @pytest.fixture
    def single_candidate_checker(self, codelet_info, dative_frame_matcher):
        slot_bonds = {0: [1], 1: ["PRODROP"], 2: [3], 3: [2]}
        for slot_id, candidate in slot_bonds.items():
            dative_frame_matcher.frame.slots[slot_id].candidates.extend([candidate])
            dative_frame_matcher.frame.set_bond(slot_id, candidate)
        single_candidate_checker_object = (
            codelets.FrameFinalizer.from_frame_matcher_and_temp_modifier(
                codelet_info, dative_frame_matcher, 42
            )
        )
        candidates = {3: [2]}
        for slot_id, candidate in candidates.items():
            dative_frame_matcher.frame.slots[slot_id].candidates.extend([candidate])

        return single_candidate_checker_object

    def test_from_frame_matcher_and_temp_modifier(
        self, single_candidate_checker, dative_frame_matcher
    ):
        assert single_candidate_checker.frame_matcher == dative_frame_matcher
        assert single_candidate_checker.urgency_level == 1
        assert single_candidate_checker.temp_modifier == 42

    def test_run(self, single_candidate_checker, dative_frame_matcher):
        output = single_candidate_checker.run()
        assert output.new_active_frames == []
        assert dative_frame_matcher.frame.slots[3].bond == [2]
        assert output.temp_modifier == 42
