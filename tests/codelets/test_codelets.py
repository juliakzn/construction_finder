import pytest

from construction_finder import codelets


@pytest.fixture
def codelet_results_instance(codelet):
    return codelets.CodeletResults(
        new_codelets=[codelet],
        temp_modifier=42,
        workspace_modifiers=["WORKSPACE_MODIFIERS"],
        new_active_frames=["NEW_ACTIVE_FRAMES"],
    )


class TestCodeletResults:
    def test_init(self, codelet, codelet_results_instance):
        assert codelet_results_instance.new_codelets == [codelet]
        assert codelet_results_instance.temp_modifier == 21
        assert codelet_results_instance.new_codelets[0].temp_modifier == 21
        assert codelet_results_instance.workspace_modifiers == ["WORKSPACE_MODIFIERS"]
        assert codelet_results_instance.new_active_frames == ["NEW_ACTIVE_FRAMES"]


class TestCodelet:
    codelet = codelets.Codelet(2, 0.42)

    def test_init(self):
        assert self.codelet.codelet_type == "Codelet"
        assert self.codelet.urgency_level == 2
        assert self.codelet.codelet_probability == 0.42
        assert self.codelet.temp_modifier is None

    def test_run(self):
        assert hasattr(self.codelet, "run")

    def test_str(self):
        assert str(self.codelet) == "<Codelet>: urgency_level=2, temp_modifier=None"
