import logging

import pytest
import spacy
import sqlalchemy
from sqlalchemy import orm

from construction_finder import codelets, database, frame


@pytest.fixture
def nlp():
    # TODO make it a small testing NLP
    return spacy.load("en_core_web_lg")


@pytest.fixture
def dont_give_me_that():
    return "Don’t give me that."


@pytest.fixture
def give_that_to_me():
    return "Give that to me."


@pytest.fixture
def wonderful_gifts():
    return "And they gave some of the most wonderful gifts to everyone"


@pytest.fixture
def dative_frame_dict():
    DATIVE_FRAME = {
        "priority": 3,
        "slots": {
            0: {
                "variable_or_constant": "variable",
                "synt_type": "VERB",
                "roles": {"ROOT": 1},
                "head": None,
                "requirements": "vector",
                "form": "",
                "requirement_type": "required",
            },
            2: {
                "variable_or_constant": "variable",
                "synt_type": "NP",
                "roles": {"nsubj": 0.9},
                "head": 0,
                "requirements": "animate",
                "form": "",
                "requirement_type": "required",
            },
            3: {
                "variable_or_constant": "variable",
                "synt_type": "NP",
                "roles": {"dobj": 0.9},
                "requirements": "inanimate",
                "head": 0,
                "form": "",
                "requirement_type": "required",
            },
            4: {
                "variable_or_constant": "variable",
                "synt_type": "NP",
                "roles": {"dative": 0.9},
                "head": 0,
                "requirements": "animate",
                "form": "",
                "requirement_type": "required",
            },
        },
    }

    return DATIVE_FRAME


@pytest.fixture
def to_frame_dict():
    TO_FRAME = {
        "priority": 3,
        "slots": {
            0: {
                "variable_or_constant": "variable",
                "synt_type": "VERB",
                "roles": {"ROOT": 1},
                "head": None,
                "requirements": "vector",
                "form": "",
                "requirement_type": "required",
            },
            1: {
                "variable_or_constant": "constant",
                "synt_type": "ADP",
                "roles": {"dative": 1},
                "head": 0,
                "requirements": "to",
                "form": "",
                "requirement_type": "required",
            },
            2: {
                "variable_or_constant": "variable",
                "synt_type": "NP",
                "roles": {"nsubj": 0.9},
                "head": 0,
                "requirements": "animate",
                "form": "",
                "requirement_type": "required",
            },
            3: {
                "variable_or_constant": "variable",
                "synt_type": "NP",
                "roles": {"pobj": 0.9},
                "requirements": "inanimate",
                "head": 0,
                "form": "",
                "requirement_type": "required",
            },
            4: {
                "variable_or_constant": "variable",
                "synt_type": "NP",
                "roles": {"pobj": 0.9},
                "head": 1,
                "requirements": "animate",
                "form": "",
                "requirement_type": "required",
            },
        },
    }
    return TO_FRAME


@pytest.fixture
def imperative_frame_dict():

    IMPERATIVE_FRAME = {
        "priority": 3,
        "slots": {
            0: {
                "variable_or_constant": "variable",
                "synt_type": "VERB",
                "roles": {"ROOT": 1},
                "head": None,
                "requirements": "vector",
                "form": "",
                "absolute_order": 0,
                "requirement_type": "required",
            },
            1: {
                "variable_or_constant": "constant",
                "synt_type": "PUNCT",
                "roles": {"punct": 0.9},
                "head": 0,
                "requirements": [".", "!"],
                "form": "",
                "absolute_order": -1,
                "requirement_type": "required",
            },
        },
        "dependent_processes": ["ProdropModifier"],
    }

    return IMPERATIVE_FRAME


@pytest.fixture
def distributive_frame_dict():

    DISTRIBUTIVE_FRAME = {
        "priority": 1,
        "pattern": True,
        "slots": {
            0: {
                "variable_or_constant": "constant",
                "synt_type": "DET",
                "roles": {"": 1},
                "head": None,
                "requirements": [
                    "both",
                    "either",
                    "neither",
                    "every",
                    "each",
                    "all",
                    "none",
                    "every one",
                    "everyone",
                    "some",
                ],
                "form": "",
                "requirement_type": "required",
            },
            1: {
                "variable_or_constant": "constant",
                "synt_type": "ADP",
                "roles": {"prep": 1},
                "head": 0,
                "requirements": "of",
                "form": "",
                "requirement_type": "required",
            },
            2: {
                "variable_or_constant": "variable",
                "synt_type": "NP",
                "roles": {"pobj": 1},
                "head": 1,
                "requirements": "NP",
                "form": "",
                "requirement_type": "required",
            },
        },
        "dependent_processes": ["NPCreator"],
    }
    return DISTRIBUTIVE_FRAME


