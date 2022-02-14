import logging
from typing import Any, Dict, List

import attr
from attr import validators

logger = logging.getLogger(f"{__name__}")


@attr.s
class ActiveFrames:
    frame_priority_groups = attr.ib(
        type=Dict[int, List[Any]],
        validator=validators.instance_of(Dict),
        default=dict(),
    )

    @classmethod
    def from_frame_priority_groups(cls, frame_priority_groups=None):
        if frame_priority_groups is None:
            frame_priority_groups: Dict = {}

        return ActiveFrames(frame_priority_groups)

    def append_frame(self, frame, priority_group):
        if priority_group in self.frame_priority_groups.keys():
            self.frame_priority_groups[priority_group].append(frame)
        else:
            self.frame_priority_groups[priority_group] = [frame]

    def remove_frame(self, frame, priority_group):
        self.frame_priority_groups[priority_group].remove(frame)

    def __len__(self):
        active_frames_length = 0
        for priority_group in self.frame_priority_groups.keys():
            active_frames_length += len(self.frame_priority_groups[priority_group])
        return active_frames_length

    def __str__(self):
        frame_list = list()
        for i, frame_group in self.frame_priority_groups.items():
            for j, frame in enumerate(frame_group):
                frame_list.append(f"Frame {i}-{j}:\n{str(frame)}")
        return ",".join(frame_list)
