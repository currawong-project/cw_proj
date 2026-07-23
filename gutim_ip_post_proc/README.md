


Post processing on the 'am' files generated from `audio_midi_record` 
----------------------------------------------------------------------
1. Record session into `~/temp/arseniy`

2. Run `~/src/libcw/build/debug/bin/cli ~/src/cw_proj/gutim_ip_post_proc/cli.cfg am_to_midi_file`
   Generates `midi_am.mid` and `midi_am.csv` from `midi.am` in `~/temp/arseniy/record_*/`.
   
  
3. Run `~/src/libcw/build/debug/bin/cli ~/src/cw_proj/gutim_ip_post_proc/cli.cfg midifile`
   Specify take numbers to include in the conversion.
   Runs `batch_convert` to create `midi_am_sf.csv` in each directory.

4. The `midi_am_sf.csv` files can also be run against the C++ score follower with `~/src/cw_proj/gutim_ip_post_proc/cli.cfg sf2`




