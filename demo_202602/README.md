
1. Segment transitions need to be verified.
2. Make a score control that resets the score follower based on the `demo_202602.cur_seg_idx`
   This will remove that responsibility from main (demo_202602) controller.
   
   
   

(multi-player: containing all segments (recorded,score-based,Scriabin)

score-follower

ctl: chooses the next player based on SF location 
  

1. Generate a score for all material.
2. Generate a multi-player file for all possible segments.
3. Create new controller to handle segment switching.



1. implement 'reset'
2. implement 'start'
3. implement start-next on 'end-loc'.
4. add gutim_spirio control to delay the starting of the next segment.



5/2026
=======

1. Add a sub-directory of preset files to 'io' directory. 
2. Each file has the form:
```
                           Post      Use    Uniform Prefer Per   Allow  Pref.  
Segment name  Perf name    Delay ms  Prob   Prob    Dry    Note  All    Dry.   
------------ ------------- --------  -----  ------- ----- ------ ------ -----
gutim_1      nicolas2-3          -1  true    false  true  false  true   true
```
3. Add UI controls to `demo202602`

-  Drop down menu to select a preset file.
- 'Reload' button to reload the current preset.

4. Add a `delay_ms` input to `end_seg_detector` which will delay prior to starting
next segment.

5. Add a new port `on_play_id` which is called when a new segment begins playing.
This will issue `gutim_ps` with new parameters.

6. 




- overall setup presets to control
  + sequence selection: given as a list to `demo_202602_ctl`
  + sequence transition delays  add to `end_seg_dector: (cur_player_id, next_player_id, delay_ms)`
  + xform selection parameters: `player_id -> (prob_fl,uniform_fl,allow_all_fl,per_note_fl)`

1. Add sequence presets to `demo_202602_ctl`
```
{ preset_name:[ <seq_1>,<seq_2>,<seq_3> ...] }
```
This will show up as a drop down on the `demo_202602_ctl` control.

1. 

2. Add a the ability to set a delay from the `end_seq_detector` UI.
This delay can be global - but use it to determine required delays between
specific segments.

3. Add a 'delay' input to the `end_seg_detector` to give a delay between the current `seg_id_in` and 
the resulting `play_id_in`.

4. Add a segment based proc which emits changes to `gutim_ps` when a particular
segment begins playing.




End Segment Processing:
=======================

1. Verify that each performed segment ends with the expected notes.
2. Verify that each performed segment begins with a note-on at time zero.
3. If there is a rest at the segment boundary then a delay must be inserted, 
   otherwise the subsequent segments should play immediately upon the end-seg-detector triggering.
   
   
   
TODO: 05/09/2026   
================
- DONE: Fix the score follower. Score follower will now not search outside the reset beg/end loc's.
- What does 'Xform Enable' in the preset file actually enable?
- DONE: Fix section transition:   
  + The delay should be from the last loc to the first loc in the next measure.
  + This is accomplished by setting a 'Post Delay' in the preset file and also setting 'release_fl' to false in `end_seg_detect.cfg`.
  
- Remove or make Scriabin optional.
- Scriabin passages are not using the correct velocity tables.
- Create a velocity table for performed sequences - maybe by interpolating the 'spirio_1' velocity table used by the score?
- Add igain to preset. 
  + Consider setting igain per-note by setting the 'g' value from ps-gutim.
- Consider a button to automatically generate a duplicated preset text file.
- Pedal on spirio sections - or at least the first Spirio section.
 
