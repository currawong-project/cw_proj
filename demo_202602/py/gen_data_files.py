import os
import csv
import json
import types

import midi

RECORDED_PORT_ID = 0  # GUTIM - recorded
SCORE_PORT_ID    = 1  # GUTIM - score
SCRIABIN_PORT_ID = 2  # Scriabin - score

def parse_score(ifname):

    def _proc_recd(r):
        typL = [('opcode','s'),('meas','i'),('index','i'),('voice','i'),('loc','i'),('eloc','i'),('oloc','i'),('tick','i'),('sec','f'),('dur','f'),('rval','f'),('dots','i'),('sci_pitch','s'),('dmark','s'),('dlevel','i'),('status','i'),('d0','i'),('d1','i'),('bar','i'),('section','i'),('bpm','i'),('grace','s'),('tie','s'),('onset','s'),('pedal','s'),('dyn','s'),('even','s'),('tempo','s'),('player_id','i'),('piano_id','i'),('src','s'),('seg_label','s'),('spirio_label','s'),('uid','i')]

        for field,typ in typL:
            r[field] = r[field].strip()
            if len(r[field])==0:
                r[field] = None
            else:
                r[field] = ({ 'i':lambda x:int(x),'f':lambda x:float(x),'s':lambda x:x}[typ])(r[field])

        return r

    scoreL = []
    with open(ifname,'r') as f:
        scoreL = [ _proc_recd(r) for r in csv.DictReader(f) ]

    return scoreL



def parse_midi_file(fname):
    
    def _proc_recd(r):
        typL= [('UID','i'),('trk','i'),('dtick','i'),('atick','i'),('amicro','i'),('type','s'),('ch','i'),('D0','i'),('D1','i'),('sci_pitch','s')]

        for field,typ in typL:
            r[field] = r[field].strip()
            if len(r[field])==0:
                r[field] = None
            else:
                if field == 'D0' and r[field]=='bpm':
                    continue

                r[field] = ({ 'i':lambda x:int(x),'f':lambda x:float(x),'s':lambda x:x}[typ])(r[field])

        return r


    with open(fname) as f:
        midiL = [ _proc_recd(r) for r in csv.DictReader(f) ]

    return midiL


