from construction_finder import codelets


class TestWorkSpaceModifier:
    wsm = codelets.WorkSpaceModifier()

    def test_str(self):
        assert str(self.wsm) == "WorkSpaceModifier"
