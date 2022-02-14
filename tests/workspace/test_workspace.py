# import logging

import pytest

from construction_finder import codelets  # noun_phrase,
from construction_finder import (active_frames, coderack, config, database,
                                 frame, frame_storage, workspace)


def clear_data(db, session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


@pytest.fixture()
def work_space(monkeypatch, nlp, dont_give_me_that, frames):

    monkeypatch.setattr(frame_storage, "FRAMES", frames)
    monkeypatch.setattr(config, "STARTING_TEMPERATURE", 144)
    work_space = workspace.WorkSpace.from_nlp_and_txt(nlp, dont_give_me_that)

    return work_space


@pytest.fixture()
def wonderful_gifts_work_space(
    monkeypatch, nlp, wonderful_gifts, distributive_frames, local_session
):

    monkeypatch.setattr(frame_storage, "FRAMES", distributive_frames)
    monkeypatch.setattr(config, "STARTING_TEMPERATURE", 144)
    monkeypatch.setattr(config, "session", local_session)
    work_space = workspace.WorkSpace.from_nlp_and_txt(nlp, wonderful_gifts)

    return work_space


@pytest.fixture
def noun_phrase_instance(nlp, wonderful_gifts):
    sentence, np, tokens = database.create_noun_phrase(
        nlp, wonderful_gifts, [3, 4, 5, 6, 7, 8]
    )
    return np


class TestWorkSpace:
    def test_from_nlp_and_txt(self, work_space, nlp, dont_give_me_that):
        assert work_space.nlp == nlp
        assert work_space.txt == dont_give_me_that
        assert isinstance(work_space.coderack, coderack.CodeRack)
        assert isinstance(work_space.active_frames, active_frames.ActiveFrames)
        assert work_space.temperature == 144

    def test_find_frames(self, frames, work_space):
        work_space.find_frames(frames)
        active_frames_dict = work_space.active_frames.frame_priority_groups
        for priority_group in active_frames_dict.keys():
            active_frame_list = work_space.active_frames.frame_priority_groups[
                priority_group
            ]
            frame_list = [f for f in frames if f["priority"] == priority_group]
            for active_frame, frame_dict in zip(active_frame_list, frame_list):
                initialized_frame = frame.Frame.from_frame_dict(frame_dict)
                assert str(active_frame) == str(initialized_frame)
                assert active_frame.dependent_processes[0].workspace == work_space
        for urgency_level in work_space.coderack.urgency_levels:
            for codelet in work_space.coderack.urgency_bins[urgency_level]:
                assert isinstance(codelet, codelets.FrameMatcher)
                assert codelet.urgency_level == 1
                assert codelet.temp_modifier == 144

    def test_run(self, work_space):

        active_frames_dict = work_space.run()
        expected = (
            "Frame 3-0:\n"
            + "{'variable_or_constant': 'variable', 'synt_type': 'VERB', 'roles': {'ROOT': 1}, 'head': None, 'requirements': 'vector', 'form': 'give', 'absolute_order': 0, 'requirement_type': 'required', 'candidates': [[2]], 'bond': [2]}, \n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'PUNCT', 'roles': {'punct': 0.9}, 'head': 0, 'requirements': ['.', '!'], 'form': '.', 'absolute_order': -1, 'requirement_type': 'required', 'candidates': [[5]], 'bond': [5]}, \n"
            + "(dependent_processes, ProdropModifier), \n"
        )

        assert str(active_frames_dict) == expected
        assert work_space.temperature == 0

    def test_run_one_priority(self, work_space):
        work_space.run_one_priority(3, 72)
        expected = (
            "Frame 3-0:\n"
            + "{'variable_or_constant': 'variable', 'synt_type': 'VERB', 'roles': {'ROOT': 1}, 'head': None, 'requirements': 'vector', 'form': 'give', 'absolute_order': 0, 'requirement_type': 'required', 'candidates': [[2]], 'bond': [2]}, \n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'PUNCT', 'roles': {'punct': 0.9}, 'head': 0, 'requirements': ['.', '!'], 'form': '.', 'absolute_order': -1, 'requirement_type': 'required', 'candidates': [[5]], 'bond': [5]}, \n"
            + "(dependent_processes, ProdropModifier), \n"
        )

        assert str(work_space.active_frames) == expected
        assert work_space.temperature == 72

    def test_run_one_priority_new_active_frame(self, wonderful_gifts_work_space):
        wonderful_gifts_work_space.run_one_priority(1, 72)
        # Based on the order of codelets, two possible variants for slot 2 candidates are possible
        expected1 = (
            "Frame 1-0:\n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'DET', 'roles': {'': 1}, "
            + "'head': None, 'requirements': ['both', 'either', 'neither', 'every', 'each', "
            + "'all', 'none', 'every one', 'everyone', 'some'], 'form': 'some', "
            + "'requirement_type': 'required', 'candidates': [[3]], 'bond': [3]}, \n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'ADP', 'roles': {'prep': "
            + "1}, 'head': 0, 'requirements': 'of', 'form': 'of', 'requirement_type': "
            + "'required', 'candidates': [[4]], 'bond': [4]}, \n"
            + "{'variable_or_constant': 'variable', 'synt_type': 'NP', 'roles': {'pobj': "
            + "1}, 'head': 1, 'requirements': 'NP', 'form': 'the most wonderful gifts', "
            + "'requirement_type': 'required', 'candidates': [[1], [5, 6, 7, 8], [10], "
            + "[5]], 'bond': [5, 6, 7, 8]}, \n"
            + "(dependent_processes, NPCreator), \n"
        )
        expected2 = (
            "Frame 1-0:\n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'DET', 'roles': {'': 1}, "
            + "'head': None, 'requirements': ['both', 'either', 'neither', 'every', 'each', "
            + "'all', 'none', 'every one', 'everyone', 'some'], 'form': 'some', "
            + "'requirement_type': 'required', 'candidates': [[3]], 'bond': [3]}, \n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'ADP', 'roles': {'prep': "
            + "1}, 'head': 0, 'requirements': 'of', 'form': 'of', 'requirement_type': "
            + "'required', 'candidates': [[4]], 'bond': [4]}, \n"
            + "{'variable_or_constant': 'variable', 'synt_type': 'NP', 'roles': {'pobj': "
            + "1}, 'head': 1, 'requirements': 'NP', 'form': 'the most wonderful gifts', "
            + "'requirement_type': 'required', 'candidates': [[1], [5, 6, 7, 8], [10], [3],"
            + "[5]], 'bond': [5, 6, 7, 8]}, \n"
            + "(dependent_processes, NPCreator), \n"
        )

        assert (
            str(wonderful_gifts_work_space.active_frames) == expected1
            or str(wonderful_gifts_work_space.active_frames) == expected2
        )

    def test_add_np(self, work_space, noun_phrase_instance, local_session, monkeypatch):
        monkeypatch.setattr(config, "session", local_session)
        work_space.add_np(noun_phrase_instance)
        assert (
            local_session.query(database.NounPhrase)
            .filter_by(np_id=noun_phrase_instance.np_id)
            .count()
            == 1
        )

    def test_remove_np(
        self, work_space, noun_phrase_instance, local_session, monkeypatch
    ):

        monkeypatch.setattr(config, "session", local_session)
        local_session.add_all([noun_phrase_instance])
        local_session.commit()
        assert (
            local_session.query(database.NounPhrase)
            .filter_by(np_id=noun_phrase_instance.np_id)
            .count()
            == 1
        )
        assert (
            local_session.query(database.Sentence)
            .filter_by(sentence_id=noun_phrase_instance.sentence_host.sentence_id)
            .count()
            == 1
        )
        assert (
            local_session.query(database.NounPhraseTokens)
            .filter_by(np_id=noun_phrase_instance.np_id)
            .count()
            == 6
        )

        work_space.remove_np(noun_phrase_instance)
        assert (
            local_session.query(database.NounPhrase)
            .filter_by(np_id=noun_phrase_instance.np_id)
            .count()
            == 0
        )
        assert (
            local_session.query(database.Sentence)
            .filter_by(sentence_id=noun_phrase_instance.sentence_host.sentence_id)
            .count()
            == 0
        )
        assert (
            local_session.query(database.NounPhraseTokens)
            .filter_by(np_id=noun_phrase_instance.np_id)
            .count()
            == 0
        )

    def test_find_np_phrases(self, work_space, local_session, monkeypatch):
        monkeypatch.setattr(config, "session", local_session)
        # assert work_space.noun_phrases == []
        np_list = list()
        for np in work_space.doc.noun_chunks:
            token_list = list(range(np.start, np.end))
            sentence, np, tokens = database.create_noun_phrase(
                work_space.nlp, work_space.doc.text, token_list
            )
            np_list.append(np)

        dets = [token.i for token in work_space.doc if (token.pos_ == "DET")]
        for det in dets:
            sentence, np, tokens = database.create_noun_phrase(
                work_space.nlp, work_space.doc.text, [det]
            )
            np_list.append(np)

        work_space.find_np_phrases()
        for output, expected in zip(work_space.noun_phrases, np_list):
            assert output.sentence_host.text == expected.sentence_host.text
            assert output in expected and expected in output

        assert local_session.query(database.NounPhrase).count() == len(np_list)
