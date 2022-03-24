import math
from tkinter import ttk
import tkinter as tk


# used to be tk.Toplevel
class Visualizer(tk.Canvas):
    def __init__(self, filename, main=None, width=1280):
        super().__init__(main)
        self.filename = filename
        self.procedure_dict = dict() # everything will be a procedure, even regular notes
        self.order_of_states = list() # the order that the notes will follow
        self.calculate_dfa() # populates order of states and procedure dict
        self.notes_to_print = list() # prepares a list to print the notes
        self.init_notes() # initializes the notes to print
        self.counter = 0 # counter for changing color of circles
        self.global_counter = 0 # counter for changing colors while changing colors
        self.previous_fill = None # previous circle filled
        self.procedure_space = dict() # dict of (radius for procedure + radii in (right side))
        self.horizontal_length, self.vertical_length = self.prepare_circles()
        # for scaling
        self.width = width 
        self.height = self.radius(self.vertical_length)
        self.config(width=self.width, height=self.height)
        self.bind("<Configure>", self.on_resize)
        self.circles = dict() # proc_name plus circles (same as procedure_dict)
        self.create()
    
    # https://stackoverflow.com/questions/22835289/how-to-get-tkinter-canvas-to-dynamically-resize-to-window-width
    def on_resize(self, event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

    def create(self):
        # Creates a object of class canvas
        # with the help of this we can create different shapes
        #self.canvas = tk.Canvas(self)

        # Creates a circle of diameter 80
        #self.canvas.
        y_center = self.scale_y(.5)
        for group in set(self.order_of_states):
            x_center = self.radius(self.procedure_space[group][1] - (self.procedure_space[group][1] - self.procedure_space[group][2]) / 2)
            total_size = len(self.procedure_dict[group])
            big_radius = self.radius(self.procedure_space[group][0])
            self.circles.setdefault(group, list())
            for n in range(total_size):
                x, y = self.calculate_circle_center(x_center, y_center, n + 1, total_size, big_radius)
                circle = self.create_oval(x - self.radius(1), y - self.radius(1), x + self.radius(1), y + self.radius(1))
                self.circles[group].append(circle)             
                
    def calculate_circle_center(self, x_center, y_center, nth_circle, total_circles, big_r):
        radians = ((2 * math.pi) / total_circles) * (nth_circle-1) + math.pi / 2       
        return x_center + big_r * math.cos(radians) - self.radius(1), y_center + big_r * math.sin(radians) - self.radius(1)
    
    def calculate_dfa(self):
        lines = None
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            if i < 3:
                i += 1
                continue
            if lines[i].split()[0] == 'bproc':
                procedure_name = lines[i].split()[1]
                while lines[i].split()[0] != 'eproc':
                    if lines[i].split()[0].isnumeric() or lines[i].split()[0][1].isnumeric():
                        self.procedure_dict.setdefault(procedure_name, list())
                        self.procedure_dict[procedure_name].append(int(lines[i].split()[0]))
                    i += 1
            elif lines[i].split()[0] == 'exec':
                procedure_name = lines[i].split()[2]
                self.order_of_states.append(procedure_name)
            elif self.is_note(lines[i].split()[0]):
                procedure_name = lines[i].split()[0]
                self.order_of_states.append(procedure_name)
                self.procedure_dict.setdefault(procedure_name, list())
                if len(self.procedure_dict[procedure_name]) != 1:
                    self.procedure_dict[procedure_name].append(0)
            i += 1
    
    def is_note(self, note):
        fchar = note[0]
        return fchar.isnumeric() or fchar == 'A' or fchar == 'B' or fchar == 'C' or fchar == 'D' or fchar == 'E' or fchar == 'F' or fchar == 'G'

    def init_notes(self):
        play_counter = 0
        dictionary_play_counter = 0
        while (play_counter != len(self.order_of_states)):
            dict_list = self.procedure_dict[self.order_of_states[play_counter]]
            self.notes_to_print.append(dict_list[dictionary_play_counter])
            dictionary_play_counter += 1
            if dictionary_play_counter == len(dict_list):
                dictionary_play_counter = 0
                play_counter += 1                    
    
    def print_note(self):
        print(self.notes_to_print[self.counter])
        self.counter += 1

    def change_circle(self, proc_name, fill=['green', 'cyan', 'red', 'violet'], on=True):
        if not on:
            if self.previous_fill is not None:
                self.itemconfig(self.previous_fill, fill='white')
            return
        fill = fill[self.global_counter % len(fill)]
        self.itemconfig(self.circles[proc_name][self.counter], fill=fill)       
        self.previous_fill = self.circles[proc_name][self.counter]
        self.counter += 1
        self.global_counter += 1
        if self.counter == len(self.circles[proc_name]):
            self.counter = 0
            
    """
     The formula: For a dict with more than one circle, we want
      the first circle to start at the bottom.
      1 circle: circle w/ big circle radius 0
      2-3 circles: circles w/ big circle radius 3*radius
      4-8 circles: circles w/ big circle radius 5*radius, etc
      The space allocated to a group of circles should be 3.5 radii of big circle horizontally
      and 3.3 radii vertically unless size is 1
    """
    def prepare_circles(self):
        hasVisited = set()
        horizontal_length = 0 # horizontal length in terms of radii
        biggest_group = 0 # biggest group to determine vertical length in terms of radii
        vertical_length = 0
        prev = 0
        for group in self.order_of_states:
            if group not in hasVisited:
                hasVisited.add(group)
                number_of_circles = len(self.procedure_dict[group])
                biggest_group = max(biggest_group, number_of_circles)
                s = int(math.sqrt(number_of_circles))
                if number_of_circles == 1:
                    s = 0
                self.procedure_space.setdefault(group, (0, 0))
                radius = s * 2 + 1 if s != 0 else 0
                hor_len =  radius * 2 + 6
                prev = horizontal_length
                horizontal_length += hor_len
                self.procedure_space[group] = (radius, horizontal_length, prev)

        s = int(math.sqrt(biggest_group))
        # ignore the case whre biggest_group = 1
        vertical_length = 3.3 * (2*s + 1)
        return horizontal_length, vertical_length                 

    def radius(self, radii):
        return radii * self.width / self.horizontal_length

    def scale_x(self, x):
        return self.winfo_reqwidth() * x
    
    def scale_y(self, y):
        return self.winfo_reqheight() * y

        
class TestApp(tk.Tk):
    def __init__(self, filenames):
        super().__init__()
        self.title('Main')
        self.windows = list()
        self.canvases = list()
        for filename in filenames:
            self.open_window(filename)
    
    def open_window(self, filename, width=1280, height=350):
        window = tk.Toplevel(self)
        window.geometry(f'{width}x{height}')
        self.windows.append(window)
        visualizer = Visualizer(filename, window, width, height)
        self.canvases.append(visualizer)
        window.title(filename)

if __name__ == '__main__':
    app = TestApp(['gff_harp.txt', 'gff_woodwind.txt'])
    app.mainloop()