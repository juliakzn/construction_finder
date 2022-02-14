import copy

import pytest

from construction_finder import active_frames, codelets, frame

PRIORITY_GROUP = 2


@pytest.fixture
def prodrop_modifier():
    return codelets.ProdropModifier()


@pytest.fixture
def active_frames_object(to_frame_dict, dative_frame_dict):
    frame1 = frame.Frame.from_frame_dict(to_frame_dict)
    frame2 = frame.Frame.from_frame_dict(dative_frame_dict)
    active_frames_object = active_frames.ActiveFrames.from_frame_priority_groups(
        {PRIORITY_GROUP: [frame1, frame2]}
    )

    return active_frames_object


@pytest.fixture
def mock_workspace(active_frames_object):
    class MockWorkSpace:
        def __init__(self, active_frames):
            self.active_frames = active_frames

    return MockWorkSpace(active_frames_object)


class TestProdropModifier:
    def test_run(self, active_frames_object, prodrop_modifier, mock_workspace):
        expected = copy.deepcopy(active_frames_object)
        prodrop_modifier.run(mock_workspace)

        for i, j in [(0, 2), (1, 1)]:
            expected.frame_priority_groups[PRIORITY_GROUP][i].slots[j].set_bond(
                "PRODROP"
            )
            expected.frame_priority_groups[PRIORITY_GROUP][i].slots[j].set_form("")
            assert (
                active_frames_object.frame_priority_groups[PRIORITY_GROUP][i]
                .slots[j]
                .bond
                == expected.frame_priority_groups[PRIORITY_GROUP][i].slots[j].bond
            )
            assert (
                active_frames_object.frame_priority_groups[PRIORITY_GROUP][i]
                .slots[j]
                .form
                == expected.frame_priority_groups[PRIORITY_GROUP][i].slots[j].form
            )
