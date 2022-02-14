import inspect

from construction_finder import codelets


class TestFrame:
    def test_from_frame_dict(self, imperative_frame, imperative_frame_dict):
        for i in range(2):
            for k in imperative_frame_dict["slots"][i]:
                assert hasattr(imperative_frame.slots[i], k)
                assert (
                    getattr(imperative_frame.slots[i], k)
                    == imperative_frame_dict["slots"][i][k]
                )
        assert imperative_frame.num_dependent_processes == 1
        print(imperative_frame.dependent_processes)
        assert isinstance(
            imperative_frame.dependent_processes[0], codelets.ProdropModifier
        )
        assert imperative_frame.required_slots_to_find == 2
        assert imperative_frame.all_required_slots_found == False
        assert imperative_frame.priority == 3
        assert imperative_frame.pattern == False

    def test_from_frame_dict_pattern(self, distributive_frame, distributive_frame_dict):
        for i in range(2):
            for k in distributive_frame_dict["slots"][i]:
                assert hasattr(distributive_frame.slots[i], k)
                assert (
                    getattr(distributive_frame.slots[i], k)
                    == distributive_frame_dict["slots"][i][k]
                )
        assert distributive_frame.num_dependent_processes == 1
        print(distributive_frame.dependent_processes)
        assert isinstance(distributive_frame.dependent_processes[0], codelets.NPCreator)
        assert distributive_frame.required_slots_to_find == 3
        assert distributive_frame.all_required_slots_found == False
        assert distributive_frame.priority == 1
        assert distributive_frame.pattern == True

    def test_set_bond(self, imperative_frame):
        imperative_frame.set_bond(0, [1, 2])
        assert imperative_frame.slots[0].bond == [1, 2]

    def test_get_bond(self, imperative_frame):
        imperative_frame.set_bond(0, [1, 2])
        output = imperative_frame.get_bond(0)
        assert output == [1, 2]

    def test_set_form(self, imperative_frame):
        imperative_frame.set_form(0, "TEST FORM")
        assert imperative_frame.slots[0].form == "TEST FORM"

    def test_set_all_required_slots_found(self, imperative_frame):
        assert imperative_frame.all_required_slots_found == False
        imperative_frame.set_all_required_slots_found()
        assert imperative_frame.all_required_slots_found == True

    def test_reduce_required_slots_to_find(self, dative_frame):
        dative_frame.reduce_required_slots_to_find()
        assert dative_frame.required_slots_to_find == 3

        dative_frame.reduce_required_slots_to_find(2)
        assert dative_frame.required_slots_to_find == 1

    def test_get_all_required_slots_found(self, imperative_frame):
        output = imperative_frame.get_all_required_slots_found()
        assert output == False

        imperative_frame.set_all_required_slots_found()
        output = imperative_frame.get_all_required_slots_found()
        assert output == True

    def test_get_all_bonded(self, imperative_frame):
        imperative_frame.set_bond(0, [1, 2])
        output = imperative_frame.get_all_bonded()
        assert output == {1, 2}
        imperative_frame.set_bond(1, [1, 2])
        output = imperative_frame.get_all_bonded()
        assert output == {1, 2}

    def test_copy(self, imperative_frame):
        output = imperative_frame.copy()
        for i in inspect.getmembers(imperative_frame):
            # To remove private and protected functions
            if not i[0].startswith("_"):
                # To remove other methods that do not start with a underscore
                if not inspect.ismethod(i[1]):
                    assert hasattr(output, i[0])

    def test_str(self, imperative_frame):
        imperative_frame.set_bond(0, [1, 2])
        imperative_frame.set_form(0, "TEST FORM")
        output = str(imperative_frame)
        expected = (
            "{'variable_or_constant': 'variable', 'synt_type': 'VERB', 'roles': {'ROOT': "
            + "1}, 'head': None, 'requirements': 'vector', 'form': 'TEST FORM', "
            + "'absolute_order': 0, 'requirement_type': 'required', 'candidates': [], 'bond': [1, 2]}, \n"
            + "{'variable_or_constant': 'constant', 'synt_type': 'PUNCT', 'roles': "
            + "{'punct': 0.9}, 'head': 0, 'requirements': ['.', '!'], 'form': '', "
            + "'absolute_order': -1, 'requirement_type': 'required', 'candidates': [], 'bond': None}, \n"
            + "(dependent_processes, ProdropModifier), \n"
        )
        assert expected == output
