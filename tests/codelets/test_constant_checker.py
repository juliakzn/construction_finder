import pytest

from construction_finder import codelets


class TestConstantChecker:
    @pytest.fixture
    def to_constant_checker(self, codelet_info, to_frame_matcher):
        slot_id = 1
        to_frame_matcher.frame.slots[slot_id].candidates.extend([[2]])
        constant_checker_object = (
            codelets.ConstantChecker.from_slot_frame_matcher_and_temp_modifier(
                codelet_info, to_frame_matcher, slot_id, 42
            )
        )
        return constant_checker_object

    @pytest.fixture
    def some_constant_checker(
        self, codelet_info, wonderful_gifts_distributive_frame_matcher
    ):
        slot_id = 0
        wonderful_gifts_distributive_frame_matcher.frame.slots[
            slot_id
        ].candidates.extend([[3], [10]])
        constant_checker_object = (
            codelets.ConstantChecker.from_slot_frame_matcher_and_temp_modifier(
                codelet_info,
                wonderful_gifts_distributive_frame_matcher,
                slot_id,
                42,
            )
        )
        return constant_checker_object

    def test_from_slot_frame_matcher_and_temp_modifier(
        self, to_constant_checker, to_frame_matcher
    ):
        slot_id = 1
        assert isinstance(to_constant_checker, codelets.ConstantChecker)
        assert to_constant_checker.slot_id == slot_id
        assert to_constant_checker.frame_matcher.frame.slots[slot_id].candidates == [
            [2]
        ]
        assert to_constant_checker.frame_matcher == to_frame_matcher
        assert to_constant_checker.urgency_level == 1
        assert to_constant_checker.temp_modifier == 42

    def test_run_to(self, to_constant_checker):
        output = to_constant_checker.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 0
        assert output.temp_modifier == 42
        assert to_constant_checker.frame_matcher.frame.slots[
            to_constant_checker.slot_id
        ].bond == [2]

    def test_run_some(self, some_constant_checker):
        output = some_constant_checker.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 0
        assert output.temp_modifier == 42
        assert some_constant_checker.frame_matcher.frame.slots[
            some_constant_checker.slot_id
        ].bond == [3]

    def test_creating_frame_finalizer(self, to_constant_checker):
        slot_list = [0, 2, 3, 4]
        candidate_list = [[0], ["PRODROP"], [1], [3]]
        for slot, candidate in zip(slot_list, candidate_list):
            to_constant_checker.frame_matcher.frame.slots[slot].add_candidate(candidate)
            to_constant_checker.frame_matcher.set_bond(
                slot, [candidate], to_constant_checker
            )

        output = to_constant_checker.run()
        assert len(output.new_codelets) == 1
        assert isinstance(output.new_codelets[0], codelets.FrameFinalizer)

    def test_str(self, to_constant_checker):
        output = str(to_constant_checker)
        expected = f"<ConstantChecker>: urgency_level=1, temp_modifier=42"
        assert output == expected
