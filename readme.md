# Music
## Funcs
1. bdim n, edim (diminuendo)
2. bcresc n, ecresc (crescendo)
3. brepeat n, erepeat (repeat)
4. bproc name, eproc (define procedure)
    4a. voverride (overrides volume of procedure and uses volume of main)
5. exec name starting_note (execute procedure)
6. instrument x y z (change instruments)
7. volume n (set volume)
8. sustain/damper, esustain/edamper (pedal)
9. tempo n (change tempo)

## Comments
1. Empty lines are now skipped.
2. Hashtags comment lines out.
## Order
Line 1: Starting Volume
Line 2: Tempo 
Line 3: Instruments/Drums
Line 4-end: Music to Play (note duration | function)

## Drums
1. Acoustic Bass Drum -- B1
2. Electric Bass Drum -- C2
3. Side Stick -- C#2
4. Acoustic Snare -- D2 
5. Hand Clap -- D#2
6. Electric Snare -- E2
7. Low Floor Tom -- F2
8. Closed Hi-hat -- F#2
9. High Floor Tom -- G2
10. Pedal Hi-hat -- G#2
11. Low Tom -- A2
12. Open Hi-hat -- A#2
11. Low-Mid Tom -- B2
12. Hi-Mid Tom  -- C3
13. Crash Cymbal 1 -- C#3
14. See the following wikipedia link for more: https://en.wikipedia.org/wiki/General_MIDI.

# TODO
Repeat stack to allow for nested repeats