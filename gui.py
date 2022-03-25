import math
import random
from tkinter import ttk
import tkinter as tk


# used to be tk.Toplevel
class Visualizer(tk.Canvas):
    def __init__(self, filename, main=None, width=1280):
        super().__init__(main)
        self.filename = filename
        self.procedure_dict = dict() # everything will be a procedure, even regular notes
        self.order_of_states = list() # the order that the notes will follow
        self.largest_radius = 0 # the largest procedure radius
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
        self.configure(bg='white')
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
        arrowshape = (5, 8, 2)
        # Creates the circles
        y_center = self.scale_y(.5)
        for group in set(self.order_of_states):
            x_center = self.radius(self.procedure_space[group][1] - (self.procedure_space[group][1] - self.procedure_space[group][2]) / 2)
            total_size = len(self.procedure_dict[group])
            big_radius = self.radius(self.procedure_space[group][0])
            self.circles.setdefault(group, list())
            for n in range(total_size):
                x, y = self.calculate_circle_center(x_center, y_center, n + 1, total_size, big_radius)
                circle = self.create_oval(x - self.radius(1), y - self.radius(1), x + self.radius(1), y + self.radius(1))
                self.itemconfig(circle, fill='black')
                self.circles[group].append(circle)             
        # creates the lines
        prev_x_center = None
        prev_y_center = None
        prev_group = None
        group_connections = dict()
        for group in (self.order_of_states):
            group_connections.setdefault(group, set())
            x_center = self.radius(self.procedure_space[group][1] - (self.procedure_space[group][1] - self.procedure_space[group][2]) / 2)
            total_size = len(self.procedure_dict[group])
            big_radius = self.radius(self.procedure_space[group][0])
            half_little_circle_angle = math.acos(- 1 * (self.radius(1) ** 2 - 2 * (big_radius**2))/(2*(big_radius**2))) * 180 / math.pi if total_size != 1 else 0
            angle_between_circles = 360.0 / total_size

            for n in range(total_size):
                if n == 0: 
                    if prev_group is not None:
                        if group in group_connections[prev_group]:
                            continue
                        group_connections[prev_group].add(group)
                        if prev_group == group:
                            if total_size == 1:
                                # self loop
                                loop_x_center = x_center + self.radius(15/16)
                                loop_y_center = y_center - self.radius(15/16)
                                start = 200
                                extent = -285 
                                radius_loop = self.radius(3/10)
                                arc = self.create_arc(loop_x_center - radius_loop, loop_y_center - radius_loop, loop_x_center + radius_loop, loop_y_center + radius_loop, start=start, extent=extent, style=tk.ARC)
                                angle_contact = -1 * (start + extent - 15) / 180 * math.pi
                                x_contact = loop_x_center + math.cos(angle_contact) * radius_loop
                                y_contact = loop_y_center + math.sin(angle_contact) * radius_loop
                                self.create_line(x_contact + 2, y_contact - 2, x_contact, y_contact, arrow=tk.LAST, arrowshape=(self.radius(1/12), self.radius(1/6), self.radius(1/12)))
                            else:
                                # complete the circle
                                start = -1 * (90 + half_little_circle_angle + (n - 1) * angle_between_circles)
                                extent = -1 * (angle_between_circles - 2 * half_little_circle_angle)
                                arc = self.create_arc(x_center - big_radius, y_center - big_radius, x_center + big_radius, y_center + big_radius, start=start, extent=extent,style=tk.ARC)

                                # little arrows
                                hlca_radians = half_little_circle_angle * math.pi / 180
                                abc_radians = angle_between_circles * math.pi / 180
                                goal_angle = math.pi / 2 + abc_radians * n - hlca_radians
                                x_end = x_center + big_radius * math.cos(goal_angle)
                                y_end = y_center + big_radius * math.sin(goal_angle)
                                x_temp = x_center + big_radius * math.cos(goal_angle - 1.0/30)
                                y_temp = y_center + big_radius * math.sin(goal_angle - 1.0/30)
                                d1 = 4 *math.sqrt((x_end - x_temp) ** 2 + (y_end - y_temp) ** 2)
                                arrowshape = (d1, d1 * math.sqrt(2), d1/2)
                                self.create_line(x_temp, y_temp, x_end, y_end, arrow=tk.LAST, arrowshape=arrowshape)
                        else:
                            # pick a random number that is between
                            # y_center + largest_radius and self.height
                            # the line will go DOWN to that number, horizontally
                            # to the target circle, and up into the bottom of the circle
                            # if going to the left, do something slightly different
                            rand = random.randint(int(y_center + self.radius(self.largest_radius) + 2 *self.radius(1)), int(self.height - self.radius(1) / 2))
                            special_case = (False, False)
                            if len(self.procedure_dict[group]) == 1 and len(self.procedure_dict[prev_group]) == 1:
                                special_case = (True, False)
                                if random.randint(0, 1) == 0:
                                    special_case = (True, True)
                                    rand = self.height - rand
                            if special_case[0]:
                                n_dict = {key: i for i, key in enumerate(self.procedure_dict)}
                                if n_dict[prev_group] + 1 == n_dict[group]:
                                    self.create_line(prev_x_center + self.radius(1), prev_y_center, x_center - self.radius(1), y_center, arrow=tk.LAST, arrowshape=arrowshape)
                                    continue
                            first_x_center, first_y_center = self.calculate_circle_center(x_center, y_center, n + 1, total_size, big_radius)
                            if first_x_center > prev_x_center:
                                x0 = prev_x_center
                                y0 = prev_y_center + self.radius(1)
                                if special_case[0] and special_case[1]:
                                    y0 = prev_y_center - self.radius(1)
                                x1 = x0 + self.radius(1)
                                y1 = rand
                                x2 = first_x_center
                                y2 = rand
                                x3 = first_x_center
                                y3 = first_y_center + self.radius(1)
                                if special_case[0] and special_case[1]:
                                    y3 = first_y_center - self.radius(1)
                                line = self.create_line(x0, y0, x1, y1, x2, y2, x3, y3, arrow=tk.LAST, arrowshape=arrowshape)
                            else:
                                x0, y0 = self.calculate_circle_center(prev_x_center, prev_y_center, 2, 10, self.radius(1))
                                if special_case[0] and special_case[1]:
                                    x0, y0 = self.calculate_circle_center(prev_x_center, prev_y_center, 4, 10, self.radius(1))
                                x1 = x0 - self.radius(1)
                                y1 = rand
                                x2 = first_x_center + self.radius(3) + random.uniform(-self.radius(1.5), self.radius(1.5))
                                y2 = rand
                                x3 = first_x_center + self.radius(1)
                                y3 = first_y_center
                                line = self.create_line(x0, y0, x1, y1, x2, y2, x3, y3, arrow=tk.LAST, arrowshape=arrowshape)
                    continue
                start = -1 * (90 + half_little_circle_angle + (n - 1) * angle_between_circles)
                extent = -1 * (angle_between_circles - 2 * half_little_circle_angle)
                arc = self.create_arc(x_center - big_radius, y_center - big_radius, x_center + big_radius, y_center + big_radius, start=start, extent=extent,style=tk.ARC)

                # little arrows
                hlca_radians = half_little_circle_angle * math.pi / 180
                abc_radians = angle_between_circles * math.pi / 180
                goal_angle = math.pi / 2 + abc_radians * n - hlca_radians
                x_end = x_center + big_radius * math.cos(goal_angle)
                y_end = y_center + big_radius * math.sin(goal_angle)
                x_temp = x_center + big_radius * math.cos(goal_angle - 1.0/30)
                y_temp = y_center + big_radius * math.sin(goal_angle - 1.0/30)
                d1 = 4 *math.sqrt((x_end - x_temp) ** 2 + (y_end - y_temp) ** 2)
                arrowshape = (d1, d1 * math.sqrt(2), d1/2)
                self.create_line(x_temp, y_temp, x_end, y_end, arrow=tk.LAST, arrowshape=arrowshape)


            prev_x_center, prev_y_center = self.calculate_circle_center(x_center, y_center, n + 1, total_size, big_radius)
            prev_group = group 
             
    def calculate_circle_center(self, x_center, y_center, nth_circle, total_circles, big_r):
        radians = ((2 * math.pi) / total_circles) * (nth_circle-1) + math.pi / 2       
        return x_center + big_r * math.cos(radians), y_center + big_r * math.sin(radians)
    
    def calculate_dfa(self):
        lines = None
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        
        i = 0
        repeat_flag = (0, False) # i, has_repeated
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
            elif lines[i].split()[0] == 'brepeat':
                repeat_flag = (i, False)
            elif lines[i].split()[0] == 'erepeat':
                if not repeat_flag[1]:
                    i = repeat_flag[0]
                    repeat_flag = (i, True)
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

    def change_circle(self, proc_name, fill=['#5eacbb', '#770088', '#bb062a', '#ef3d50', '#2a2758'], on=True):
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
                self.largest_radius = max(radius, self.largest_radius)
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
