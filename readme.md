# Musical DFAs
A variety of example text files are provided in the music folder that explain how to write music that is interpretable by the parser. For some example pieces, see the following demonstration videos:   
  
[Great Fairy Fountain](https://youtu.be/Qk7qNtPA7xk)  
[Mirror Temple (Mirror Magic Mix)](https://youtu.be/qxxRMfcM5_k)  
[General](https://youtu.be/VDsemZ05V7o)  
## Functions
1. bdim n, edim (diminuendo)
2. bcresc n, ecresc (crescendo)
3. brepeat n, erepeat (repeat)
4. bproc name, eproc (define procedure)  
    4a. voverride (overrides volume of procedure and uses volume of main)  
    4b. ioverride (overrides instrument of procedure and uses instrument of main)
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
Drums follow a numbering scheme that can be referenced here: https://en.wikipedia.org/wiki/General_MIDI#Percussion.
