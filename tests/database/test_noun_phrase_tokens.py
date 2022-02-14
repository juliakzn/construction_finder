import uuid

from construction_finder import database


def test_noun_phrase_tokens(local_session, nps, np_tokens, token_numbers):

    forms = ["that", "me", "it", "them"]

    for np_token, np, token_number, form in zip(
        list(local_session.query(database.NounPhraseTokens)), nps, token_numbers, forms
    ):
        assert np_token.np_host == np
        assert np_token in np.tokens
        assert isinstance(np_token.token_id, uuid.UUID)
        assert np_token.token_number == token_number
        assert np_token.form == form
