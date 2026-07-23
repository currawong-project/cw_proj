import math
import numpy as np

class const:
    noteOffSt  = 0x80
    noteOnSt   = 0x90
    polyPrSt   = 0xa0
    ctlSt      = 0xb0
    pgmSt      = 0xc0
    chPresSt   = 0xd0
    pbendSt    = 0xe0
    sysExSt    = 0xf0
    sysExEndSt = 0xf7
    metaSt     = 0xff

    seqNumbMId   = 0x00
    textMId      = 0x01
    copyMId      = 0x02
    trkNameMId   = 0x03
    instrNameMId = 0x04
    lyricsMId    = 0x05
    markerMId    = 0x06
    cuePointMId  = 0x07
    midiChMId    = 0x20
    endOfTrkMId  = 0x2f
    tempoMId     = 0x51
    smpteMId     = 0x54
    timeSigMId   = 0x58
    keySigMId    = 0x59
    seqSpecMId   = 0x7f

    maxPitch = 127
    maxVel   = 127

    sustainCId    = 0x40
    portamentoCId = 0x41
    sostenutoCId  = 0x42
    softCId       = 0x43
    legatoCId     = 0x44

    textD = {
        noteOffSt    :"nof",
        noteOnSt     :"non",
        polyPrSt     :"ppr",
        ctlSt        :"ctl",
        pgmSt        :"pgm",
        chPresSt     :"cpr",
        pbendSt      :"bnd",
        sysExSt      :"sex",
        sysExEndSt   :"see",
        metaSt       :"met",
        seqNumbMId   :"seq",
        textMId      :"txt",
        copyMId      :"cpy",
        trkNameMId   :"trk",
        instrNameMId :"ins",
        lyricsMId    :"lyr",
        markerMId    :"mrk",
        cuePointMId  :"cue",
        midiChMId    :"mch",
        endOfTrkMId  :"eot",
        tempoMId     :"tmp",
        smpteMId     :"smt",
        timeSigMId   :"tsg",
        keySigMId    :"ksg",
        seqSpecMId   :"spc"
    }

    # General MIDI program names
    genMidiPgmD = {
        0: ("piano","grand"),
        1: ("piano","bright"),
        2: ("piano","electric"),
        3: ("piano","honky-tonk"),
        4: ("piano","electric"),
        5: ("piano","electric"),
        6: ("harpsichord"),
        7: ("clavichord"),
        8: ("celesta"),
        9: ("glockenspiel"),
        10: ("music box"),
        11: ("vibraphone"),
        12:("marimba"),
        13:("xylophone"),
        14:("tubular bell"),
        15:("dulcimer"),
        16:("organ","drawbar"),
        17:("organ","percussive"),
        18:("organ","rock"),
        19:("organ","church"),
        20:("organ","reed"),
        21:("accordian"),
        22:("harmonica"),
        23:("accordian","tango"),
        24:("guitar","acoustic","nylon"),
        25:("guitar","acoustic","steel"),
        26:("guitar","electric","jazz"),
        27:("guitar","electric","clean"),
        28:("guitar","electric","muted"),
        29:("guitar","overdriven"),
        30:("guitar","distorted"),
        31:("guitar","harmonics"),
        32:("bass","acoustic"),
        33:("bass","electric","finger"),
        34:("bass","electric","pick"),
        35:("bass","fretless"),
        36:("bass","slap"),
        37:("bass","slap"),
        38:("bass","synth"),
        39:("bass","synth"),
        40:("violin",),
        41:("viola"),
        42:("cello"),
        43:("contrabass"),
        44:("strings","tremelo"),
        45:("strings","pizzicato"),
        46:("harp","orchestral"),
        47:("timpani"),
        48:("string","ensemble"),
        49:("string","ensemble"),
        50:("strings","synth"),
        51:("strings","synth"),
        52:("voice","ahh","choir"),
        53:("voice","ooh",),
        54:("voice","synth",),
        55:("orchestra","hit",),
        56:("trumpet",),
        57:("trombone",),
        58:("tuba"),
        59:("trumpet","muted"),
        60:("french horn"),
        61:("brass","section"),
        62:("brass","synth"),
        63:("brass","synth"),
        64:("soprano saxophone"),
        65:("alto saxophone"),
        66:("teno saxophone"),
        67:("baritone saxophone"),
        68:("oboe",),
        69:("english horn"),
        70:("bassoon"),
        71:("clarinet"),
        72:("piccolo"),
        73:("flute"),
        74:("recorder"),
        75:("flute","pan"),
        76:("bottle","blown"),
        77:("shakuhachi"),
        78:("whistle"),
        79:("ocarina"),
        80:("lead","square"),
        81:("lead","sawtooth"),
        82:("lead","calliope"),
        83:("lead","chiff"),
        84:("lead","charang"),
        85:("lead","voice"),
        86:("lead","fifths"),
        87:("lead","bass+lead"),
        88:("pad","new age"),
        89:("pad","warm"),
        90:("pad","polysynth"),
        91:("pad","choir"),
        92:("pad","bowed"),
        93:("pad","metallic"),
        94:("pad","halo"),
        95:("pad","sweep"),
        96:("fx","train"),
        97:("fx","soundtrack"),
        98:("fx","crystal"),
        99:("fx","atmosphere"),
        100:("fx","brightness"),
        101:("fx","goblins"),
        102:("fx","echoes"),
        103:("fx","sci-fi"),
        104:("sitar"),
        105:("banjo"),
        106:("shmisen"),
        107:("koto"),
        108:("kalimba"),
        109:("bag pipe"),
        110:("fiddle"),
        111:("shanai"),
        112:("tinkle bell"),
        113:("agogo"),
        114:("drum","steel"),
        115:("woodblock"),
        116:("drum","taiko"),
        117:("drum","tom"),
        118:("drum","synth"),
        119:("cymbal","reverse"),
        120:("guitar","fret noise"),
        121:("voice","breath noise"),
        122:("seashore"),
        123:("bird"),
        124:("telephone"),
        125:("helicopter"),
        126:("applause"),
        127:("gunshot" )
    }

    # general MIDI percussion names 
    genMidiPercA = {
        35:("bass drum","acoustic"),
        36:("bass drum",),
        37:("side stick"),
        38:("snare", "acoustic"),
        39:("clap"),
        40:("snare","electric"),
        41:("tom","floor","low"),
        42:("cymbal","high hat","closed"),
        43:("tom","high","floor"),
        44:("cymbal","high hat","pedal"),
        45:("tom","low"),
        46:("cymbal","high hat","open"),
        47:("tom","low","mid"),
        48:("tom","high","mid"),
        49:("cymbal","crash"),
        50:("tom","high"),
        51:("cymbal","ride"),
        52:("cymbal","chinese"),
        53:("bell","ride"),
        54:("tambourine"),
        55:("cymbal","splash"),
        56:("bell","cow"),
        57:("cymbal","crash"),
        58:("vibraslap"),
        59:("cymbal","ride"),
        60:("bongo","high"),
        61:("bongo","low"),
        62:("conga","high","mute"),
        63:("conga","high","open"),
        64:("conga","low"),
        65:("timbale","high"),
        66:("timbale","low"),
        67:("agogo","high"),
        68:("agogo","low"),
        69:("cabasa",),
        70:("maracas"),
        71:("whistle","short"),
        72:("whistle","long"),
        73:("guiro","short"),
        74:("guiro","long"),
        75:("claves",),
        76:("woodblock","high"),
        77:("woodblocK","low"),
        78:("cuica","mute"),
        79:("cuica","open"),
        80:("triangle","mute"),
        81:("triange","open"),
    }
        

