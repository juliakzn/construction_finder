import logging
from typing import List

from construction_finder import (active_frames, codelets, coderack, config,
                                 database, frame, frame_storage)

logger = logging.getLogger(f"{__name__}")


# TODO: add attr and list all attributes for the class
class WorkSpace:
    @classmethod
    def from_nlp_and_txt(cls, nlp, txt):

        work_space = WorkSpace()
        work_space.nlp = nlp
        work_space.txt = txt
        work_space.doc = nlp(txt)
        logger.info(f"Analyzing sentence: {txt}")

        work_space.noun_phrases: List[database.NounPhrase] = list()
        work_space.find_np_phrases()

        work_space.coderack = coderack.CodeRack()
        logger.info(f"Created a new coderack: {work_space.coderack}")

        work_space.active_frames = (
            active_frames.ActiveFrames.from_frame_priority_groups()
        )
        work_space.temperature = config.STARTING_TEMPERATURE

        logger.info("Looking for potential frames")
        work_space.find_frames(frame_storage.FRAMES)
        logger.info("All potential frames identified\n_____________________\n")

        return work_space

    def find_frames(self, frames):
        logger.info("Tokens:")
        for token in self.doc:
            logger.info(
                f"Token {token.i}: {token.text}: POS: {token.pos_}, TAG: {token.tag_}, MORPH: {token.morph}, HEAD: {token.head}, SyntRole: {token.dep_}"
            )
        logger.info(f"Noun chunks: {[chunk for chunk in self.doc.noun_chunks]}")

        for frame_dict in frames:
            if frame_dict:
                initialized_frame = frame.Frame.from_frame_dict(frame_dict)
                if hasattr(initialized_frame, "dependent_processes"):
                    for dependent_process in initialized_frame.dependent_processes:
                        dependent_process.assign_workspace(workspace=self)
                self.active_frames.append_frame(
                    initialized_frame, initialized_frame.priority
                )

        logger.info(
            f"Workspace initialized the following active frames: \n{self.active_frames}"
        )

    def initialize_frames(self, frames, temperature_per_priority_group):
        new_codelets = list()
        for initialized_frame in frames:
            codelet_info = {"urgency_level": 1, "codelet_probability": 1}
            frame_matcher = codelets.FrameMatcher.from_frame_and_sentence(
                codelet_info, initialized_frame, self.doc
            )
            frame_matcher.urgency_level = 1
            new_codelets.append(frame_matcher)

        # Adjust temperature modifiers based on the number of frames to match
        n = len(new_codelets)

        for new_codelet in new_codelets:
            new_codelet.temp_modifier = temperature_per_priority_group / float(n)

            if hasattr(new_codelet.frame, "dependent_processes"):
                for dependent_process in new_codelet.frame.dependent_processes:
                    dependent_process.assign_workspace(self)

            self.coderack.add_codelet(new_codelet)

    def run(self):
        priorities = list(self.active_frames.frame_priority_groups.keys())
        priorities.sort()
        temperature_per_priority_group = config.STARTING_TEMPERATURE / len(priorities)
        for priority in priorities:
            self.run_one_priority(priority, temperature_per_priority_group)
        return self.active_frames

    def run_one_priority(self, priority, temperature_per_priority_group):
        priority_frames = self.active_frames.frame_priority_groups[priority]
        self.initialize_frames(priority_frames, temperature_per_priority_group)
        while not self.coderack.empty():
            logger.info("Starting a new workspace epoch")
            for k, v in self.coderack.urgency_bins.items():
                for c in v:
                    logger.info(f"In the coderack: {c}")
            spin_result = self.coderack.spin_codelet()
            logger.info(
                f"Received the following results from the codelet: {str(spin_result)}"
            )

            self.temperature -= spin_result.temp_modifier
            logger.info(
                f"Current workspace temperature is: {self.temperature}\n_____________________\n"
            )

            if spin_result.workspace_modifiers is not None:
                for workspace_modifier in spin_result.workspace_modifiers:
                    workspace_modifier.run(self)
                logger.info(
                    f"Activated workspace modifiers processes: {spin_result.workspace_modifiers}"
                )

            if spin_result.new_active_frames is not None:
                for append_or_remove, new_active_frame in spin_result.new_active_frames:
                    if append_or_remove == "append":
                        self.active_frames.append_frame(new_active_frame)
                        logger.info(f"Added active frame: {str(new_active_frame)}")
                    elif append_or_remove == "remove":
                        self.active_frames.remove_frame(new_active_frame)
                        logger.info(f"Removed active frame: {str(new_active_frame)}")

    def add_np(self, np):
        config.session.add_all([np])
        config.session.commit()

    def remove_np(self, np):
        config.session.query(database.NounPhrase).filter(
            database.NounPhrase.np_id == np.np_id
        ).delete()
        config.session.query(database.NounPhraseTokens).filter(
            database.NounPhraseTokens.token_id.in_(
                [token.token_id for token in np.tokens]
            )
        ).delete()
        if config.session.query(database.Sentence.noun_phrases).filter(
            database.Sentence.sentence_id == np.sentence_host.sentence_id
        ):
            config.session.query(database.Sentence).filter(
                database.Sentence.sentence_id == np.sentence_host.sentence_id
            ).delete()
        config.session.commit()

    def find_np_phrases(self):
        for np in self.doc.noun_chunks:
            token_list = list(range(np.start, np.end))
            sentence, np, tokens = database.create_noun_phrase(
                self.nlp, self.doc.text, token_list
            )
            config.session.add_all([sentence, np] + tokens)

        # Add all 'DET' in order to correctly process pronouns such as 'that' in 'Don't give me that',
        # which are classified as 'DET'
        dets = [token.i for token in self.doc if (token.pos_ == "DET")]
        for det in dets:
            sentence, np, tokens = database.create_noun_phrase(
                self.nlp, self.doc.text, [det]
            )
            config.session.add_all([sentence, np] + tokens)

        config.session.commit()
