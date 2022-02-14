from construction_finder import codelets, coderack


def test_spin_results():
    spin_result = coderack.SpinResult(
        temp_modifier=100,
        workspace_modifiers=["WORKSPACE MODIFIER 1", "WORKSPACE MODIFIER 2"],
        new_active_frames=[("append", "NEW ACTIVE FRAME")],
    )
    assert spin_result.temp_modifier == 100
    assert spin_result.workspace_modifiers == [
        "WORKSPACE MODIFIER 1",
        "WORKSPACE MODIFIER 2",
    ]
    assert spin_result.new_active_frames == [("append", "NEW ACTIVE FRAME")]


class SpecialTestCodelet(codelets.Codelet):
    def run(self):
        return codelets.CodeletResults(
            [], 42, ["WORKSPACE MODIFIER 1", "WORKSPACE MODIFIER 2"]
        )


class TestCoderack:
    coderack_exemplar = coderack.CodeRack()
    test_codelet1 = SpecialTestCodelet(urgency_level=2, codelet_probability=0.6)
    test_codelet2 = SpecialTestCodelet(urgency_level=6, codelet_probability=0.7)
    coderack_exemplar.add_codelet(test_codelet1)
    coderack_exemplar.add_codelet(test_codelet2)

    def test_urgency_levels(self):
        assert self.coderack_exemplar.urgency_levels == [1, 2, 3, 4, 5]
        coderack_exemplar2 = coderack.CodeRack(urgency_levels=[1, 2, 3])
        assert coderack_exemplar2.urgency_levels == [1, 2, 3]

    def test_add_codelet(self):
        assert self.coderack_exemplar.urgency_bins[2] == [self.test_codelet1]
        assert self.coderack_exemplar.urgency_bins[5] == [self.test_codelet2]

    def test_assess_urgency(self):
        urgency = self.coderack_exemplar.assess_urgency()
        assert urgency == [2, 2, 5, 5, 5, 5, 5]

    def test_contains(self):
        test_codelet3 = SpecialTestCodelet(urgency_level=2, codelet_probability=0.8)
        assert self.test_codelet1 in self.coderack_exemplar
        assert self.test_codelet2 in self.coderack_exemplar
        assert test_codelet3 not in self.coderack_exemplar

    def test_spin_codelet(self):
        spinned_codelet = self.coderack_exemplar.spin_codelet()
        assert spinned_codelet.temp_modifier == 42
        assert spinned_codelet.workspace_modifiers == [
            "WORKSPACE MODIFIER 1",
            "WORKSPACE MODIFIER 2",
        ]
