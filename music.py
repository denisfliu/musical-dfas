from re import T
import pygame.midi
import time
import threading
import random
from gui import *
import queue


dataQ = queue.SimpleQueue()

class Parser():
    def __init__(self, filename=['music.txt']):
        self.head_note = None
        self.volume = 0
        self.tempo = 0
        self.instruments = list()
        self.all_instruments = set()
        
        """
        Initializing variables used for reading.
        """
        self.store_next_repeat = False
        self.note = None
        self.repeat_num = 0
        self.volume_change = 0 # 1 is dim, 2 is cresc
        self.volume_change_amount = 1 # used for dim/cresc
        self.volume_override = False # used for volume within procedures
        self.instrument_override = False
        self.store_proc = False
        self.proc_name = ''
        self.sustain = False
        self.proc_dict = dict() # (procname: list of (halfstep list, dur))
        self.repeat_ref = None
        """
        Initialization done.
        """
        self.read(filename)

    def read(self, filename):
        lines = None
        with open(filename, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines[:3]):
            if i == 0:
                self.volume = int(line)
            elif i == 1:
                self.tempo = int(line)
            elif i == 2:
                self.instruments = list(map(lambda x: int(x), line.split()))
                self.all_instruments.update(self.instruments)
        for line in lines[3:]:
            # flush the new line                
            line = line[:-1]                
            split = line.split()
            if len(line) > 7 and line[:7] == 'brepeat':
                self.store_next_repeat = True
                self.repeat_num = int(line.split()[-1])
            elif line == 'erepeat':
                self.note.add_next_note(self.repeat_ref)
            elif line == 'sustain' or line == 'damper':
                self.sustain = True
            elif line == 'esustain' or line == 'edamper':
                self.sustain = False
            elif line == 'edim' or line == 'ecresc':
                self.volume_change = 0
            elif split[0] == 'tempo':
                self.tempo = int(split[1])
            elif split[0] == 'bdim':
                self.volume_change = 1
                self.volume_change_amount = float(split[1])
            elif split[0] == 'bcresc':
                self.volume_change = 2
                self.volume_change_amount = float(split[1])
            elif split[0] == 'instrument':
                self.instruments = list(map(lambda x: int(x), split[1:]))
                self.all_instruments.update(self.instruments)
            elif split[0] == 'volume':
                self.volume = int(split[1])
            elif split[0] == 'bproc':
                self.store_proc = True
                self.proc_name = split[1]
            elif split[0] == 'eproc':
                self.store_proc = False
            elif split[0] == 'exec':
                note_duration_list = line.split()
                proc = note_duration_list[-1]
                start_note = note_duration_list[-2][:-1]
                start_octave = note_duration_list[-2][-1]
                l = self.proc_dict[proc]
                Notes = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
                notes_keys_copy = list(Notes.keys()).copy()
                Notes.update({Notes[k]: k for k in Notes})
                if start_note[-1] == 'b':
                    start_note = f'{Notes[Notes[start_note[0]] - 2]}#'
                start_at = 0
                # overrides taken care of here
                if l[0] == 'voverride':
                    self.volume_override = True
                    start_at = start_at + 1
                if l[0] == 'ioverride':
                    self.instrument_override = True
                    start_at = start_at + 1
                for i, ((notes, volume, instruments, sustain), dur) in enumerate(l[start_at:]):
                    if self.volume_override:
                        volume = self.volume
                    if self.instrument_override:
                        instruments = self.instruments
                    # calculate note based on half step position
                    half_to_note = list(map(lambda x: notes_keys_copy[(Notes[start_note] + int(x)) % 12], notes))
                    # octave
                    def octave_helper(num):
                        if num < 0:
                            return -1 * int((-num) / 12 + 1)
                        else:
                            return int(num / 12)
                    half_to_octave = list(map(lambda x: int(start_octave) + octave_helper(Notes[start_note] + int(x)), notes))
                    combine = [x + str(y) for x, y in zip(half_to_note, half_to_octave)]
                    self.add_note(Note(note=combine, volume=volume, instruments=instruments, duration=self.calculate_tempo(dur), max_repeats=self.repeat_num, sustain=sustain, proc_name=proc))
                    # dim/cresc 
                    if self.volume_change == 1:
                        self.volume = int(self.volume / (self.volume_change_amount ** i))
                    elif self.volume_change == 2:
                        self.volume = min(int(self.volume * (self.volume_change_amount ** i)), 127)
            else:
                note_duration_list = line.split()
                if (note_duration_list[0] == 'voverride' or note_duration_list[0] == 'ioverride'):
                    self.proc_dict[self.proc_name] = self.proc_dict.get(self.proc_name, list())
                    self.proc_dict[self.proc_name].append(note_duration_list[0])
                    continue
                dur = float(note_duration_list[-1])

                if not self.store_proc:
                    newNote = Note(note=note_duration_list[:-1], volume=self.volume, instruments=self.instruments.copy(), duration=self.calculate_tempo(dur), max_repeats=self.repeat_num, sustain=self.sustain, proc_name=note_duration_list[0])
                    self.add_note(newNote)
                else:
                    self.proc_dict[self.proc_name] = self.proc_dict.get(self.proc_name, list())
                    self.proc_dict[self.proc_name].append(((note_duration_list[:-1], self.volume, self.instruments.copy(), self.sustain), dur))

                # dim/cresc 
                if self.volume_change == 1:
                    self.volume = int(self.volume / self.volume_change_amount)
                elif self.volume_change == 2:
                    self.volume = min(int(self.volume * self.volume_change_amount), 127)
 
    def calculate_tempo(self, length_in_quarter_notes):
        return float(length_in_quarter_notes) / float(self.tempo) * 60.0

    def add_note(self, newNote):
        # if the previous note is none, we set the head note
        if self.note is None:
            self.head_note = newNote
        else:
            # set the alt_note to the same as next_note, so when repeats occur we
            # don't care
            # the case erepeats takes care of case where we want a repeat
            if self.note.next_note is None:
                self.note.next_note = newNote
            self.note.alt_note = newNote
        # store note reference for next note
        if self.store_next_repeat:
            self.repeat_ref = newNote
            self.store_next_repeat = False

        self.note = newNote

