from typing import List

from construction_finder import codelets


class FrameSlot:
    @classmethod
    def from_slot_dict(cls, slot_dict):
        frame_slot = FrameSlot()
        frame_slot.__dict__.update(**slot_dict)
        frame_slot.candidates = []
        frame_slot.bond = None

        return frame_slot

    def set_bond(self, candidate):
        self.bond = candidate

    def get_bond(self):
        return self.bond

    def set_form(self, form):
        self.form = form

    def add_candidate(self, candidate):
        self.candidates.append(candidate)

    def extend_candidates(self, candidate_list):
        self.candidates.extend(candidate_list)

    def remove_candidate(self, candidate):
        self.candidates.remove(candidate)

    def replace_candidates(self, candidate_list):
        self.candidates = candidate_list


class Frame:
    @classmethod
    def from_frame_dict(cls, frame_dict):
        frame = Frame()
        frame.frame_dict = frame_dict
        frame.slots = []
        # Candidate for deletion if not found useful until Nov 13
        # frame.required_slots_to_find = len([slot for slot in frame.slots if slot.optional == False])
        frame.all_required_slots_found = False

        # Candidate for deletion, if not found useful until Nov 4, 2021
        # frame.matcher = None
        frame.priority = frame_dict["priority"]
        frame.pattern = frame_dict.get("pattern", False)
        slot_dict = frame_dict["slots"]
        for key in slot_dict.keys():
            frame.slots.append(FrameSlot.from_slot_dict(slot_dict[key]))
        frame.required_slots_to_find = len(
            [slot for slot in frame.slots if slot.requirement_type == "required"]
        )

        frame.num_dependent_processes = 0
        if "dependent_processes" in frame_dict:
            frame.dependent_processes = []
            for dependent_process_name in frame_dict["dependent_processes"]:
                dependent_process_class = getattr(codelets, dependent_process_name)
                dependent_process = dependent_process_class()
                frame.dependent_processes.append(dependent_process)
            frame.num_dependent_processes = len(frame.dependent_processes)

        return frame

    def set_bond(self, slot_id, candidate):
        self.slots[slot_id].set_bond(candidate)

    def get_bond(self, slot_id):
        return self.slots[slot_id].get_bond()

    def set_form(self, slot_id, form):
        self.slots[slot_id].set_form(form)

    def set_all_required_slots_found(self):
        self.all_required_slots_found = True

    def get_all_required_slots_found(self):
        return self.all_required_slots_found

    def reduce_required_slots_to_find(self, number_of_slots: int = 1):
        self.required_slots_to_find -= number_of_slots

    def get_all_bonded(self):
        return set().union(*[slot.bond for slot in self.slots if slot.bond is not None])

    def copy(self):
        return Frame.from_frame_dict(self.frame_dict)

    def __str__(self):
        frame_str = ""
        for key, value in self.__dict__.items():
            if isinstance(value, List):
                for item in value:
                    if isinstance(item, FrameSlot):
                        frame_str += str(item.__dict__) + ", \n"
                    elif isinstance(item, codelets.WorkSpaceModifier):
                        frame_str += f"({str(key)}, {str(item)})" + ", \n"
                    else:
                        frame_str += f"({str(key)}, {str(value)})"
        return frame_str
