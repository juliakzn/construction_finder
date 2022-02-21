import abc
import logging
from typing import Dict, List, Union

import attr
import spacy
from attr import validators

from construction_finder import config, database, frame
from construction_finder.construction_finder_logger import log_bonding

logger = logging.getLogger(f"{__name__}")


class CodeletResults:
    def __init__(
        self,
        new_codelets: List,
        temp_modifier: float,
        workspace_modifiers=None,
        new_active_frames=None,
    ):
        self.new_codelets = new_codelets
        self.workspace_modifiers = workspace_modifiers
        logger.info(
            f"Initialized workspace_modifiers: {self.workspace_modifiers} from {workspace_modifiers}"
        )
        self.new_active_frames = new_active_frames

        # Change temperature modifiers
        if len(new_codelets) > 0:
            for codelet in new_codelets:
                codelet.temp_modifier = temp_modifier / (2 * len(new_codelets))
            self.temp_modifier = temp_modifier / 2
        else:
            self.temp_modifier = temp_modifier


class Codelet:
    def __init__(self, urgency_level: int, codelet_probability: float):
        self.codelet_type = self.__class__.__name__
        self.urgency_level = urgency_level
        self.codelet_probability = codelet_probability
        self.temp_modifier = None

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError("Expected to be implemented by derived classes")

    def __str__(self):
        return f"""<{self.codelet_type}>: urgency_level={self.urgency_level}, temp_modifier={self.temp_modifier}"""


class FrameMatcher(Codelet):
    @classmethod
    def from_frame_and_sentence(
        cls,
        codelet_info: Dict[str, Union[str, int]],
        frame: frame.Frame,
        sentence_doc: spacy.tokens.doc.Doc,
    ):
        """
        Initialize FrameMatcher from frame and sentence,
        if initializing from finding a constant assign a bond to the constant

        frame: frame to match
        sentence_doc: spacy doc construed from a sentence we are trying to find a frame in
        constant: index of the constant in sentence_doc
        """
        frame_matcher = FrameMatcher(**codelet_info)
        frame_matcher.frame = frame
        frame_matcher.sentence_doc = sentence_doc
        frame_matcher.not_bonded_slot_ids = None
        logger.info(f"Created a new frame matcher: {frame_matcher}")
        return frame_matcher

    def run(self):
        new_codelets = list()
        if self.not_bonded_slot_ids is None:
            not_bonded_slot_ids = [
                i
                for i, slot in enumerate(self.frame.slots)
                if (slot.bond == None) and (slot.requirement_type == "required")
            ]
        else:
            not_bonded_slot_ids = self.not_bonded_slot_ids

        for not_bonded_slot_id in not_bonded_slot_ids:
            codelet_info = {
                "urgency_level": self.urgency_level + 1,
                "codelet_probability": 1,
            }
            slot_matcher = SlotMatcher.from_slot_frame_matcher_and_temp_modifier(
                codelet_info, self, not_bonded_slot_id
            )
            new_codelets.append(slot_matcher)

        logger.info(f"Created new slot matchers:")
        for slot_matcher in new_codelets:
            logger.info(str(slot_matcher))

        return CodeletResults(new_codelets, self.temp_modifier)

    def set_bond(self, slot_id, candidate, active_codelet):
        new_codelets = list()
        self.frame.set_bond(slot_id, candidate)
        form = " ".join(
            [token.text for token in self.sentence_doc if token.i in candidate]
        )
        self.frame.set_form(slot_id, form)

        if self.frame.slots[slot_id].requirement_type != "optional":
            self.frame.reduce_required_slots_to_find()

        for i in [i for i in range(len(self.frame.slots)) if i != slot_id]:
            if candidate in self.frame.slots[i].candidates:
                self.frame.slots[i].remove_candidate(candidate)
                logger.info(
                    f"Removing candidate {candidate} from candidates for slot {i}, because it bonded to slot {slot_id}"
                )
                codelet_info = {
                    "urgency_level": self.urgency_level + 1,
                    "codelet_probability": 1,
                }
                single_cand_checker = (
                    SingleCandidateChecker.from_frame_matcher_and_temp_modifier(
                        codelet_info, self
                    )
                )
                new_codelets.append(single_cand_checker)

        # Check if that was the last required slot, if yes initialize a FrameFinalizer
        if self.frame.required_slots_to_find == 0:
            self.frame.set_all_required_slots_found()
            frame_finalizer = self.create_frame_finalizer(
                active_codelet.urgency_level + 1, active_codelet.temp_modifier / 2
            )
            new_codelets.append(frame_finalizer)

        return new_codelets

    def get_form(self, candidate):
        bonded_text = [
            token for i, token in enumerate(self.sentence_doc) if i in candidate
        ]
        return bonded_text

    def create_frame_finalizer(self, urgency_level, temp_modifier):
        codelet_info = {
            "urgency_level": urgency_level + 1,
            "codelet_probability": 1,
        }
        frame_finalizer = FrameFinalizer.from_frame_matcher_and_temp_modifier(
            codelet_info, self, temp_modifier
        )

        return frame_finalizer

    def assign_noun_phrases(self, noun_phrases):
        self.noun_phrases = noun_phrases


