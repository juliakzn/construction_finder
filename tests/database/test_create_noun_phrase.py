from construction_finder import database


def test_create_noun_phrase(wonderful_gifts, nlp):
    token_list = [5, 6, 7, 8]
    form_list = [nlp(wonderful_gifts)[t].text for t in token_list]
    sentence, np, np_tokens = database.create_noun_phrase(
        nlp, wonderful_gifts, token_list
    )
    assert isinstance(sentence, database.Sentence)
    assert isinstance(np, database.NounPhrase)
    for t, token_number, form in zip(np_tokens, token_list, form_list):
        assert t.token_number == token_number
        assert t.form == form
