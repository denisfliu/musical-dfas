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
## Order
Line 1: Starting Volume
Line 2: Tempo 
Line 3: Instruments
Line 4-end: Music to Play (note duration | function)


# TODO
Repeat stack to allow for nested repeats