import pytest

from construction_finder import codelets


class TestDependencyMatcher:
    @pytest.fixture
    def dependency_matcher_resolution_on_dependency(
        self, codelet_info, to_frame_matcher
    ):
        slot_id = 4
        to_frame_matcher.frame.slots[slot_id].candidates.extend([[3], [1]])
        dependency_matcher_object = (
            codelets.DependencyMatcher.from_slot_frame_matcher_and_temp_modifier(
                codelet_info, to_frame_matcher, slot_id, 42
            )
        )
        return dependency_matcher_object

    @pytest.fixture
    def dependency_matcher_no_resolution(self, codelet_info, to_frame_matcher):
        slot_id = 1
        to_frame_matcher.frame.slots[slot_id].candidates.extend([[3], [1]])
        dependency_matcher_object = (
            codelets.DependencyMatcher.from_slot_frame_matcher_and_temp_modifier(
                codelet_info, to_frame_matcher, slot_id, 42
            )
        )
        return dependency_matcher_object

    def test_from_slot_frame_matcher_and_temp_modifier(
        self, dependency_matcher_resolution_on_dependency, to_frame_matcher
    ):
        assert isinstance(
            dependency_matcher_resolution_on_dependency, codelets.DependencyMatcher
        )
        assert (
            dependency_matcher_resolution_on_dependency.frame_matcher
            == to_frame_matcher
        )
        assert dependency_matcher_resolution_on_dependency.urgency_level == 1
        assert dependency_matcher_resolution_on_dependency.codelet_probability == 1
        assert dependency_matcher_resolution_on_dependency.slot_id == 4
        assert dependency_matcher_resolution_on_dependency.temp_modifier == 42

    def test_run_resolution_on_dependency(
        self, dependency_matcher_resolution_on_dependency
    ):
        output = dependency_matcher_resolution_on_dependency.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 0
        assert dependency_matcher_resolution_on_dependency.frame_matcher.frame.slots[
            4
        ].bond == [3]
        assert (
            dependency_matcher_resolution_on_dependency.frame_matcher.frame.slots[
                4
            ].form
            == "me"
        )
        assert output.temp_modifier == 42

    def test_run_no_resolution(self, dependency_matcher_no_resolution):
        output = dependency_matcher_no_resolution.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 1
        assert isinstance(output.new_codelets[0], codelets.SyntRoleChecker)
        assert output.new_codelets[0].urgency_level == 2
        assert output.new_codelets[0].codelet_probability == 1
        assert dependency_matcher_no_resolution.frame_matcher.frame.slots[
            1
        ].candidates == [[3], [1]]
        assert output.temp_modifier == 21

    def test_str(self, dependency_matcher_no_resolution):
        output = str(dependency_matcher_no_resolution)
        expected = "<DependencyMatcher>: urgency_level=1, temp_modifier=42, slot_id=1"
        assert output == expected
