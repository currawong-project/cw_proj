import json

def analyze_end_seg( mp_cfg_fname, end_seg_fname ):


    with open( multi_play_cfg_fname ) as f:
        cfg = json.load(f)

        for perf_name,d in cfg.items():
            for evt in d['msgL']:
                

    


def report_first_note_time_offset( multi_play_cfg_fname  ):

    avg_sec = 0
    max_sec = 0
    with open( multi_play_cfg_fname ) as f:
        cfg = json.load(f)

        for perf_name,d in cfg.items():
            for evt in d['msgL']:
                if evt['status'] == 144 and evt['d1']>0:
                    avg_sec += evt['sec']
                    max_sec = max(max_sec,evt['sec'])

                    if evt['sec'] > .25:
                        print(perf_name,evt['sec'])
                    break

        print("avg:",avg_sec/len(cfg),"max:",max_sec)
                    


if __name__ == "__main__":

    multi_play_cfg_fname = "multi_player.cfg"
    end_seg_fname = "../io/pgm_03_midi_xform/end_seg_detect.cfg"

    
    report_first_note_time_offset(multi_play_cfg_fname)