def to_hz( midi ):
    return (13.75 * pow(2,-9.0/12.0)) * pow(2.0,float(midi) / 12.0)

def hz_to_midi( hz ):

    hzV = np.array([ 8.18 * pow(2.0,x/12.0) for x in range(128) ])
    
    midi = 0
    
    if hz < hzV[0]:
        midi = 0
    elif hz > hzV[-1]:
        midi = 127
    else:
        midi = np.argmin( np.abs(hzV - (np.ones((128,)) * hz))) 

    return midi

def sci_pitch_to_midi_pitch( sciPitchStr ):
    stOffsV = [9, 11, 0, 2, 4, 5, 7]

    sciPitchStr = sciPitchStr.lower()
    
    pitchClass = ord(sciPitchStr[0]) - ord('a')

    if pitchClass < 0 or pitchClass >= len(stOffsV):
        raise ValueError("Invalid note character (%s) in scientific pitch string." % (sciPitchStr[0],))
    

    stOffs = stOffsV[pitchClass]

    nextIdx = 2
    if sciPitchStr[1]=="#": 
        stOffs+=1
    elif sciPitchStr[1]=="b":
        stOffs-=1
    else:
        nextIdx = 1

    s = sciPitchStr[nextIdx:]
    
    octave = int(s)

    if math.isnan(octave):
        raise ValueError("Invalid octave value '%s' in scientific pitch string." % (s,))

    return (octave * 12) + stOffs + 12 