def insert_scriabin( i_score_fname, scriabinD, o_score_fname ):

    def _insert_scriabin( scriabinD, scoreL ):
       

        def _transform_midi(midiL, src, player_id, piano_id, seg_label, ifn):

            def _set_dur_secs( midiL ):

                def _calc_dur_secs(midiL,sec0,idx,pitch):
                    m = next((r for r in midiL[idx:] if midi.is_note_off(r) and r['d0'] == pitch),None)

                    assert m['sec'] >= sec0
                    
                    return m['sec'] - sec0
                
                for i,r in enumerate(midiL):
                    if midi.is_note_on(r):
                        r['dur'] = _calc_dur_secs(midiL,r['sec'],i+1,r['d0'])
                        
                return midiL

            status_map = { 'non':midi.const.noteOnSt, 'nof':midi.const.noteOffSt, 'ped':midi.const.ctlSt, 'ctl':midi.const.ctlSt }
            op_map     = { 'non':'non', 'nof':'nof', 'ped':'ctl', 'ctl':'ctl' }
            outL  = []
            for m in midiL:
                if m['type'] in op_map:
                    outL.append( dict(
                             opcode    = op_map[ m['type'] ],
                             tick      = m['dtick'],
                             sec       = float(m['amicro']) / 1000000.0,
                             dur       = 0,
                             oloc      = None,
                             sci_pitch = m['sci_pitch'],
                             status    = status_map[ m['type'] ],
                             d0        = m['D0'],
                             d1        = m['D1'],
                             src       = src,
                             piano_id  = piano_id,
                             player_id = player_id,
                             seg_label = seg_label ) )

            return _set_dur_secs(outL)
        
        def _insert_midi( scoreL, midiL, src, player_id, piano_id, seg_label, ifn ):

            outL  = []
            # locate the set of 4 consecutive records in the score which are already marked with this scriabin segment label
            # (these records will be replaced with the full set of scriabin midi records)
            idxL  = [ i for i,r in enumerate(scoreL) if r['seg_label']==seg_label ]
            min_i = min(idxL)  
            max_i = max(idxL)

            assert max_i - min_i == 3

            
            offset_sec = 0
            
            # for each score record
            for i,r in enumerate(scoreL):

                # if this is the first record that matches the scriabin segment that we are inserting
                if i == min_i:
                    
                    # offset_sec = all records in midiL must be shifted by the duration of the block
                    offset_sec += midiL[-1]['sec'] + midiL[-1]['dur']

                    # beg_sec = new starting time of the first msg in the midiL is the end of the last msg in outL[]
                    beg_sec = outL[-1]['sec'] + outL[-1]['dur']

                    # Shift midiL in time to make beg_sec the starting time of the first msg
                    for i,m in enumerate(midiL):
                        m['sec'] += beg_sec

                    # append the block to the output list
                    outL += midiL
                else:
                    # if this is not the scriabin section ...
                    if min_i > i or i > max_i:
                        r['sec'] += offset_sec
                        r['dur'] = 0 if r['dur'] is None else r['dur']
                        
                        
                        outL.append(r) # ... then copy the record from input to output
            
            return outL

                
        # for each scriabin section
        for _,d in scriabinD.items():
            # read in the scriabin csv
            midiL = parse_midi_file(d['ifn'])

            # transform the scriabin midi into a format comptible with the score data
            midiL = _transform_midi(midiL,**d)

            # insert the scriabin midi into the score
            scoreL = _insert_midi(scoreL,midiL,**d)

        return scoreL

    def _update_oloc_index_and_uid(scoreL):

        locMapD = {}
        cur_loc = -1
        cur_sec = None
        for i,r in enumerate(scoreL):
            r['index'] = i
            r['uid']   = i

            if not midi.is_note_on(r):
                r['oloc'] = None
            else:

                if cur_sec is None or cur_sec != r['sec']:
                    cur_sec = r['sec']
                    cur_loc += 1

                if r['oloc'] not in locMapD:
                    locMapD[ r['oloc'] ] = cur_loc

                r['oloc'] = cur_loc

        # give the last msg in the score a loc ('even if it isn't a note-on)
        # (the 'demo_202602_ctl' uses this to notice that it has come to the end of the score)
        scoreL[-1]['oloc'] = cur_loc
        return locMapD
    
    def _validate(scoreL):

        for i,r in enumerate(scoreL):
            if i > 0:
                assert scoreL[i-1]['sec'] <= r['sec']

    def _write_output( scoreL, ofname):

        fieldnames = list(scoreL[0].keys())
        with open(ofname,"w") as f:
            wtr = csv.DictWriter(f,fieldnames)
            wtr.writeheader()
            for r in scoreL:
                wtr.writerow(r)
                

    scoreL = parse_score(i_score_fname)
    scoreL = _insert_scriabin(scriabinD,scoreL)
    locMapD = _update_oloc_index_and_uid(scoreL)
    _validate(scoreL)
    _write_output(scoreL,o_score_fname)

    
    return locMapD
        

def update_transform_file_locations(i_transform_fname,o_transform_fname,locMapD):

    with open(i_transform_fname) as f:
        r = json.load(f)

        for d in r['fragL']:
            d['begPlayLoc'] = locMapD[ d['begPlayLoc'] ]
            d['endPlayLoc'] = locMapD[ d['endPlayLoc'] ]

    with open(o_transform_fname,'w') as f:
        json.dump(r,f,indent=2)
                
def is_scriabin_segment( r ):
    key = 'scriabin'

    if type(r) == type(""):
        seg_label = r
    else:
        seg_label = r['seg_label']
    
    
    return seg_label[0:len(key)] == key
        

