import uuid

import pytest

from construction_finder import database


class TestNounPhrase:
    def test_init(self, local_session, sentences, nps):

        s1, s2 = sentences
        sentence_hosts = [s1, s1, s2, s2]
        for np, sentence_host in zip(
            list(local_session.query(database.NounPhrase)), sentence_hosts
        ):
            assert isinstance(np.np_id, uuid.UUID)
            assert np.sentence_host == sentence_host
            assert np in sentence_host.noun_phrases

    def test_contains(self, local_session, wonderful_gifts_doc, nlp):
        sentence = database.Sentence(wonderful_gifts_doc.text, nlp)

        same_np = database.NounPhrase(sentence)
        same_tokens = [3, 4, 5, 6, 7, 8]
        for token in same_tokens:
            local_session.add(database.NounPhraseTokens(same_np, token))

        gifts_np = database.NounPhrase(sentence)
        gifts_tokens = [5, 6, 7, 8]
        for token in gifts_tokens:
            local_session.add(database.NounPhraseTokens(gifts_np, token))

        everyone_np = database.NounPhrase(sentence)
        everyone_tokens = [10]
        for token in everyone_tokens:
            local_session.add(database.NounPhraseTokens(everyone_np, token))

        local_session.commit()

        assert same_np in same_np
        assert gifts_np in same_np
        assert everyone_np not in same_np
