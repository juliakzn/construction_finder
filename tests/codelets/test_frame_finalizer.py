import pytest

from construction_finder import codelets


class TestFrameFinalizer:
    @pytest.fixture
    def some_frame_finalizer(
        self, codelet_info, wonderful_gifts_distributive_frame_matcher
    ):
        slot_bonds = {0: [3], 1: [4], 2: [5, 6, 7, 8]}
        for slot_id, candidate in slot_bonds.items():
            wonderful_gifts_distributive_frame_matcher.frame.slots[
                slot_id
            ].candidates.extend([candidate])
            wonderful_gifts_distributive_frame_matcher.frame.set_bond(
                slot_id, candidate
            )
        frame_finalizer_object = (
            codelets.FrameFinalizer.from_frame_matcher_and_temp_modifier(
                codelet_info, wonderful_gifts_distributive_frame_matcher, 42
            )
        )
        return frame_finalizer_object

    @pytest.fixture
    def everyone_frame_finalizer(
        self, codelet_info, wonderful_gifts_distributive_frame_matcher
    ):
        slot_bonds = {0: [10], 1: [4], 2: [5, 6, 7, 8]}
        for slot_id, candidate in slot_bonds.items():
            wonderful_gifts_distributive_frame_matcher.frame.slots[
                slot_id
            ].candidates.extend([candidate])
            wonderful_gifts_distributive_frame_matcher.frame.set_bond(
                slot_id, candidate
            )
        frame_finalizer_object = (
            codelets.FrameFinalizer.from_frame_matcher_and_temp_modifier(
                codelet_info, wonderful_gifts_distributive_frame_matcher, 42
            )
        )
        return frame_finalizer_object

    def test_from_frame_matcher_and_temp_modifier(
        self, some_frame_finalizer, wonderful_gifts_distributive_frame_matcher
    ):
        assert (
            some_frame_finalizer.frame_matcher
            == wonderful_gifts_distributive_frame_matcher
        )
        assert some_frame_finalizer.urgency_level == 1
        assert some_frame_finalizer.temp_modifier == 42

    def test_run(
        self, some_frame_finalizer, wonderful_gifts_distributive_frame_matcher
    ):
        output = some_frame_finalizer.run()
        assert output.new_active_frames == []

    def test_run(
        self, everyone_frame_finalizer, wonderful_gifts_distributive_frame_matcher
    ):
        output = everyone_frame_finalizer.run()
        assert output.new_active_frames == [
            ("remove", wonderful_gifts_distributive_frame_matcher.frame)
        ]
