import csv
import json
import types

MIDI_NOTE_ON_STATUS = 0x90
MIDI_NOTE_OFF_STATUS = 0x80
MIDI_CTL_STATUS = 0xb0
MIDI_DAMPER_D0 = 0x41
MIDI_SOST_D0 = 0x42
MIDI_DAMPER_HALF_VALUE = 43
MIDI_MAX_CTL_VALUE = 127

"""
        {
        "spirio_1": {
          "player_id": 3,
          "label": "gutim_4",
          "port_id": 0,
          "msgL": [
          {
            "uid": 0,
            "sec": 0.0,
            "ch": 0,
            "status": 144,
            "d0": 24,
            "d1": 5
          } ]
         }
        }
"""

def gen_note_list( arg ):
    
    spb   = 60.0 / arg.bpm
    noteL = []
    noteN = int(arg.dur_sec / spb)
    pitch = arg.min_pitch
    dyn   = arg.min_dyn
    for i in range(noteN):
        sec     = i * spb
        dur_sec = spb * 0.75
        
        noteL.append( types.SimpleNamespace(**dict(sec=sec, pitch=pitch, dyn=dyn, dur_sec=dur_sec)))

        pitch += 1
        if pitch > arg.max_pitch:
            pitch = arg.min_pitch

        dyn += 1
        if dyn > arg.max_dyn:
            dyn = arg.min_dyn

    return noteL
        

def gen_mp_section( arg ):

    noteL = gen_note_list(arg)    
    msgL  = []
    uid   = 0
    
    for n in noteL:
        msgL.append( dict(uid=uid, sec=n.sec, ch=0, status=MIDI_NOTE_ON_STATUS, d0=n.pitch, d1=n.dyn) )
        uid+=1
        
        msgL.append( dict(uid=uid, sec=n.sec + n.dur_sec, ch=0, status=MIDI_NOTE_OFF_STATUS, d0=n.pitch, d1=0) )
        uid+=1

    msgL = sorted(msgL,key=lambda x:x['sec'])
        
    return dict(player_id=arg.player_id, label=arg.label, port_id=arg.port_id, msgL=msgL )
    
def gen_score( args, mpSectD ):

    idD = {}

    def _gen_id(the_id):
        if the_id not in idD:
            idD[the_id] = 0
        else:
            idD[the_id] += 1
            the_id = f"{the_id}_{idD[the_id]}"
        return the_id
    
    
    def _midi_to_sci_pitch( midi ):
        NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        return f"{NOTE_NAMES[midi % 12]}{(midi // 12) - 1}"

    

    scoreL        = []
    loc           = 0
    meas_note_idx = 0
    meas          = 0

    sect_id = _gen_id(f"sect_{args.section_id}")
    scoreL.append(dict(meas=1,sec=0.0,loc=None,sci_pitch=None,status=None,d0=None,d1=None,bar=None,section=args.section_id,player_id=args.player_id,piano_id=None,id=sect_id))
    
    for m in mpSectD['msgL']:
        sci_pitch = _midi_to_sci_pitch( m['d0'] )

        if meas_note_idx == 0:
            meas += 1
            meas_id = _gen_id(f"meas_{meas}")
            scoreL.append(dict(meas=meas,sec=m['sec'],loc=None,sci_pitch=None,status=None,d0=None,d1=None,bar=meas,section=None,player_id=args.player_id,piano_id=None,id=meas_id))


        note_id = _gen_id(f"n{meas}_1{sci_pitch}")
        scoreL.append(dict(meas=meas,sec=m['sec'],loc=loc,sci_pitch=sci_pitch,status=m['status'],d0=m['d0'],d1=m['d1'],bar=None,section=None,player_id=args.player_id,piano_id=args.piano_id,id=note_id))

        if m['status'] == MIDI_NOTE_ON_STATUS:
            loc += 1

        meas_note_idx = (meas_note_idx + 1) % args.notes_per_meas
        
    return scoreL