class Note():
    def __init__(self, note=['C4', 'E4', 'G4'], instruments=[0], volume=64, velocity=64, duration=.4, max_repeats=2, sustain=False, proc_name=''):
        self.note = note
        self.volume = volume
        self.instruments = instruments
        self.velocity = random.randint(velocity - 10, velocity + 10)
        self.duration = duration
        self.sustain = sustain
        self.next_note = None
        self.alt_note = None
        self.repeat = 0
        self.max_repeats = max_repeats
        self.midi_note = list(map(lambda x: self.string_to_midi(x), self.note))
        self.proc_name = proc_name

    def __str__(self):
        return f'Notes: {self.note}\nVolume: {self.volume}\nDuration: {self.duration}\n'

    def change_note(self, new_note):
        self.note = new_note
    
    def add_next_note(self, next_note):
        self.next_note = next_note
    
    # use this for repeats
    def to_next_note(self):
        if self.repeat == self.max_repeats:
            return self.alt_note
        self.repeat = self.repeat + 1
        if self.next_note is None:
            return None
        return self.next_note

    # https://stackoverflow.com/questions/13926280/musical-note-string-c-4-f-3-etc-to-midi-note-value-in-python 
    def string_to_midi(self, n):
        Notes = [["C"],["C#","Db"],["D"],["D#","Eb"],["E"],["F"],["F#","Gb"],["G"],["G#","Ab"],["A"],["A#","Bb"],["B"]]
        answer = 0
        i = 0
        #Note
        letter = n[:-1]
        for note in Notes:
            for form in note:
                if letter.upper() == form.upper():
                    answer = i
                    break
            i += 1
        #Octave
        answer += (int(n[-1]))*12
        return answer