def gen_segment_ref_list( score_fname, playerToIdMapD ):

    refL           = []
    scoreL         = parse_score(score_fname)
    idToPlayerMapD = { ident:name for name,ident in playerToIdMapD.items() }
    cur_section_id = next((r['section'] for r in scoreL if r['section'] is not None),None)
    cur_seg_label  = None
    beg_timeD = {}
    
    for i,r in enumerate(scoreL):
        if r['section'] is not None:
            cur_section_id = r['section']

        if midi.is_note_on(r):
            if cur_seg_label is None or r['seg_label'] != cur_seg_label:

                cur_seg_label = r['seg_label']

                beg_timeD[ r['oloc'] ] = r['sec']
                
                # the seg recd is added on the FIRST note onset of the new segment
                refL.append({ 'seg_label':r['seg_label'],
                              'seg_id':len(refL),
                              'spirio_label': None if is_scriabin_segment(r) else r['spirio_label'],
                              'beg_meas':r['meas'],
                              'beg_section_id': cur_section_id,
                              'beg_loc': r['oloc'],
                              'end_loc': None,
                              'player_id': r['player_id'],                           
                              'player_label': idToPlayerMapD[r['player_id']]                              
                             } )


    # set the 'end_loc' for each segment
    for i,r in enumerate(refL):
        max_loc = r['beg_loc']
        for m in scoreL:
            if m['seg_label'] == r['seg_label'] and m['oloc'] is not None:
                max_loc = m['oloc']
        
        r['end_loc'] = max_loc


        
            

    return refL

def report_segment_ref_list( refL ):

    for r in refL:
        spirio_label = ' ' if r['spirio_label'] is None else r['spirio_label']
        meas_label   = ' ' if r['beg_meas'] is None else f"{r['beg_meas']}"
        print(f"{r['seg_id']:2} loc:{r['beg_loc']:4}-{r['end_loc']:4}  m:{meas_label:3} {r['beg_section_id']:4} {r['seg_label']:10} {spirio_label:9} {r['player_label']}")

