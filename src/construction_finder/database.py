import uuid

import sqlalchemy
from sqlalchemy import Column, Integer, UnicodeText, orm, types
from sqlalchemy.ext import declarative

engine = sqlalchemy.create_engine("sqlite://", echo=True)
Base = declarative.declarative_base(bind=engine)


def provide_session(engine):
    connection = engine.connect()
    Sentence.metadata.create_all(connection)
    transaction = connection.begin()
    SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal(bind=connection)
    return session


class UUID(types.TypeDecorator):
    impl = types.BINARY

    cache_ok = True

    def __init__(self):
        self.impl.length = 16
        types.TypeDecorator.__init__(self, length=self.impl.length)

    def process_bind_param(self, value, dialect=None):
        if value and isinstance(value, uuid.UUID):
            return value.bytes
        elif value and not isinstance(value, uuid.UUID):
            raise ValueError(f"value {value} is not a valid uuid.UUID")
        else:
            return None

    def process_result_value(self, value, dialect=None):
        if value:
            return uuid.UUID(bytes=value)
        else:
            return None

    def is_mutable(self):
        return False


class Sentence(Base):
    __tablename__ = "sentence"
    sentence_id = Column(UUID, primary_key=True)
    text = Column(UnicodeText, nullable=True)

    def __init__(self, text, nlp):
        self.sentence_id = uuid.uuid4()
        self.text = text
        self.nlp = nlp
        self.doc = nlp(text)


class NounPhrase(Base):
    __tablename__ = "sentence_noun_phrase"
    np_id = Column(UUID, primary_key=True)
    sentence_id = Column(UUID, sqlalchemy.ForeignKey("sentence.sentence_id"))

    sentence_host = orm.relationship(
        Sentence,
        primaryjoin=sentence_id == Sentence.sentence_id,
        backref="noun_phrases",
    )

    def __init__(self, sentence):
        self.sentence_host = sentence
        self.np_id = uuid.uuid4()

    def get_form(self):
        return [token.form for token in self.tokens]

    def __contains__(self, np):
        current_np_form = self.get_form()
        np_to_compare_form = np.get_form()
        return " ".join(np_to_compare_form) in " ".join(current_np_form)


class NounPhraseTokens(Base):
    __tablename__ = "noun_phrase_tokens"
    token_id = Column(UUID, primary_key=True)
    np_id = Column(UUID, sqlalchemy.ForeignKey("sentence_noun_phrase.np_id"))
    token_number = Column(Integer, nullable=False)
    form = Column(UnicodeText, nullable=True)

    np_host = orm.relationship(
        NounPhrase,
        primaryjoin=np_id == NounPhrase.np_id,
        backref="tokens",
    )

    def __init__(self, noun_phrase, token_number):
        self.np_host = noun_phrase
        self.token_id = uuid.uuid4()
        self.token_number = token_number
        self.form = self.np_host.sentence_host.doc[token_number].text


def create_noun_phrase(nlp, sentence, token_list):
    sentence = Sentence(sentence, nlp)
    np = NounPhrase(sentence)
    np_tokens = list()
    for token in token_list:
        t = NounPhraseTokens(np, token)
        np_tokens.append(t)

    return sentence, np, np_tokens
