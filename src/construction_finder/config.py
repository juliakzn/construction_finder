import spacy

from construction_finder import database

STARTING_TEMPERATURE = 144

nlp = spacy.load("en_core_web_lg")
session = database.provide_session(database.engine)