def gen_multi_player( segRefL, score_fname, liveTakeD, o_fname ):

    def _calc_port_id( seg_label, live_fl ):

        if live_fl:
            return RECORDED_PORT_ID
        
        return SCRIABIN_PORT_ID if is_scriabin_segment( seg_label ) else SCORE_PORT_ID

    def _process_live_segments( liveTakeD, base_player_id ):
        
        def _parse_live_recording( fn ):
            msgL  = []
            midiL = parse_midi_file(fn)

            for i,m in enumerate(midiL):
                status = { 'non':midi.const.noteOnSt, 'nof':midi.const.noteOffSt, 'ped':midi.const.ctlSt, 'ctl':midi.const.ctlSt, 'tempo':None, 'eot':None }[m['type']]

                if status is not None:
                    sec = float(m['amicro']) / 1000000.0
                    msgL.append(dict(uid=len(msgL), sec=sec, ch=0, status=status, d0=m['D0'], d1=m['D1']))
                    
            return msgL

        def _drop_leading_time( msgL ):            
           # Drop all messages prior to the damper message preceeding the first note-on message.

            damper_msg_idx = None
            sost_msg_idx = None
            for i,m in enumerate(msgL):
                if midi.is_note_on(m):
                    beg_idx = i
                    break
                
                elif midi.is_sostenuto(m):
                    sost_msg_idx = i
                    
                elif midi.is_damper(m):
                    damper_msg_idx = i

                    
            if damper_msg_idx is None:
                damper_msg_idx = beg_idx
                
            if sost_msg_idx is None:
                sost_msg_idx = beg_idx

            # do not include any msg's prior to the first note-on except for the pedal msg immediately preceding beg_idx.
            outL = [ m for i,m in enumerate(msgL) if i>=beg_idx or i in [sost_msg_idx,damper_msg_idx] ]

            # get the index of the first note-on msg
            note_on_idx = next((i for i,m in enumerate(outL) if midi.is_note_on(m)),None)

            # set the pedal msg's preceeding the note-on on 50ms increments prior to the note-on msg
            FIFTY_MS = 0.05
            sec = 0
            for i,m in enumerate(outL[0:note_on_idx]):
                m['sec'] = sec
                m['uid'] = i;
                sec += FIFTY_MS

            dsec = sec - outL[note_on_idx]['sec']
                
            # shift all successive messages relative to the start of the first note-on msg
            for i,m in enumerate(outL[note_on_idx:]):
                m['sec'] += dsec
                m['uid'] = note_on_idx + i
                
            return outL
        
        mpD         = {}   # { player_label: { player_id, player_label, port_id, msgL } }
        menuD       = {}   # { seg_label:[ (title,player_id( ]
        player_id   = base_player_id
        base_folder = liveTakeD['base_folder']
        
        # for each segment
        for seg_label,refD in liveTakeD['takeD'].items():

            #print(seg_label,len(refD['takeL']))
            
            for take_num in refD['takeL']:
                menu_title   = f"{refD['folder']}-{take_num}"
                player_label = f"{seg_label}_{refD['folder']}_{take_num}"
                fn           = os.path.join(base_folder,refD['folder'],f'record_{take_num}','midi_am_sf.csv')                
                msgL         = _parse_live_recording(fn)
                msgL         = _drop_leading_time(msgL)
                #port_id             = SCRIABIN_PORT_ID if is_scriabin_segment( seg_label ) else GUTIM_PORT_ID
                port_id      = _calc_port_id( seg_label, True )
                mpD[ player_label ] = dict(player_id=player_id, label=player_label, port_id=port_id, msgL=msgL)
                if seg_label not in menuD:
                    menuD[seg_label] = []
                menuD[seg_label].append((menu_title,player_id))
                player_id += 1
                
            
        return mpD,menuD,player_id
            

    def _process_score_segments( segRefL, score_fname, base_player_id ):

        def _gen_score_msg_list( scoreL, seg_label, beg_loc ):

            msgL = []
            base_sec = None
            for r in scoreL:
                
                if seg_label == r['seg_label'] and r['status'] is not None:
                    if base_sec is None:
                        base_sec = r['sec']
                    msgL.append(dict(uid=len(msgL), sec=r['sec']-base_sec, ch=0, status=r['status'], d0=r['d0'], d1=r['d1']))
            return msgL

        mpD   = {}
        menuD = {}
        player_id = base_player_id
        scoreL = parse_score(score_fname)
        for refD in segRefL:
            seg_label           = refD['seg_label']
            player_label        = f"{seg_label}_score"
            menu_title          = f"score_{refD['beg_section_id']}"
            msgL                = _gen_score_msg_list( scoreL, seg_label, refD['beg_loc'] )
            assert seg_label not in mpD
            #port_id             = SCRIABIN_PORT_ID if is_scriabin_segment( refD ) else GUTIM_PORT_ID
            port_id      = _calc_port_id( seg_label, False )            
            mpD[ player_label ] = dict(player_id=player_id,label=player_label,port_id=port_id,msgL=msgL)
            menuD[ seg_label ] = [(menu_title,player_id)]
            player_id += 1

        return mpD,menuD

    def _write_menu_files( scoreSegMenuD, liveSegMenuD ):

        base_folder = "menus"
        os.makedirs(base_folder,exist_ok=True)
        
        # merge the menus into a single dictionary { seg_label:[(title,player_id)] }
        for seg_label,_ in scoreSegMenuD.items():
            if seg_label in liveSegMenuD:
                scoreSegMenuD[seg_label] += liveSegMenuD[seg_label]
            #print(seg_label,len(scoreSegMenuD[seg_label]))

        for seg_label,menuL in scoreSegMenuD.items():
            if len(menuL) > 1:
                fn = os.path.join(base_folder,f"{seg_label}.cfg")
            
                with open(fn,"w") as f:
                    json.dump({label:player_id for label,player_id in menuL},f,indent=2)

        return scoreSegMenuD

    def _write_multi_player_file( scoreMpD, liveMpD, o_fname ):

        player_idL = []
        
        for player_label,r in scoreMpD.items():
            assert player_label not in liveMpD
            player_idL.append(r['player_id'])

        assert len(player_idL) == len(set(player_idL))

        mpD = scoreMpD | liveMpD

        with open(o_fname,"w") as f:
            json.dump(mpD,f,indent=2)    
        
    next_player_id = 0
    # Each entry in segMenuD{} produces a segement menu that maps
    # a title to a multi-player player-id.
    segMenuD = {}  # { <seg_label>:[ (<menu_title>,<player_id>) ] }

    # Generate the multi-player dictionary for the live recordings and their associated menu dictionaries
    liveMpD,liveSegMenuD, next_player_id = _process_live_segments( liveTakeD, next_player_id )

    # Generate the multi-player dictionary for score based playback for all segements.
    # Generate menu dictionaries for all segments that are also played live.
    scoreMpD,scoreSegMenuD = _process_score_segments( segRefL, score_fname, next_player_id )

    # write the segment menu files
    segMenuD = _write_menu_files( scoreSegMenuD, liveSegMenuD )

    # write the multi-player file
    _write_multi_player_file( scoreMpD, liveMpD, o_fname )

    return segMenuD
    
