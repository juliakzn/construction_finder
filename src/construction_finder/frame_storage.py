# TODO: add linear order to frame_storage to process cases like 'The more the merrier'

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

IMPERATIVE_FRAME = {
    "priority": 2,
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


FRAMES = [
    TO_FRAME,
    # DATIVE_FRAME,
    # IMPERATIVE_FRAME,
    DISTRIBUTIVE_FRAME,
]
