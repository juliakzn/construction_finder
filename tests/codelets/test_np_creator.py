import pytest

from construction_finder import codelets, config, frame_storage, workspace


@pytest.fixture
def np_creator(wonderful_gifts_to_frame_matcher):
    return codelets.NPCreator()


@pytest.fixture()
def work_space(monkeypatch, nlp, wonderful_gifts, frames):

    monkeypatch.setattr(frame_storage, "FRAMES", frames)
    monkeypatch.setattr(config, "STARTING_TEMPERATURE", 42)
    work_space = workspace.WorkSpace.from_nlp_and_txt(nlp, wonderful_gifts)

    return work_space


class TestNPCreator:
    def test_init(self, np_creator):
        assert isinstance(np_creator, codelets.NPCreator)

    def test_assign_workspace(self, np_creator, work_space):
        np_creator.assign_workspace(work_space)
        assert np_creator.workspace == work_space

    def test_assign_features(self, np_creator, wonderful_gifts_to_frame_matcher):
        np_creator.assign_properties(wonderful_gifts_to_frame_matcher)
        expected_bonded = set([token for token in np_creator.np.tokens])
        assert (
            expected_bonded == wonderful_gifts_to_frame_matcher.frame.get_all_bonded()
        )
        assert (
            np_creator.np.sentence_host.text
            == wonderful_gifts_to_frame_matcher.sentence_doc.text
        )
