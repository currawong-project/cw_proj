import csv
import json
import midi_util

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

def get_score_note_list( score_fname, beg_loc, end_loc ):
    scoreL = parse_score(score_fname)
    noteL = []
    for r in scoreL:
        if r['opcode'] == 'non' and r['onset'] is not None and r['onset'] == 'o' and r['oloc'] is not None and (beg_loc <= r['oloc'] and r['oloc'] <= end_loc):            
            noteL.append(dict(sec=r['sec'], loc=r['oloc'], pitch=r['d0'], vel=r['d1'], sci_pitch=r['sci_pitch']) )
            
    return noteL


def get_ctl_info( ctl, seg_label, take_label ):

    with open(pgm_ctl_fname) as f:
        ctl = json.load(f)
    
    for seg in ctl['segL']:
        if seg['seg_label'] == seg_label:
            for label,player_id in seg['menuD'].items():
                if label == take_label:
                    return player_id, seg['beg_loc'], seg['end_loc']
            print(f"take label: {take_label} not found.")
            assert False

    print(f"seg label: {seg_label} not found.")
    assert False
    return None,None,None

def get_perf_msg_list(mp_fname, player_id ):
    
    with open(mp_fname) as f:
        mpD = json.load(f)

    msgL = []
    for player_name,d in mpD.items():
        if d['player_id'] == player_id:
            for m in d['msgL']:
                if m['status'] == 144 and m['d1'] > 0:
                    msgL.append(dict(sec=m['sec'],pitch=m['d0'],vel=m['d1']))
    return msgL

def print_score( noteL, N=10):

    print("score: ",end="")
    for i,r in enumerate(noteL):
        s = f"{r['sci_pitch']}-{r['vel']}"
        print(f"{s:7} ",end="")
        if i >= N:
            break
        
    print("")
    return
    
    for i,r in enumerate(noteL):        
        print(f"{r['loc']:4} {r['pitch']:3} {r['sci_pitch']:4} {r['vel']:3}")
        if i >= N:
            break

        
def print_perf( noteL, N=10):

    print("perf:  ",end="")
    for i,r in enumerate(noteL):
        sci_pitch = midi_util.to_sci_pitch( r['pitch'] )
        s = f"{sci_pitch}-{r['vel']}"
        print(f"{s:7} ",end="")
        if i >= N:
            break
        
    print("")
    return

    for i,r in enumerate(noteL):
        sci_pitch = midi_util.to_sci_pitch( r['pitch'] )
        
        print(f"{r['pitch']:3} {sci_pitch:4} {r['vel']:3} ")
        if i >= N:
            break
        
def compare( score_fname, pgm_ctl_fname, mp_fname, seg_label, take_label ):

    N = 15
    
    player_id,beg_loc,end_loc = get_ctl_info(pgm_ctl_fname,seg_label,take_label)

    score_noteL = get_score_note_list(score_fname,beg_loc,end_loc)

    print_score( score_noteL, N )
    
    perf_msgL = get_perf_msg_list(mp_fname,player_id)

    print_perf( perf_msgL, N )
    

    
if __name__ == "__main__":
    score_fname   = "score_demo_20260217.csv"
    pgm_ctl_fname = "pgm_ctl.cfg"
    mp_fname      = "multi_player.cfg"
    seg_label     = "gutim_3"
    take_label    = "arseniy1-6"

    seg_label     = "gutim_10"
    take_label    = "score_5961"
    
    compare( score_fname, pgm_ctl_fname, mp_fname, seg_label, take_label )

    print(midi_util.to_sci_pitch( 70 ))
    print(midi_util.to_sci_pitch( 78 ))
    