@pytest.fixture
def frames(imperative_frame_dict):
    return [imperative_frame_dict]


@pytest.fixture
def distributive_frames(distributive_frame_dict):
    return [distributive_frame_dict]


@pytest.fixture()
def imperative_frame(imperative_frame_dict):
    return frame.Frame.from_frame_dict(imperative_frame_dict)


@pytest.fixture()
def dative_frame(dative_frame_dict):
    return frame.Frame.from_frame_dict(dative_frame_dict)


@pytest.fixture()
def to_frame(to_frame_dict):
    return frame.Frame.from_frame_dict(to_frame_dict)


@pytest.fixture()
def distributive_frame(distributive_frame_dict):
    return frame.Frame.from_frame_dict(distributive_frame_dict)


@pytest.fixture()
def codelet_info():
    return {"urgency_level": 1, "codelet_probability": 1}


@pytest.fixture
def dont_give_me_that_sentence_doc(nlp, dont_give_me_that):
    return nlp(dont_give_me_that)


@pytest.fixture
def give_that_to_me_sentence_doc(nlp, give_that_to_me):
    return nlp(give_that_to_me)


@pytest.fixture
def wonderful_gifts_doc(nlp, wonderful_gifts):
    return nlp(wonderful_gifts)


@pytest.fixture
def dative_frame_matcher(codelet_info, dont_give_me_that_sentence_doc, dative_frame):
    frame_matcher_object = codelets.FrameMatcher.from_frame_and_sentence(
        codelet_info, dative_frame, dont_give_me_that_sentence_doc
    )
    frame_matcher_object.temp_modifier = 42
    return frame_matcher_object


@pytest.fixture
def to_frame_matcher(codelet_info, give_that_to_me_sentence_doc, to_frame):
    frame_matcher_object = codelets.FrameMatcher.from_frame_and_sentence(
        codelet_info, to_frame, give_that_to_me_sentence_doc
    )
    frame_matcher_object.temp_modifier = 42
    return frame_matcher_object


@pytest.fixture
def wonderful_gifts_to_frame_matcher(codelet_info, wonderful_gifts_doc, to_frame):
    frame_matcher_object = codelets.FrameMatcher.from_frame_and_sentence(
        codelet_info, to_frame, wonderful_gifts_doc
    )
    frame_matcher_object.temp_modifier = 42
    return frame_matcher_object


@pytest.fixture
def wonderful_gifts_distributive_frame_matcher(
    codelet_info, wonderful_gifts_doc, distributive_frame
):
    frame_matcher_object = codelets.FrameMatcher.from_frame_and_sentence(
        codelet_info, distributive_frame, wonderful_gifts_doc
    )
    frame_matcher_object.temp_modifier = 42
    return frame_matcher_object


@pytest.fixture
def imperative_frame_matcher(
    codelet_info, dont_give_me_that_sentence_doc, imperative_frame
):
    frame_matcher_object = codelets.FrameMatcher.from_frame_and_sentence(
        codelet_info, imperative_frame, dont_give_me_that_sentence_doc
    )
    frame_matcher_object.temp_modifier = 42
    return frame_matcher_object


@pytest.fixture
def codelet():
    codelet = codelets.Codelet(2, 0.42)
    codelet.temp_modifier = 42
    return codelet


@pytest.fixture
def local_session():
    engine = sqlalchemy.create_engine(
        "sqlite://", echo=False
    )  # echo=False disables logging to console, which is intended for testing
    connection = engine.connect()
    database.Sentence.metadata.create_all(connection)
    transaction = connection.begin()
    TestingSessionLocal = orm.sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def mute_logging(caplog):
    file_names = ["codelets", "coderack", "workspace", "workspace_modifiers"]
    # Disable logging for testing
    for file_name in file_names:
        caplog.set_level(logging.CRITICAL, logger=f"construction_finder.{file_name}")