class SlotMatcher(Codelet):
    @classmethod
    def from_slot_frame_matcher_and_temp_modifier(
        cls,
        codelet_info: Dict[str, Union[str, int]],
        frame_matcher: FrameMatcher,
        slot_id: frame.FrameSlot,
        temp_modifier: float = None,
    ):
        slot_matcher = SlotMatcher(**codelet_info)
        slot_matcher.frame_matcher = frame_matcher
        slot_matcher.frame = frame_matcher.frame
        slot_matcher.frame_slots = frame_matcher.frame.slots
        slot_matcher.slot_id = slot_id
        slot_matcher.slot = frame_matcher.frame.slots[slot_id]
        slot_matcher.temp_modifier = temp_modifier

        return slot_matcher

    def run(self):
        """Find all potential candidates for a slot, create bond testers for each slot"""

        logger.info(
            f"Running a slot matcher for slot {self.slot_id} of frame {self.frame}"
        )

        candidates = list()
        new_codelets = list()
        new_active_frames = list()

        if self.slot.variable_or_constant == "constant":

            candidates = [
                [i]
                for i in range(len(self.frame_matcher.sentence_doc))
                if self.frame_matcher.sentence_doc[i].text in self.slot.requirements
            ]

            # If found more than one candidate, create an additional FrameMatcher for the same frame and sentence
            for candidate in candidates[1:]:
                frame_copy = self.frame_matcher.frame.copy()
                codelet_info = {
                    "urgency_level": self.urgency_level + 1,
                    "codelet_probability": 1,
                }
                new_frame_matcher = FrameMatcher.from_frame_and_sentence(
                    codelet_info, frame_copy, self.frame_matcher.sentence_doc
                )
                new_frame_matcher.frame.slots[self.slot_id].add_candidate(candidate)
                new_frame_matcher.set_bond(self.slot_id, candidate, self)
                bonded_text = new_frame_matcher.get_form(candidate)
                log_bonding(
                    logger,
                    new_frame_matcher.frame,
                    self.slot_id,
                    new_frame_matcher.frame.slots[self.slot_id].candidates[0],
                    bonded_text,
                )
                new_codelets.append(new_frame_matcher)
                new_active_frames.append(("append", new_frame_matcher.frame))

            candidates = [candidates[0]]

        elif self.slot.variable_or_constant == "variable":
            # Find candidates
            if self.slot.synt_type == "NP":
                for np in list(config.session.query(database.NounPhrase)):
                    np_indices = [token.token_number for token in np.tokens]
                    candidates.append(np_indices)
            else:
                candidates = [
                    [i]
                    for i in range(len(self.frame_matcher.sentence_doc))
                    if self.frame_matcher.sentence_doc[i].pos_ in self.slot.synt_type
                ]

        # If a slot has absolute order requirements, use them to choose the right candidates
        if hasattr(self.slot, "absolute_order"):

            if self.slot.absolute_order < 0:
                sentence_order = (
                    len(self.frame_matcher.sentence_doc) + self.slot.absolute_order
                )
            else:
                sentence_order = self.slot.absolute_order
            if sentence_order in candidates:
                candidates = [[sentence_order]]

        self.slot.candidates.extend(candidates)
        logger.info(f"Slot matcher identified candidates: {candidates}")

        codelet_info = {
            "urgency_level": self.urgency_level + 1,
            "codelet_probability": 1,
        }

        if self.slot.variable_or_constant == "constant":
            constant_checker = (
                ConstantChecker.from_slot_frame_matcher_and_temp_modifier(
                    codelet_info,
                    self.frame_matcher,
                    self.slot_id,
                )
            )
            new_codelets.append(constant_checker)

        elif self.slot.variable_or_constant == "variable":
            dependency_matcher = (
                DependencyMatcher.from_slot_frame_matcher_and_temp_modifier(
                    codelet_info,
                    self.frame_matcher,
                    self.slot_id,
                )
            )
            new_codelets.append(dependency_matcher)
        logger.info(f"Created new codelets: {new_codelets}")

        return CodeletResults(
            new_codelets, self.temp_modifier, new_active_frames=new_active_frames
        )

    def __str__(self):
        return f"""<{self.codelet_type}>: urgency_level={self.urgency_level}, temp_modifier={self.temp_modifier}, slot_id={self.slot_id}"""


