import spacy

from construction_finder import codelets, frame


class TestFrameMatcher:
    def test_from_frame_and_sentence(
        self,
        dative_frame_matcher,
        codelet_info,
        dont_give_me_that_sentence_doc,
        dative_frame,
    ):
        assert dative_frame_matcher.urgency_level == 1
        assert dative_frame_matcher.codelet_probability == 1
        assert dative_frame_matcher.sentence_doc == dont_give_me_that_sentence_doc
        assert dative_frame_matcher.not_bonded_slot_ids is None
        assert str(dative_frame_matcher.frame) == str(dative_frame)

    def test_run(self, dative_frame_matcher):
        frame_matcher_result = dative_frame_matcher.run()
        for i, codelet in enumerate(frame_matcher_result.new_codelets):
            assert isinstance(codelet, codelets.SlotMatcher)
            assert codelet.urgency_level == 2
            assert codelet.codelet_probability == 1
            assert codelet.temp_modifier == 5.25
            assert codelet.slot_id == i
        assert frame_matcher_result.temp_modifier == 21

    def test_set_bond(self, dative_frame_matcher, codelet):

        new_codelets = dative_frame_matcher.set_bond(0, [2], codelet)
        assert dative_frame_matcher.frame.slots[0].bond == [2]
        assert dative_frame_matcher.frame.slots[0].form == "give"
        assert dative_frame_matcher.frame.all_required_slots_found == False
        assert dative_frame_matcher.frame.required_slots_to_find == 3
        assert len(new_codelets) == 0

        _ = dative_frame_matcher.set_bond(1, ["PRODROP"], codelet)
        assert dative_frame_matcher.frame.all_required_slots_found == False
        assert dative_frame_matcher.frame.required_slots_to_find == 2

        _ = dative_frame_matcher.set_bond(2, [4], codelet)
        assert dative_frame_matcher.frame.all_required_slots_found == False
        assert dative_frame_matcher.frame.required_slots_to_find == 1

        new_codelets = dative_frame_matcher.set_bond(3, [3], codelet)
        assert dative_frame_matcher.frame.all_required_slots_found == True
        assert dative_frame_matcher.frame.required_slots_to_find == 0
        assert len(new_codelets) == 1

    def test_get_form(self, dative_frame_matcher):
        output = dative_frame_matcher.get_form([2])[0]
        assert isinstance(output, spacy.tokens.token.Token)
        assert output.text == "give"

    def test_create_frame_finalizer(self, dative_frame_matcher):
        output = dative_frame_matcher.create_frame_finalizer(
            urgency_level=1, temp_modifier=42
        )
        assert isinstance(output, codelets.FrameFinalizer)
        assert output.frame_matcher == dative_frame_matcher
        assert output.urgency_level == 2
        assert output.temp_modifier == 42

    def test_assign_noun_phrases(self, dative_frame_matcher):
        dative_frame_matcher.assign_noun_phrases("TEST_NOUN_PHRASES")
        assert dative_frame_matcher.noun_phrases == "TEST_NOUN_PHRASES"