def write_mp_file( fname, mpSectL ):

    mpSectD = {}
    for mpSect in mpSectL:
        mpSectD[ mpSect['label'] ] = mpSect

    with open(fname,"w") as f:
        json.dump(mpSectD,f,indent=2)
    
    

def write_score_file( fname, scoreL ):
    titleL = ["index","meas","sec","loc","oloc","sci_pitch","status","d0","d1","bar","section","grace","player_id","piano_id","id","re_attack"]

    rowL = []
    for idx,s in enumerate(scoreL):
        s['oloc'] = s['loc']
        rowL.append({ title:s[title] if title in s else None for title in titleL })

    with open(fname,"w") as f:
        wtr = csv.DictWriter(f,fieldnames=titleL)

        wtr.writeheader()
        for r in rowL:
            wtr.writerow(r)
            

def write_preset_file( arg, preset_json_fname, scoreL ):

    def _loc_list( scoreL ):
        locL = []
        for s in scoreL:
            if s['status'] == MIDI_NOTE_ON_STATUS:
                locL.append(s['loc'])
        return locL

    preset_labels  = [ 'dry','a','b','c','d','f1','f2','f3','f4','g','ga','g1a','g1d']

    fragL          = []
    cur_preset_idx = 0
    locL = _loc_list(scoreL)

    # select every 'preset_loc_delta' loc
    locL = [ locL[i] for i in range(0,len(locL),arg.preset_loc_delta) ]

    # form the fragL[]
    for frag_id,beg_loc in enumerate(locL):
        fragL.append( dict( frag_id=frag_id,
                            end_loc=beg_loc + (arg.preset_loc_delta-1),
                            inGain=1.0,
                            outGain=1.0,
                            wetDryGain=0.5,
                            fadeOutMs=50.0,
                            presetN=len(preset_labels),
                            presetL=[ dict(order=0, preset_label=label, play_fl=False) for label in preset_labels ] ) )

        fragL[-1]['presetL'][ cur_preset_idx ]['order'] = 1

        cur_preset_idx += 1
        if cur_preset_idx >= len(preset_labels):
            cur_preset_idx = 0

    # form the fragD{}
    fragD = dict(fragN=len(fragL),
                 masterWetInGain=1.5,
                 masterWetOutGain=1.0,
                 masterDryGain=1.0,
                 masterSyncDelayMs=400.0,
                 fragL=fragL)

    # write the file
    with open(preset_json_fname,"w") as f:
        json.dump(fragD,f,indent=2)
        

if __name__ == "__main__":

    multi_player_json_fname  = "multi_player.json"
    score_csv_fname_prefix   = "score"
    preset_json_fname_prefix = "preset"

    paramL = [
        dict(label="section_a", section_id=1000, piano_id=0, player_id=0),
        dict(label="section_b", section_id=2000, piano_id=1, player_id=1),
        dict(label="section_c", section_id=3000, piano_id=2, player_id=2),
    ]
    
    
    argD = dict(
        label     = None,
        section_id = None,
        piano_id  = None,
        player_id = None,
        pedal_fl  = False,
        port_id   = 0,
        dur_sec   = 60,
        bpm       = 60,        
        min_pitch = 21,
        max_pitch = 108,
        min_dyn   = 1,
        max_dyn   = 24,
        notes_per_meas  = 4,

        preset_loc_delta = 10
    )

    mpSectL = []
    
    for i,paramD in enumerate(paramL):
        
        for k,v in paramD.items():
            argD[k] = v

        arg     = types.SimpleNamespace(**argD)

        mpSectD = gen_mp_section(arg)
        
        mpSectL.append(mpSectD)
        
        scoreL  = gen_score(arg,mpSectD)
        score_csv_fname = f"{score_csv_fname_prefix}{i}.csv"
        write_score_file( score_csv_fname, scoreL )

        preset_json_fname = f"{preset_json_fname_prefix}{i}.json"
        write_preset_file( arg, preset_json_fname, scoreL )
    

    write_mp_file( multi_player_json_fname, mpSectL )

    