def gen_pgm_ctl_file( segRefL, segMenuD, start_menu_fname, o_fname ):

    scriabin_label = 'scriabin'
    gutim_label    = 'gutim'

    seg_idL = [] 

    with open(start_menu_fname) as f:
        start_menuD = json.load(f)
        start_menuD = { seg_idx:title for title,seg_idx in start_menuD.items() }
    
    for seg_idx,r in enumerate(segRefL):
    
        if r['seg_label'][:len(scriabin_label)] == scriabin_label:
            d = { r['seg_label']: segMenuD[ r['seg_label']][0][1] }
            type_id = 'scriabin'
             
        elif r['spirio_label'] is not None:
            d = { r['seg_label']: segMenuD[ r['seg_label']][0][1] }
            type_id = 'spirio'
            
        else:
            assert r['seg_label'][:len(gutim_label)] == gutim_label
            d = { label:player_id for label,player_id in segMenuD[ r['seg_label'] ] }
            type_id = 'gutim'

        
        seg_idL.append( dict(type_id = type_id,
                             seg_label=r['seg_label'],
                             seg_id=r['seg_id'],
                             title = start_menuD[seg_idx],
                             seg_idx = seg_idx,
                             beg_loc = r['beg_loc'],
                             end_loc = r['end_loc'],
                             menuD   = d,                             
                             )                        
                       )


    # seg_idL:[ { title:<>,
    #             type_id:'gutim'|'scriabin'|'spirio',
    #             beg_loc:<>,
    #             end_loc:<>,
    #             menuD:{ <title>:mp_player_id } } ]
    # 
    # 'title' is the UI title of this segment
    #    
    # 'menuD': Menu of possible player_id's for this segment
    # '  spirio' and 'scriabin' segments only have a single player id in menuD{}
    
    # 
    with open(o_fname,'w') as f:
        json.dump({ "segL":seg_idL },f,indent=2)

    