class Notes2Music():
    def __init__(self, visualize=False, file_name=['music.txt']): 
        parsers = list(map(lambda x: Parser(x), file_name))
        self.starting_notes = list(map(lambda x: x.head_note, parsers))
        self.instruments = list(map(lambda x: x.all_instruments, parsers))
        self.visualize = visualize
        if self.visualize:
            self.app = App(filenames=file_name, s=self)
    # prints without repeats
    def print_notes(self):
        for start in self.starting_notes:
            n = start
            while n is not None:
                print(n)
                n = n.alt_note

    def play_notes(self, player, start_note, channel_dict, thread_num):
        # play sounds
        note = start_note
        next_call = self.next_call
        for channel in channel_dict.values():
            player.write_short(0xb0 + channel, 64, 127 if note.sustain else 0)
        while note is not None:
            for instrum in note.instruments:
                channel = channel_dict[instrum]
                for n in note.midi_note:
                    player.note_on(n, note.volume, channel)
            next_call = next_call + note.duration
            if self.visualize:
                dataQ.put((thread_num, note.proc_name), block=False)
            time.sleep(next_call - time.time())
            for instrum in note.instruments:
                channel = channel_dict[instrum]
                for n in note.midi_note:
                    player.note_off(n, note.volume, channel)
            note = note.to_next_note() 
        
    def play(self):
        pygame.midi.init()
        player = pygame.midi.Output(0, 1)
        
        channel_dict = dict()
        for instrum in self.instruments:
            for ins in instrum:
                if ins not in channel_dict:
                    channel_dict[ins] = len(channel_dict)
                    player.set_instrument(ins, len(channel_dict) - 1)
        threads = []
        for i, (start_note, instrum) in enumerate(zip(self.starting_notes, self.instruments)):
            threads.append(threading.Thread(target=self.play_notes, args=(player, start_note, channel_dict, i)))
        self.next_call = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        del player
        pygame.midi.quit()

    def play_without_multithreading(self):
        pygame.midi.init()
        player = pygame.midi.Output(0, 1)
        channel_dict = dict()
        for ins in self.instruments[0]:
            channel_dict[ins] = len(channel_dict)
        self.play_notes(player, self.starting_notes[0], channel_dict)
            
    def is_digit(self, num):
        return num == '0' or num == '1' or num == '2' or num == '3' or num == '4' or num == '5' or num == '6' or num == '7' or num == '8' or num == '8' or num == '9'

class App(tk.Tk):
    def __init__(self, filenames, s):
        super().__init__()
        self.s = s
        self.title('Main')
        self.windows = list()
        self.canvases = list()
        self.geometry("350x30")
        for filename in filenames:
            self.open_window(filename)
        button = tk.Button(self, text='Play', command=self.start_playback)
        button.pack()
    
    def start_playback(self):
        self.play_thread = threading.Thread(target=self.s.play)
        self.play_thread.start()
        self.after(10, self.on_after_elapsed)

    def on_after_elapsed(self):
        try:
            value = dataQ.get(block=False)
            if value is None:
                return
        except queue.Empty:
            self.after(10, self.on_after_elapsed)
            return
        canvas_num, proc_name = value
        self.canvases[canvas_num].change_circle(proc_name)
        self.after(10, self.on_after_elapsed)

    def open_window(self, filename, width=1280):
        window = tk.Toplevel(self)
        visualizer = Visualizer(filename, window, width)
        self.canvases.append(visualizer)
        window.geometry(f'{width}x{int(math.ceil(visualizer.height))}')
        self.windows.append(window)
        # Pack the canvas to the main window and make it expandable
        visualizer.pack(fill = tk.BOTH)
        window.title(filename)

if __name__ == '__main__':
    # order must be shorter to longest or problems with the multithreading happen
    #s = Notes2Music(['gff_woodwind.txt'])
    #s = Notes2Music(['gff_harp.txt'])
    #s = Notes2Music(['music.txt'])
    #s.print_notes()
    #s.play_without_multithreading()

    s = Notes2Music(visualize=True, file_name=['gff_harp.txt', 'gff_woodwind.txt'])
    #s = Notes2Music(visualize=True, file_name=['gff_woodwind.txt'])
    #s = Notes2Music(visualize=True, file_name=['gff_harp.txt'])
    s.app.mainloop()
    dataQ.put(None)
    s.app.play_thread.join()

    
    #master.geometry("330x220 + 300 + 300")
    #app = App()
    #app.mainloop()
    