class DependencyMatcher(Codelet):
    @classmethod
    def from_slot_frame_matcher_and_temp_modifier(
        cls,
        codelet_info: Dict[str, Union[str, int]],
        frame_matcher: FrameMatcher,
        slot_id: frame.FrameSlot,
        temp_modifier: float = None,
    ):
        dependency_matcher = DependencyMatcher(**codelet_info)
        dependency_matcher.frame_matcher = frame_matcher
        dependency_matcher.slot_id = slot_id
        dependency_matcher.temp_modifier = temp_modifier

        return dependency_matcher

    def run(self):
        doc = self.frame_matcher.sentence_doc
        head_index = self.frame_matcher.frame.slots[self.slot_id].head
        new_codelets = []

        if head_index is not None:
            if (
                self.frame_matcher.frame.slots[head_index].variable_or_constant
                == "constant"
            ):
                ancestor_form = self.frame_matcher.frame.slots[head_index].requirements
            else:
                ancestor_form = None
            ancestor_synt_type = self.frame_matcher.frame.slots[head_index].synt_type

        highest_probability_bond = 0
        most_probable_candidates = []

        for candidate in self.frame_matcher.frame.slots[self.slot_id].candidates:
            ancestor_synt_type_found = False
            ancestor_form_found = False
            for word_id in candidate:
                # Check ancestor
                if head_index is not None:
                    candidate_head = doc[word_id].head

                    if ancestor_synt_type == candidate_head.pos_:
                        ancestor_synt_type_found = True

                    if ancestor_form and (ancestor_form == candidate_head.text):
                        ancestor_form_found = True

                    if ancestor_synt_type_found and ancestor_form_found:
                        most_probable_candidates.append(candidate)
                        highest_probability_bond = 1 / len(most_probable_candidates)

        logger.info(
            f"DependencyMatcher found the following candidates: {most_probable_candidates}"
        )

        if len(most_probable_candidates) == 1:
            chosen_candidate = most_probable_candidates[0]
            new_codelets.extend(
                self.frame_matcher.set_bond(self.slot_id, chosen_candidate, self)
            )
            bonded_text = self.frame_matcher.get_form(chosen_candidate)
            log_bonding(
                logger,
                self.frame_matcher.frame,
                self.slot_id,
                chosen_candidate,
                bonded_text,
            )

        else:
            codelet_info = {
                "urgency_level": self.urgency_level + 1,
                "codelet_probability": 1,
            }
            synt_role_checker = (
                SyntRoleChecker.from_slot_frame_matcher_and_temp_modifier(
                    codelet_info,
                    self.frame_matcher,
                    self.slot_id,
                )
            )
            new_codelets.append(synt_role_checker)

        return CodeletResults(new_codelets, self.temp_modifier)

    def __str__(self):
        return f"""<{self.codelet_type}>: urgency_level={self.urgency_level}, temp_modifier={self.temp_modifier}, slot_id={self.slot_id}"""


