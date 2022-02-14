# TODO
Ordered by priority

Make a test for SyntRoleChecker to create BondChecker DONE 2022-02-07
Move modification of temp_modifiers to CodeletResults DONE 2022-02-07
Create SingleCandidate Checker - run if not bonded items with 

# TODO: if something in a frame bonded, raise all not bonded  codelets - part of set_bond
            # for this frame 1 up in urgency level
            not_bonded_slot_ids = [
                slot_id
                for slot_id, slot in enumerate(self.frame_matcher.frame.slots)
                if slot.bond is not None
            ]

# TODO create semantic vector checker as a separate codelet - meaning checker

Create new codelet: takes everything if something has more than one candidate, checks if any of the candidates 
has been bonded, removes them

Remove NounPhrase class and its test
Rename SentenceNunPhraseNew class to NounPhrase

Fix running frames in the correct order - now initialized all at once DONE 2021-01-17
Fix DependencyChecker logging, does not report new codelets

Fix workspace run_one_priority_new_active_frames test - not bonding  DONE 2021-01-10
Divide constant and variable Slot Matchers
Make absolute order check a function move out of SlotMatcher
Both SlotMatcher and Constant Checker now create a new frame - figure out which one needs to do it and only leave creation of the new frame there
Fix test for workspace for processing a new active frame - currently does not add a new frame
When ConstantChecker creates a new frame, it needs to be added to active_frames
Run and see if "some" and "everyone" got individual frames
Find out why frames with priority 1 are not processed first
Make the SlotMatcher that needs NP  to chose from workspace noun_phrases

If something in a frame bonded, raise all not bonded  codelets for this frame 1 up in urgency level
Add a role checker within Constant Checker
Figure out circular import in codelets WorkSpaceModifier
Find why non-required slots receive slotmatchers - think if maybe they shoudl only be created if their initializer is found
Make Constant Checker to check roles # and self.frame_matcher.sentence_doc[i].dep_ in self.slot.roles
Make all NP chunks my NounPhrases at creation DONE 2021-11-18
Fix failing test DONE - incorrect initialization 2021-11-01
Move workspace_modifiers to codelets? DONE 2021-11-04
Make assign_properties function for WorkSpaceModifiers - make it realized by subclass -- DONE 2021-11-03
Test NPCreator - fix the failing test DONE 2021-11-05

# Workspace modifiers
1. NPCreator
2. Active Frames - add groups: frames that affect "noun chunks", frames that have dependent processes - current DONE 2021-10-19
3. Add priorities to groups ONE 2021-10-19
4. In workspace run them in order of priorities

# Linguistics
1. Fix add_np functionality of workspace DONE 2022-02-04
2. Fix noun phrases assignment DONE 2022-02-04
3. Make noun chunks written in a database DONE 2022-02-04
4. Modify slot matcher to get NPs from the database DONE 2022-02-04
5. Replace "optional" with "required": variants : required, optional, conditionally required DONE 2021-10-15
6. Fix noun chunks, they need to contain "they", "some" without dependency
7. In case of "some of NP" the whole thing should be a noun chunk
8. This needs to happen before slotmatcher works, because it depends on noun chunks
9. Add a quantifier rule, by which things like "some of NP", "all of NP", etc. will be added to noun chunks - do that as quantifier construction!

# Frame
1. if an optional slot is found then slots_to_find number increases by all its dependents, and they get a slot matcher
2. By default dependent slots do not get a slot matcher

## Tests
1. Test workspace add_np
2. Test FrameFinalizer
3. Add checking that a frame without dependent_process has num_dependent_processes == 0

## Codelets
1. Extra Constant Checker - count "slot 1 bonded to [[4]]: [of]" in the log DONE 2022-01-11
2. FrameFinalizers are not created - fix DONE-2022-01-11
3. Create a test for ConstantChecker that it creates a FrameFinalizer DONE 2022-01-12
4. Think about coderack previously importing codelets to provide type of list to urgency bin, 
removed due to circular import, seems like not the best decision - make a tree of module imports and 
consider it 
5. Figure out how not to make a copy of the same code for FrameFinalizer DONE 2021-10-08
6. Process slots in frame storage ??
7. Process relative order before bonding
8. Process cases with two constants, like 'The more the merrier', based on linear order
9. If something in a frame bonded, raise all not bonded codelets
10. Slot matcher: Save probability associated with role, provide it as a probability of the candidate
11. Add slot_id to ConstantChecker.str
12. Slot codelet: think about abstracting SlotCodelet and move similar functionality there


## Tests
2. Make the nlp fixture in conftest into a small testing NLP

## Improvements
1. Figure out if candidates are removed if they are no longer considered, if no, make that happen
2. Add a frane with optional slots, add test for FrameMtacher.chekc_if_done for optional slots

## Attr
1. Add attrs to Workspace

