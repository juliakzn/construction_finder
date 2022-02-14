import logging
import random
from typing import Dict, List, Tuple, Union

from construction_finder import codelets, frame

logger = logging.getLogger(f"{__name__}")


class SpinResult:
    def __init__(
        self,
        temp_modifier: float,
        workspace_modifiers: Union[List[codelets.WorkSpaceModifier], None] = None,
        new_active_frames: Union[Tuple[str, frame.Frame], None] = None,
    ):
        self.temp_modifier = temp_modifier
        self.workspace_modifiers = workspace_modifiers
        self.new_active_frames = new_active_frames

    def __str__(self):
        return f"""<SpinResult>: temp_modifier={self.temp_modifier}, workspace_modifiers={self.workspace_modifiers}"""


class CodeRack:
    def __init__(self, urgency_levels: List = [1, 2, 3, 4, 5]):
        self.urgency_levels = urgency_levels
        self.urgency_bins: Dict = dict()

        for urgency_level in urgency_levels:
            self.urgency_bins[urgency_level]: List = []

    def add_codelet(self, codelet):
        urgency_level = min(codelet.urgency_level, max(self.urgency_levels))
        self.urgency_bins[urgency_level].append(codelet)

    def assess_urgency(self):
        urgency = list()
        for urgency_level in self.urgency_levels:
            n = len(self.urgency_bins[urgency_level])
            urgency.extend([urgency_level] * n * urgency_level)
        return urgency

    def empty(self):
        total_codelets = 0
        for urgency_level in self.urgency_levels:
            n = len(self.urgency_bins[urgency_level])
            total_codelets += n
        return total_codelets == 0

    def __contains__(self, codelet):
        result = False
        for urgency_level in self.urgency_levels:
            if codelet in self.urgency_bins[urgency_level]:
                result = True
        return result

    def spin_codelet(self):
        logger.info("Spinning a new codelet")
        urgency = self.assess_urgency()
        logger.info(f"Current urgency = {urgency}")
        workspace_modifiers = None
        new_active_frames = None

        if len(urgency) > 0:
            chosen_bin = random.choice(urgency)
            random_codelet_index = random.randint(
                0, len(self.urgency_bins[chosen_bin]) - 1
            )
            chosen_codelet = self.urgency_bins[chosen_bin].pop(random_codelet_index)
            logger.info(f"Chose codelet {chosen_codelet} from urgency bin {chosen_bin}")

            codelet_result = chosen_codelet.run()
            temp_modifier = codelet_result.temp_modifier

            for new_codelet in codelet_result.new_codelets:
                self.add_codelet(new_codelet)

            if hasattr(codelet_result, "workspace_modifiers"):
                workspace_modifiers = codelet_result.workspace_modifiers
            if hasattr(codelet_result, "new_active_codelets"):
                new_active_frames = codelet_result.new_active_frames
        else:
            temp_modifier = 0

        return SpinResult(temp_modifier, workspace_modifiers, new_active_frames)