class SyntRoleChecker(Codelet):
    @classmethod
    def from_slot_frame_matcher_and_temp_modifier(
        cls,
        codelet_info: Dict[str, Union[str, int]],
        frame_matcher: FrameMatcher,
        slot_id: int,
        temp_modifier: float = None,
    ):
        synt_role_checker = SyntRoleChecker(**codelet_info)
        synt_role_checker.frame_matcher = frame_matcher
        synt_role_checker.slot_id = slot_id
        synt_role_checker.temp_modifier = temp_modifier

        return synt_role_checker

    def run(self):
        doc = self.frame_matcher.sentence_doc
        roles = self.frame_matcher.frame.slots[self.slot_id].roles
        new_codelets = []
        highest_probability_bond = 0
        most_probable_candidates = dict()

        for candidate in self.frame_matcher.frame.slots[self.slot_id].candidates:
            for word_id in candidate:
                if doc[word_id].dep_ in roles:
                    if roles[doc[word_id].dep_] >= highest_probability_bond:
                        highest_probability_bond = roles[doc[word_id].dep_]
                        if highest_probability_bond in set(
                            most_probable_candidates.keys()
                        ):
                            most_probable_candidates[highest_probability_bond].append(
                                candidate
                            )
                        else:
                            most_probable_candidates[highest_probability_bond] = [
                                candidate
                            ]

        chosen_candidates = most_probable_candidates[highest_probability_bond]
        logger.info(
            f"SyntRoleChecker found the following candidates: {chosen_candidates}"
        )
        logger.info(f"Length of chosen_candidates: {len(chosen_candidates)}")
        self.frame_matcher.frame.slots[self.slot_id].replace_candidates(
            chosen_candidates
        )

        if len(chosen_candidates) == 1:
            new_codelets.extend(
                self.frame_matcher.set_bond(self.slot_id, chosen_candidates[0], self)
            )
            logger_frame_message = (
                f"Frame {self.frame_matcher.frame} slot {self.slot_id} bonded to "
            )
            logger_bond_message = f"{[chosen_candidates[0]]}"
            bonded_text = [
                token
                for i, token in enumerate(self.frame_matcher.sentence_doc)
                if i in chosen_candidates[0]
            ]
            logger_message = (
                f"{logger_frame_message}{logger_bond_message}: {bonded_text}"
            )
            logger.info(logger_message)
        else:
            # TODO: create meaning checker
            pass

        return CodeletResults(new_codelets, self.temp_modifier)

    def __str__(self):
        return f"""<{self.codelet_type}>: urgency_level={self.urgency_level}, temp_modifier={self.temp_modifier}, slot_id={self.slot_id}"""


class SingleCandidateChecker(Codelet):
    @classmethod
    def from_frame_matcher_and_temp_modifier(
        cls,
        codelet_info: Dict[str, Union[str, int]],
        frame_matcher: FrameMatcher,
        temp_modifier: float = None,
    ):
        single_cand_checker = SingleCandidateChecker(**codelet_info)
        single_cand_checker.frame_matcher = frame_matcher
        single_cand_checker.temp_modifier = temp_modifier

        return single_cand_checker

    def run(self):
        new_codelets = list()
        for i in range(len(self.frame_matcher.frame.slots)):
            slot = self.frame_matcher.frame.slots[i]
            if (slot.get_bond() is None) and (len(slot.candidates) == 1):
                logger.info(f"Frame {self.frame_matcher.frame}")
                logger.info(
                    f"Identified slot (slot_id={i}) with a single candidate ({slot.candidates[0]}), bonding"
                )
                new_codelets = self.frame_matcher.set_bond(i, slot.candidates[0], self)

        return CodeletResults(new_codelets, self.temp_modifier)


