from construction_finder import frame


class TestFrameSlot:
    slot_dict = {
        "variable_or_constant": "variable",
        "synt_type": "VERB",
        "roles": {"ROOT": 1},
        "head": None,
        "requirements": "vector",
        "form": "",
        "optional": False,
    }
    frame_slot = frame.FrameSlot.from_slot_dict(slot_dict)

    def test_frame_slot_builder(self):
        for k in self.slot_dict.keys():
            assert hasattr(self.frame_slot, k)
            assert getattr(self.frame_slot, k) == self.slot_dict[k]
        assert self.frame_slot.candidates == []
        assert self.frame_slot.bond is None

    def test_set_bond(self):
        self.frame_slot.set_bond("TEST BOND")
        assert self.frame_slot.bond == "TEST BOND"

    def test_get_bond(self):
        self.frame_slot.set_bond("TEST BOND")
        my_bond = self.frame_slot.get_bond()
        assert my_bond == "TEST BOND"

    def test_set_form(self):
        self.frame_slot.set_bond("TEST FORM")
        assert self.frame_slot.bond == "TEST FORM"

    def test_add_candidate(self):
        self.frame_slot.add_candidate([1])
        self.frame_slot.add_candidate([2])
        assert self.frame_slot.candidates == [[1], [2]]

    def test_extend_candidates(self):
        self.frame_slot.extend_candidates([[3, 4, 5], [6, 7]])
        assert self.frame_slot.candidates == [[1], [2], [3, 4, 5], [6, 7]]

    def test_remove_candidate(self):
        self.frame_slot.remove_candidate([1])
        assert self.frame_slot.candidates == [[2], [3, 4, 5], [6, 7]]

    def test_replace_candidates(self):
        self.frame_slot.replace_candidates([9, 10])
        assert self.frame_slot.candidates == [9, 10]
