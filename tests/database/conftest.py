import pytest

from construction_finder import database


@pytest.fixture
def texts():
    return ["Don't give that to me", "Give it to them"]


@pytest.fixture
def sentences(local_session, nlp, texts):
    txt1, txt2 = texts
    s1 = database.Sentence(txt1, nlp)
    s2 = database.Sentence(txt2, nlp)

    local_session.add_all([s1, s2])
    local_session.commit()

    return s1, s2


@pytest.fixture
def nps(local_session, sentences):

    s1, s2 = sentences
    np1 = database.NounPhrase(s1)
    np2 = database.NounPhrase(s1)
    np3 = database.NounPhrase(s2)
    np4 = database.NounPhrase(s2)

    local_session.add_all([np1, np2, np3, np4])
    local_session.commit()

    return [np1, np2, np3, np4]


@pytest.fixture
def np_tokens(local_session, nps, token_numbers):
    np1, np2, np3, np4 = nps
    np1_1 = database.NounPhraseTokens(np1, token_numbers[0])
    np2_1 = database.NounPhraseTokens(np2, token_numbers[1])
    np3_1 = database.NounPhraseTokens(np3, token_numbers[2])
    np4_1 = database.NounPhraseTokens(np4, token_numbers[3])

    local_session.add_all([np1_1, np2_1, np3_1, np4_1])
    local_session.commit()

    return [np1_1, np2_1, np3_1, np4_1]


@pytest.fixture
def token_numbers():
    return [3, 5, 1, 3]
