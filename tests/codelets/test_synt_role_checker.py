import pytest

from construction_finder import codelets


class TestSyntRoleChecker:
    @pytest.fixture
    def synt_role_checker(self, codelet_info, to_frame_matcher):
        slot_id = 3
        to_frame_matcher.frame.slots[slot_id].candidates.extend([[3], [1]])
        synt_role_checker_object = (
            codelets.SyntRoleChecker.from_slot_frame_matcher_and_temp_modifier(
                codelet_info, to_frame_matcher, slot_id, 42
            )
        )
        return synt_role_checker_object

    @pytest.fixture
    def gifts_synt_role_checker(self, codelet_info, wonderful_gifts_to_frame_matcher):
        slot_id = 3
        wonderful_gifts_to_frame_matcher.frame.slots[slot_id].candidates.extend(
            [[1], [3, 4, 5, 6, 7, 8], [10]]
        )
        synt_role_checker_object = (
            codelets.SyntRoleChecker.from_slot_frame_matcher_and_temp_modifier(
                codelet_info, wonderful_gifts_to_frame_matcher, slot_id, 42
            )
        )
        return synt_role_checker_object

    def test_from_slot_frame_matcher_and_temp_modifier(
        self, synt_role_checker, to_frame_matcher
    ):
        slot_id = 3
        assert isinstance(synt_role_checker, codelets.SyntRoleChecker)
        assert synt_role_checker.slot_id == slot_id
        assert synt_role_checker.frame_matcher.frame.slots[slot_id].candidates == [
            [3],
            [1],
        ]
        assert synt_role_checker.frame_matcher == to_frame_matcher
        assert synt_role_checker.urgency_level == 1
        assert synt_role_checker.temp_modifier == 42

    def test_run_no_new_codelets(self, synt_role_checker):
        output = synt_role_checker.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 0
        assert output.temp_modifier == 42
        assert synt_role_checker.frame_matcher.frame.slots[3].bond == [3]

    def test_run_with_new_codelets(self, gifts_synt_role_checker):
        output = gifts_synt_role_checker.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 0
        assert output.temp_modifier == 42
        assert gifts_synt_role_checker.frame_matcher.frame.slots[3].candidates == [
            [3, 4, 5, 6, 7, 8],
            [10],
        ]
        assert gifts_synt_role_checker.frame_matcher.frame.slots[3].bond == None

    def test_str(self, synt_role_checker):
        output = str(synt_role_checker)
        expected = "<SyntRoleChecker>: urgency_level=1, temp_modifier=42, slot_id=3"
        assert output == expected
