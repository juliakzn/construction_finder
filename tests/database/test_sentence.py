import uuid

from construction_finder import database


def test_sentence(local_session, sentences, texts):

    for sentence, expected_text in zip(
        list(local_session.query(database.Sentence)), texts
    ):
        assert isinstance(sentence.sentence_id, uuid.UUID)
        assert sentence.text == expected_text