def hz_to_sci_pitch( hz, flat_fl=False):
    lV = [ 'C','C','D','D','E','F','F','G','G','A','A','B' ];
    sV = [ ' ','#',' ','#',' ',' ','#',' ','#',' ','#',' ' ];

    kV = [ 'C','D','D','E','E','F','G','G','A','A','B','B' ];
    fV = [ ' ','b',' ','b',' ',' ','b',' ','b',' ','b',' ' ];
    
    minNote = -21       # C-1 = 21 semitones below a0 (27.5 hz)
    maxNote = (9*12)+3  # 3 semitones above a9 

    hzV = [ 27.5 * pow(2,v/12.0) for v in range(minNote,maxNote,1) ]

    #hzV = 27.5 * 2.^([minNote:maxNote]./12);

  
    dV       = hzV - (np.ones((len(hzV),)) * hz)
    i        = np.argmin( np.abs(dV))
    octave   = np.floor( i / 12 ) - 1
    pitchV   = kV if flat_fl else lV
    accV     = fV if flat_fl else sV
    letterCh = pitchV[np.mod( i, 12 )]
    accCh    = accV[np.mod(i,12)]

    if accCh == ' ':
        str = "%c%i" % (letterCh,octave)
    else:
        str = "%c%c%i" % (letterCh,accCh,octave)
  
    return str

def to_sci_pitch( midi, flat_fl = False ):
    return hz_to_sci_pitch(to_hz(midi),flat_fl)

def sci_pitch_to_midi( sciPitch ):
    """ Given scientific pitch as a string return the parsed reprentation:
    <pitch_class>,<alter>,<octave> where:
    <pitch_class> is in A,B,C,D,E,F or G
    <alter> is in  -1,0,1 (flat,natural,sharp)
    <octave> integer octave
    """

    assert( 2 <= len(sciPitch) and len(sciPitch) <= 3 )
    
    octave = None
    alter = 0

    pitch_class = sciPitch[0]

    if sciPitch[1] == '#':
        alter = 1
    elif sciPitch[1] == 'b':
        alter = -1
    elif sciPitch[1] == ' ':
        alter = 0
    elif sciPitch[1].isdigit():
        octave = int(sciPitch[1])

    if octave is None:
        octave = int(sciPitch[2])

    assert( pitch_class.upper() in 'ABCDEFG' and octave is not None)

    return pitch_class,alter,octave


def is_note_on(d):
    return d['status'] == const.noteOnSt and d['d1'] is not None and d['d1']>0

def is_note_off(d):
    return d['status'] == const.noteOffSt or (d['status']==const.noteOnSt and d['d1'] is not None and d['d1']==0)

def is_ctl(d):
    return d['status'] == const.ctlSt


def is_note_on(m):
    return m['status']==const.noteOnSt and m['d1']>0

def is_note_off(m):
    return (m['status']==const.noteOnSt and m['d1']==0) or m['status'] == const.noteOffSt


PEDAL_THRESH = 30

def is_damper(m):
    return  m['status']==const.ctlSt and m['d0']==const.sustainCId

def is_damper_down(m,thresh=PEDAL_THRESH):
    return  is_damper(m) and m['d1']>thresh

def is_damper_up(m,thresh=PEDAL_THRESH):
    return  is_damper(m) and m['d1']<=thresh

def is_sostenuto(m):
    return m['status']==const.ctlSt and m['d0']==const.sostenutoCId

def is_sostenuto_down(m,thresh=PEDAL_THRESH):
    return is_sostenuto(m)  and m['d1']>thresh

def is_sostenuto_up(m,thresh=PEDAL_THRESH):
    return  is_sostenuto(m) and m['d1']<=thresh

    
