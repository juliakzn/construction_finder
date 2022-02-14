from typing import Tuple

import pytest

from construction_finder import codelets, config, database, frame


class TestSlotMatcher:
    @pytest.fixture
    def session_with_np_chunks(self, local_session, to_frame_matcher, nlp, monkeypatch):
        sentence = database.Sentence(to_frame_matcher.sentence_doc.text, nlp)
        np1 = database.NounPhrase(sentence)
        np2 = database.NounPhrase(sentence)
        np1_tokens = database.NounPhraseTokens(np1, 1)
        np2_tokens = database.NounPhraseTokens(np2, 3)
        local_session.add_all([sentence, np1, np2, np1_tokens, np2_tokens])
        local_session.commit()
        monkeypatch.setattr(config, "session", local_session)

    @pytest.fixture
    def constant_slot_matcher(self, codelet_info, to_frame_matcher):
        slot_id = 1
        temp_modifier = 42
        return codelets.SlotMatcher.from_slot_frame_matcher_and_temp_modifier(
            codelet_info, to_frame_matcher, slot_id, temp_modifier
        )

    @pytest.fixture
    def complex_constant_slot_matcher(
        self, codelet_info, wonderful_gifts_distributive_frame_matcher
    ):
        slot_id = 0
        temp_modifier = 42
        return codelets.SlotMatcher.from_slot_frame_matcher_and_temp_modifier(
            codelet_info,
            wonderful_gifts_distributive_frame_matcher,
            slot_id,
            temp_modifier,
        )

    @pytest.fixture
    def np_slot_matcher(self, codelet_info, to_frame_matcher):
        slot_id = 2
        temp_modifier = 42
        return codelets.SlotMatcher.from_slot_frame_matcher_and_temp_modifier(
            codelet_info, to_frame_matcher, slot_id, temp_modifier
        )

    @pytest.fixture
    def verb_slot_matcher(self, codelet_info, imperative_frame_matcher):
        slot_id = 0
        temp_modifier = 42
        return codelets.SlotMatcher.from_slot_frame_matcher_and_temp_modifier(
            codelet_info, imperative_frame_matcher, slot_id, temp_modifier
        )

    def test_from_slot_frame_matcher_and_temp_modifier(
        self, constant_slot_matcher, to_frame_matcher
    ):
        assert constant_slot_matcher.urgency_level == 1
        assert constant_slot_matcher.codelet_probability == 1
        assert constant_slot_matcher.codelet_type == "SlotMatcher"
        assert constant_slot_matcher.frame_matcher == to_frame_matcher
        assert constant_slot_matcher.frame == to_frame_matcher.frame
        assert constant_slot_matcher.frame_slots == to_frame_matcher.frame.slots
        assert constant_slot_matcher.slot_id == 1
        assert constant_slot_matcher.slot == to_frame_matcher.frame.slots[1]
        assert constant_slot_matcher.temp_modifier == 42

    def test_run_constant(self, constant_slot_matcher):
        output = constant_slot_matcher.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 1
        assert isinstance(output.new_codelets[0], codelets.ConstantChecker)
        assert output.new_codelets[0].urgency_level == 2
        assert output.new_codelets[0].codelet_probability == 1
        assert output.new_codelets[0].slot_id == 1
        assert output.temp_modifier == 21
        assert constant_slot_matcher.slot.candidates == [[2]]

    def test_run_complex_constant(self, complex_constant_slot_matcher):
        output = complex_constant_slot_matcher.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 2
        assert isinstance(output.new_codelets[0], codelets.FrameMatcher)
        assert output.new_codelets[0].urgency_level == 2
        assert output.new_codelets[0].codelet_probability == 1
        assert output.new_codelets[0].frame.slots[
            complex_constant_slot_matcher.slot_id
        ].candidates == [[10]]

        assert isinstance(output.new_codelets[1], codelets.ConstantChecker)
        assert output.new_codelets[1].urgency_level == 2
        assert output.new_codelets[1].codelet_probability == 1
        assert output.new_codelets[1].slot_id == 0

        assert output.temp_modifier == 21
        assert complex_constant_slot_matcher.slot.candidates == [[3]]

        assert isinstance(output.new_active_frames[0], Tuple)
        assert output.new_active_frames[0][0] == "append"
        assert isinstance(output.new_active_frames[0][1], frame.Frame)
        expected_frame = (
            "{'variable_or_constant': 'constant', 'synt_type': 'DET', 'roles': {'': 1}, "
            + "'head': None, 'requirements': ['both', 'either', 'neither', 'every', 'each', "
            + "'all', 'none', 'every one', 'everyone', 'some'], 'form': 'everyone', "
            + "'requirement_type': 'required', 'candidates': [[10]], 'bond': [10]}, \n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'ADP', 'roles': {'prep': "
            + "1}, 'head': 0, 'requirements': 'of', 'form': '', 'requirement_type': "
            + "'required', 'candidates': [], 'bond': None}, \n"
            + "{'variable_or_constant': 'variable', 'synt_type': 'NP', 'roles': {'pobj': "
            + "1}, 'head': 1, 'requirements': 'NP', 'form': '', 'requirement_type': "
            + "'required', 'candidates': [], 'bond': None}, \n"
            + "(dependent_processes, NPCreator), \n"
        )
        assert str(output.new_active_frames[0][1]) == expected_frame

    def test_run_verb_variable(self, verb_slot_matcher):
        output = verb_slot_matcher.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 1
        assert isinstance(output.new_codelets[0], codelets.DependencyMatcher)
        assert output.new_codelets[0].urgency_level == 2
        assert output.new_codelets[0].codelet_probability == 1
        assert output.new_codelets[0].slot_id == 0
        assert output.temp_modifier == 21
        assert verb_slot_matcher.slot.candidates == [[2]]

    def test_run_np_variable(self, np_slot_matcher, session_with_np_chunks):
        output = np_slot_matcher.run()
        assert isinstance(output, codelets.CodeletResults)
        assert len(output.new_codelets) == 1
        assert isinstance(output.new_codelets[0], codelets.DependencyMatcher)
        assert output.new_codelets[0].urgency_level == 2
        assert output.new_codelets[0].codelet_probability == 1
        assert output.new_codelets[0].slot_id == 2
        assert output.temp_modifier == 21
        assert np_slot_matcher.slot.candidates == [[1], [3]]

    def test_str(self, np_slot_matcher):
        output = str(np_slot_matcher)
        expected = "<SlotMatcher>: urgency_level=1, temp_modifier=42, slot_id=2"
        assert output == expected