<!--- ## DEBUG 
## Documentation 
## Frame storage --->

# Done
In alphabetical order of groups, within each group order by date of done, descending


## DEBUG
1. Find out why animate NP slot bonds to [10] and not to [3, 4, 5, 6, 7, 8] DONE 2022-02-05
2. Fix workspace run_one_priority test - not bonding DONE 2021-12-25
3. Find out why constant checker cannot find "some" DONE 2021-12-08
4. Fix failing tests - DONE 2021-10-14
5. Find out why to-sentence is getting "some" as form for dobj - I added DET to noun chunks and dobj is correct synt role for this role DONE 2021-10-1 
6. Find why DependencyMatcher bonded slot 4 to [[10]]: [the] DONE 20121-10-10
7. Find out why in "some of the most wonderful gifts" "some" and "the most wonderful gifts" are treated separately DONE 2021-10-10
8. Find out why to-sentence is getting None for animate dative DONE 2021-10-10
9. Finish dealing with FrameFinalizer, fix tests and get to a running program DONE 2021-10-09
10. ConstantChecker - codelets: does not bond DONE 2021-07-26
11. Debug Prodrop Modifier DONE 2021-08-07
12. Debug FrameFinalizer DONE 2021-08-07

## Active frames
1. Initialize all currently present constructions, delete initialization from constant DONE 2021-07

## Codelets
1. For each constant found create a constant checker with one candidate - this should result in two FrameMatchers DONE 2021-12-17 
2. Assign candidate as candidate for the constant slot DONE 2021-12-17
3. Figure out how not to make a copy of the same code for FrameFinalizer DONE 2021-10-08
4. Figure out how to process DependentProcesses DONE 2021-10-07
5. Process absolute order requirements at slot matcher - Active SlotMatcher DONE 2021-07-31
6. Process list as constant requirements, change everywhere DONE 2021-07-31 
7. Make frame finalizer into a checking function on FrameMatcher, run after every bond DONE 2021-10-01
8. Remove FrameFinalizer, do not create it from places where it is currently created DONE 2021-10-06
9. Create number of required slots and do =-1 on every bond - that would be less processing DONE 2021-10-05

## Frames
1. Separate "everyone" and "everyone of them" into different frames DONE 2021-01-06
2. Produce copy for frames DONE 2021-12-16
3. Add imperative frame DONE 2021-08
4. Add rule that subject can be not present if imperative is found DONE 2021-08
5. Make frame.reduce_required_slots_to_find DONE 2021-10-05
6. Remove required_slots_to_find from FrameMatcher and its tests DONE 2021-10-05

## Frame storage
1. Add linear order to frame_storage - in what order slots should appear if that is important DONE

## Logging
1. At the beginning print all tokens of the sentence with pos_, head, and dep_  DONE 2021-07-21

## POS
1. Explore NLTK POS tagger, see if it is doing better than `spacy` DONE 2021-07-29
2. Add determiner conversion processing: in case a determiner "this" or "that" is not followed by a noun chunk, 
add that to noun chunks DONE 2021-07-29

## Processing form
1. Make set bond function with adding form DONE 2021-07-21

## Tests
1. Fix remove_np functionality of workspace DONE 2022-01-28
2. Fix workspace tests - DONE 2022-01-24
3. Add pattern finding to FrameFinalizer DONE 2022-01-07
4. Add pattern finding to FrameFinalizer test DONE 2022-01-09
5. Process removing frames in workspace - DONE 2022-01-02
6. Fix Workspace tests - DONE 2022-01-05
7. Test remove frame in active frames - DONE 2021-01-02
8. Finish Treating Constant Checker - clean up and fix tests DONE 2021-12-23 
9. Fix SlotMatcher complex constant test DONE 2021-12-23
10. Make tests for workspace - see stubs DONE 2012-11-18
11. Make test_workspace_modifiers dependent of conftest for frame dicts DONE 2012-10-23
12. Tests for active frames - DONE 2021-08-15
13. Test for coderack - DONE 2021-08-15
14. Tests for frame  - DONE 2021-08-29
15. Test for workspace modifiers - DONE 2021-08-30
16. Tests for workspace - DONE 2021-09-05
17. Remove DATIVE_FRAME and IMPERATIVE_FRAME from test_frame, replace them with fixtures in conftest DONE 2021-09-18
18. Tests for codelets DONE 2021-09-27
19. Figure out how to nicely mute logging for all testing DONE 2021-09-28

# Workspace
1. Test changes in workspace DONE 2021-10-23
2. After the run of DependencyMatcher FrameFinalizer is created, while it should not be - find why why  DONE 2021-12-26

## Workspace modifieres
1. Make prodrop a workspace modifier DONE 2021-08-07
2. Process dependent_processes in frame storage - make finalizer start them  DONE 2021-08