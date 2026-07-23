import json
import midi

def report( ref_fname, mp_fname):

    def _get_ending_events( msgL, N, ena_damp_fl=True, ena_sost_fl=True ):

        sost_fl   = True
        sost_recd = None
        damp_fl   = True
        damp_recd = None
        endL = []
        for m in reversed(msgL):

            if midi.is_note_on(m):
                endL.append(m)
                
            elif midi.is_note_off(m):
                endL.append(m)
                
            elif midi.is_damper_up(m):
                damp_recd = m
            
            elif midi.is_damper_down(m):
                if ena_damp_fl and damp_fl and damp_recd is not None:
                    endL.append(damp_recd)
                    damp_fl = False
                            
            elif midi.is_sostenuto_up(m):
                sost_recd = m
                
            elif midi.is_sostenuto_down(m):
                if ena_sost_fl and sost_fl and sost_recd is not None:
                    endL.append(sost_recd)
                    sost_fl = False

        
            if len(endL) >= N:
                break

        return sorted(endL,key=lambda x: x['sec'])

    def _report_end_list( title, endL ):

        def _msg_to_string(m):
            s = None
            if m is None:
                s = "<none>"
            elif midi.is_note_on(m):
                s = f"({m['d0']})"
            elif midi.is_note_off(m):
                s = f"{m['d0']}"
            elif midi.is_damper_up(m):
                s = "dU"
            elif midi.is_sostenuto_up(m):
                s = "sU"
            else:
                assert False

            return s

        def _end_dur(endL):
            beg_sec = min( (m['sec'] for m in endL))
            end_sec = max( (m['sec'] for m in endL))

            return end_sec - beg_sec

        print(f"{title} : ",end="")
        for m in endL:            
            print(f"{_msg_to_string(m)} ",end=" ")
        print(f"{_end_dur(endL):5.3f}")
        

    with open(ref_fname) as f:
        refD = json.load(f)
        
    with open(mp_fname) as f:
        fullMpD = json.load(f)

    fullMpD = { d['player_id']:d for label,d in fullMpD.items() }

    # for each segment
    for r in refD['segL']:
        print(r['seg_label'])
        for mp_title,player_id in r['menuD'].items():
            mpD = fullMpD[ player_id ]

            endL = _get_ending_events( mpD['msgL'], N=5, ena_damp_fl=False, ena_sost_fl=False  )

            _report_end_list(mp_title,endL)

        print("")

    return refD
            
def gen_ctl_file( refD, o_fname ):

    ctlL = []
    for i,r in enumerate(refD['segL']):

        d = dict(id=i,
                 trig_seg_id=i,
                 seg_label = r['seg_label'],
                 spirio_label = r['seg_label'],
                 piano_id = 0,
                 piano_label = "A",
                 min_ms = 0,
                 max_ms = 2000,
                 type = "p_det",
                 pdetL = [
                     dict(ch=0,status=midi.const.noteOnSt,d0=0, release_fl=True),
                     dict(ch=0,status=midi.const.ctlSt,   d0=midi.const.sustainCId, release_fl=True),
                     ],
                 sdetL = [] )

        
                 
        ctlL.append(d)

    with open(o_fname,"w") as f:
        json.dump(dict(list=ctlL),f)
    
        
def report_msg_list( mp_fname, key_label ):

    with open(mp_fname) as f:
        fullMpD = json.load(f)

    for player_label,d in fullMpD.items():
        for m in d['msgL']:
            if midi.is_note_on(m):
                if player_label == key_label:
                    print(m['d0'])
    
    

if __name__ == "__main__":

       mp_fname = "multi_player.cfg"
       ref_fname = "pgm_ctl.cfg"

       refD = report(ref_fname,mp_fname)

       #gen_ctl_file(refD,"midi_detect.cfg")

       report_msg_list(mp_fname,"gutim_2_han2_4")
       
