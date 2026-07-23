import gen_data_files as gdf
import midi

def report( fname, beg_loc, end_loc ):

    scoreL = gdf.parse_score(fname)

    for m in scoreL:
        if m['oloc'] is not None and beg_loc <= m['oloc'] and m['oloc'] < end_loc and midi.is_note_on(m):
            print( m['d0'],m['oloc'] )
        


def find_sequence( fname, seqL ):

    scoreL = gdf.parse_score(fname)
    n = 0
    for i,m in enumerate(scoreL):
        if midi.is_note_on(m):
            if m['d0'] in seqL:
                
                n += 1
                
                if n >= len(seqL):
                    print(i,"***",m)
                    n = 0
            else:
                n = 0;
            
if __name__ == "__main__":

    score_fname = "score_demo_20260217.csv"
    beg_loc = 46
    end_loc = 104
    
    #report(score_fname,beg_loc,end_loc)
    
    
    find_sequence( score_fname, [36,81,88] )