class FrameFinalizer(Codelet):
    @classmethod
    def from_frame_matcher_and_temp_modifier(
        cls,
        codelet_info: Dict[str, Union[str, int]],
        frame_matcher: FrameMatcher,
        temp_modifier: float = None,
    ):
        frame_finalizer = FrameFinalizer(**codelet_info)
        frame_finalizer.frame_matcher = frame_matcher
        frame_finalizer.temp_modifier = temp_modifier

        return frame_finalizer

    def run(self):
        active_frames = []
        workspace_modifiers = []

        if self.frame_matcher.frame.frame_dict.get("pattern", False) is True:
            all_bond_list = [slot.bond for slot in self.frame_matcher.frame.slots]
            bond_list = list()
            for current_bond_list in all_bond_list:
                bond_list.extend(current_bond_list)
            min_bond = min(bond_list)
            max_bond = max(bond_list)
            pattern_found = True
            for expected in range(min_bond, max_bond):
                if expected not in bond_list:
                    pattern_found = False
            if pattern_found is False:
                active_frames = [("remove", self.frame_matcher.frame)]
                logger.info(
                    f"Removing frame {self.frame_matcher.frame} from consideration"
                )

        if (self.frame_matcher.frame.frame_dict.get("pattern", False) is False) or (
            pattern_found is True
        ):
            if self.frame_matcher.frame.num_dependent_processes > 0:

                for dependent_process in self.frame_matcher.frame.dependent_processes:
                    dependent_process.assign_properties(self.frame_matcher)
                    workspace_modifiers.append(dependent_process)

                logger.info(
                    f"Found dependent processes: {self.frame_matcher.frame.num_dependent_processes}: {self.frame_matcher.frame.dependent_processes}"
                )
                logger.info(f"Workspace modifiers: {workspace_modifiers}")

        return CodeletResults(
            [], self.temp_modifier, workspace_modifiers, active_frames
        )


class ConstantChecker(Codelet):
    @classmethod
    def from_slot_frame_matcher_and_temp_modifier(
        cls,
        codelet_info: Dict[str, Union[str, int]],
        frame_matcher: FrameMatcher,
        slot_id: int,
        temp_modifier: float = None,
    ):
        constant_checker = ConstantChecker(**codelet_info)
        constant_checker.frame_matcher = frame_matcher
        constant_checker.slot_id = slot_id
        constant_checker.temp_modifier = temp_modifier

        return constant_checker

    def run(self):

        new_codelets = []
        candidate = self.frame_matcher.frame.slots[self.slot_id].candidates[0]
        bonded_text = self.frame_matcher.get_form(candidate)

        # TODO: add here a role check
        if (
            bonded_text[0].text
            in self.frame_matcher.frame.slots[self.slot_id].requirements
        ):

            resulting_codelets = self.frame_matcher.set_bond(
                self.slot_id, candidate, self
            )
            if len(resulting_codelets) > 0:
                new_codelets.extend(resulting_codelets)

            log_bonding(
                logger,
                self.frame_matcher.frame,
                self.slot_id,
                self.frame_matcher.frame.slots[self.slot_id].candidates[0],
                bonded_text,
            )

        return CodeletResults(new_codelets, self.temp_modifier)


############### Workspace modifiers ###############


@attr.s
class WorkSpaceModifier:
    def assign_workspace(self, workspace):
        self.workspace = workspace

    def assign_properties(self, *args, **kwargs):
        raise NotImplementedError("Must be implemented by the subclass")

    def __str__(self):
        return self.__class__.__name__


class ProdropModifier(WorkSpaceModifier):
    def assign_properties(self, *args, **kwargs):
        pass

    def run(self, workspace):
        active_frames = workspace.active_frames
        # Find subject slot, bond it to prodrop
        for priority_group in active_frames.frame_priority_groups.keys():
            frame_list = active_frames.frame_priority_groups[priority_group]
            for frame in frame_list:
                for slot_id, slot in enumerate(frame.slots):
                    if "nsubj" in slot.roles:
                        candidate = "PRODROP"
                        form = ""
                        if frame.get_bond(slot_id) is None:
                            frame.set_bond(slot_id, candidate)
                            frame.set_form(slot_id, form)
                            logger.info(
                                f"Assigned PRODROP to slot={slot_id} of the frame {str(frame)}"
                            )


@attr.s
class NPCreator(WorkSpaceModifier):
    np = attr.ib(
        type=List[int],
        validator=validators.optional(validators.instance_of(List)),
        init=False,
    )

    def assign_properties(self, frame_matcher: FrameMatcher):
        text = frame_matcher.sentence_doc.text
        token_list = list(frame_matcher.frame.get_all_bonded())
        sentence, np, tokens = database.create_noun_phrase(config.nlp, text, token_list)
        self.np = np

    def run(self, workspace):
        for np_chunk in config.session.query(database.NounPhrase):
            if np_chunk in self.np:
                workspace.remove_np(np_chunk)
                if self.np not in workspace.noun_phrases:
                    workspace.add_np(self.np)
        logger.info(f"Current noun phrases: {workspace.noun_phrases}")
