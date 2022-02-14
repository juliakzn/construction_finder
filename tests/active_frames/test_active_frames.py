from construction_finder import active_frames


def test_active_frames_class():
    test_frame = "TEST FRAME 1"
    test_frame_groups = {0: [test_frame]}
    active_frames_exemplar = active_frames.ActiveFrames.from_frame_priority_groups(
        frame_priority_groups=test_frame_groups
    )
    active_frames_exemplar.append_frame("TEST FRAME 2", 1)

    assert active_frames_exemplar.frame_priority_groups == {
        0: ["TEST FRAME 1"],
        1: ["TEST FRAME 2"],
    }

    assert len(active_frames_exemplar) == 2
    assert str(active_frames_exemplar) == (
        """Frame 0-0:
TEST FRAME 1,Frame 1-0:
TEST FRAME 2"""
    )

    active_frames_exemplar.remove_frame("TEST FRAME 2", 1)
    assert active_frames_exemplar.frame_priority_groups == {0: ["TEST FRAME 1"], 1: []}
    assert len(active_frames_exemplar) == 1

    assert str(active_frames_exemplar) == (
        """Frame 0-0:
TEST FRAME 1"""
    )