if __name__ == "__main__":

    args = dict(
        
        playerToIdMapD = {'A':0,'H':1,'N':2,'S':3 },

        i_score_fname    = "data/score_cult_evt_20250929_5.csv",
        o_score_fname    = "score_demo_20260217.csv",
        i_transform_fname = "data/cult_evt_xforms.txt",
        o_transform_fname = "demo_xforms.txt",
        o_multi_plyr_fname = "multi_player.cfg",
        o_pgm_ctl_fname    = "pgm_ctl.cfg",
        i_start_menu_fname = "start_menu.json",
        
        scriabinD = {
            'scriabin_1':{ "src":"scriabin_74_1",  "ifn":"data/scriabin/scriabin_prelude_op74_1.csv",  'player_id':2, 'piano_id':0, 'seg_label':'scriabin_1' },
            'scriabin_2':{ "src":"scriabin_51_2",  "ifn":"data/scriabin/scriabin_prelude_op51_2.csv",  'player_id':0, 'piano_id':1, 'seg_label':'scriabin_2' },
            'scriabin_3':{ "src":"scriabin_74_5",  "ifn":"data/scriabin/scriabin_prelude_op74_5.csv",  'player_id':1, 'piano_id':1, 'seg_label':'scriabin_3' },
        },

       liveTakeD = {
           'base_folder':"/home/kevin/temp/currawong",
           'takeD':{
               'gutim_1':  dict(player='N', folder='nicolas2',  takeL=[1,2,3,4,5,6,7,8,9,10,11,12]),
               'gutim_2':  dict(player='H', folder='han2',      takeL=[0,1,2,3,4,5,6]), # no valid end: 7
               'gutim_3':  dict(player='A', folder='arseniy1',  takeL=[6,0,1,2,3]), # 6=pref'd
               'gutim_5':  dict(player='N', folder='nicolas2',  takeL=[19,20,21,22,24,25,26,27,28,29]), # skip 23 SF issue
               'gutim_7':  dict(player='H', folder='han2',      takeL=[22,23,24,25,26,27,28,29,30,31,32,33,34]),
               'gutim_8':  dict(player='A', folder='arseniy1',  takeL=[15,7,8,9,10,11,12,13,14,16]), # 15=pref'd
               'gutim_9':  dict(player='H', folder='han2',      takeL=[8,9,12,13,14,15,16,17,18,20,21]), # no valid end: 10,11,19
               'gutim_10': dict(player='N', folder='nicolas2',  takeL=[13,14,15,16,17,18]),
               'gutim_12': dict(player='A', folder='arseniy1',  takeL=[25,17,18,20,21,22,23,24,26]), # 25=pref'd no valid end: 19
               'gutim_15': dict(player='N', folder='nicolas2',  takeL=[36,37,38,39,40,41,43]), # no valid end: 42
               'gutim_17': dict(player='A', folder='arseniy1',  takeL=[32,27,28,29,30,31,33,34,35]), # 32=pref'd
               'gutim_18': dict(player='H', folder='han1',      takeL=[14,13,17,19,10,11,12,15,16,18,20,21,22,23]), #14,13,17,19=pref'd
               'gutim_20': dict(player='N', folder='nicolas2',  takeL=[30,31,32,33,34,35]),
               'gutim_22': dict(player='A', folder='arseniy1',  takeL=[42,36,37,38,39,40,41,43,44,45,46]), # 42=pref'd
               'gutim_23': dict(player='H', folder='han1',      takeL=[31,32,33,34,24,25,26,27,28,29,30,35,37,38,39]), # 36 false start, 31-34=pref'd
               'gutim_25': dict(player='N', folder='nicolas1',  takeL=[3,9,12,16,17,18,19,20]), # all pref'd
               'gutim_26': dict(player='H', folder='han1',      takeL=[9,0,1,2,3,4,5,6,8]), # 7 false start 9=pref'd
               'gutim_28': dict(player='A', folder='arseniy1',  takeL=[51,47,48,49,50,52]) # 51=pref'd
               }
       }


        
    )
    
    args = types.SimpleNamespace(**args)


    # insert the scriabin sections into the score
    locMapD = insert_scriabin(args.i_score_fname,args.scriabinD,args.o_score_fname)

    # update the transform preset file with the new score locations
    update_transform_file_locations(args.i_transform_fname,args.o_transform_fname,locMapD)

    # generate a segment reference list 
    segRefL = gen_segment_ref_list( args.o_score_fname, args.playerToIdMapD )

    report_segment_ref_list(segRefL)
    
    segMenuD = gen_multi_player( segRefL, args.o_score_fname, args.liveTakeD, args.o_multi_plyr_fname )

    gen_pgm_ctl_file( segRefL, segMenuD, args.i_start_menu_fname, args.o_pgm_ctl_fname )
