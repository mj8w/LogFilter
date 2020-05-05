'''
    Copyright 2020 Micheal Wilson - mail4mikew@gmail.com

    This software is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    It is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import tkinter as tk
from tkinter import filedialog as fd 
from tkinter import ttk
import re

import string
from config import filter_options, marker_options
from widgets import MarkTextBox, TextLineNumbers

printable = set(string.printable)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.Filter_Re = tk.StringVar()
        self.Mark_Re = tk.StringVar()
        self.available_filters = filter_options
        self.available_markers = marker_options
        self.pack()
        self.create_widgets()
        self.file_contents = []
        self.line_map = []          # for each filtered line displayed, the original line #  
        
    def LoadFileWithFilter(self):
        try:
            total_lines = len(self.file_contents)
            first, last = [val*total_lines for val in self.textbox.yview()]
            if last < 1: 
                first_to_show = 1
            else: 
                first_to_show = self.line_map[int(first)]            # line number to align display to after it is loaded
            print("first to show {}".format(first_to_show))
            
            self.file_contents = []
            self.line_map = [] 
            element = str( self.Filter_Re.get())
            marking = str(self.Mark_Re.get())
            print("Element selected '{}'".format(element))
            lineNum = 1
            locateLineNum = 1
            with open(self.filename, "r") as input_file:
                lines = input_file.readlines()
                
                for line in lines:  
                    line = re.sub(r'[^\x09-\x7f]',r'.', line)
                    lineNumStr = ("    {}".format(lineNum))[-5:]
                    keep = re.search(element, line)
                    if keep:
                        if self.HaveLineNums.get() == "on":
                            line = " ".join([lineNumStr, line])
                            self.file_contents.append(line)
                            self.line_map.append(lineNum)
                            self.textbox.AddLineNumTag(locateLineNum,0,locateLineNum,5)
                        else:
                            self.file_contents.append(line)
                            self.line_map.append(lineNum)
                        
                        for will_mark in re.finditer(marking, line):
                            print(locateLineNum,will_mark.start(),locateLineNum,will_mark.end())
                            self.textbox.AddMarkTag(locateLineNum,will_mark.start(),locateLineNum,will_mark.end())                        
                            
                        locateLineNum += 1
                    lineNum += 1
                        
                self.textbox.LoadData(self.file_contents)
                
                for i,lineNum in enumerate(self.line_map):
                    if lineNum >= first_to_show:
                        first = float(i)/float(len(self.line_map))
                        print("Restore show {} ({} of {} lines".format(first, i, len(self.line_map)))
                        # self.textbox.see("{}.{}".format(i,0))
                        self.textbox.yview_moveto(first)
                        break
                
        except AttributeError:
            pass

        """
        from ScrolledText import ScrolledText
        s=ScrolledText()
        s.pack(fill='both', expand=1)
        s.insert('end', some_text)
        first, last = s.yview()
        s.delete(1.0, 'end')
        s.insert('end', some_text)
        s.yview_moveto(first)
        """

    def GetFileName(self):
        self.filename= fd.askopenfilename(filetypes=(("Logs", ".log"), ("All files","*.*"))) 
        print(self.filename)
        self.master.title(self.filename) # change the title of the app to a label of this filename
        self.LoadFileWithFilter()        
        
    def on_filter_combo_select(self, event):
        (event)
        element = self.Filter_Re.get()
        print("Element selected '{}'".format(element))
        self.LoadFileWithFilter()

    def on_marker_combo_select(self, event):
        (event)
        element = self.Mark_Re.get()
        print("Marker selected '{}'".format(element))
        self.LoadFileWithFilter()

    def OnHaveLineNumsChanged(self):
        print(self.HaveLineNums.get())
        self.LoadFileWithFilter()

    def on_keypress_filters(self, event):
        if event.char == '\r':
            self.on_apply_filters()

    def on_keypress_markers(self, event):
        if event.char == '\r':
            self.on_apply_markers()

    def on_apply_filters(self):
        element = self.Filter_Re.get()
        print("Element selected '{}'".format(element))
        self.available_filters.append(element)
        self.available_filters = list(set(self.available_filters))  # remove copies
        self.filter_re['values'] = self.available_filters
        self.LoadFileWithFilter()

    def on_apply_markers(self):
        element = self.Mark_Re.get()
        print("Element selected '{}'".format(element))
        self.available_markers.append(element)
        self.available_markers = list(set(self.available_markers))  # remove copies
        self.marker_re['values'] = self.available_markers
        self.LoadFileWithFilter()
        
    def _on_change(self, event):
        self.linenumbers.redraw()
        
    def create_textbox_frame(self):
        self.textbox_frame = tk.Frame(self.master)    

        # textbox with a scroll bar        
        self.textbox = MarkTextBox(self.textbox_frame)
        
        self.scroll = tk.Scrollbar(self.textbox_frame, command = self.textbox.yview)
        self.textbox.configure(yscrollcommand=self.scroll.set)
        
        self.linenumbers = TextLineNumbers(self.textbox_frame, width=40)
        self.linenumbers.attach(self.textbox)

        # place the scrollbar next to the text box
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.linenumbers.pack(side="left", fill="y")
        self.textbox.pack(side="right", fill="both", expand=True)
        # self.textbox.pack(side=tk.LEFT, expand = tk.YES, fill=tk.BOTH)       
        self.textbox.bind("<<Change>>", self._on_change)
        self.textbox.bind("<Configure>", self._on_change)

    def create_widgets(self):

        self.create_textbox_frame()
        self.textbox_frame.pack(side=tk.BOTTOM, expand = tk.YES, fill=tk.BOTH)

        # options frame goes on the top & contains a number of widgets
        self.options_frame = tk.Frame(self.master, borderwidth=5)
        self.options_frame.pack(side=tk.LEFT)

        # ROW 0

        # file dialog button
        self.file_select = tk.Button(self.options_frame, text='File Open', command=self.GetFileName)
        self.file_select.grid(row=0, column=0)

        # label
        tk.Label(self.options_frame, text="Filter Lines (RegEx)", padx = 5, pady = 5).grid(row=0, column=1)
        
        # combo box
        self.filter_re = ttk.Combobox(self.options_frame, values=self.available_filters, textvariable = self.Filter_Re)
        self.filter_re.grid(row=0, column=2)
        self.filter_re.current(0)
        self.filter_re["width"] = 60
        self.filter_re.bind("<<ComboboxSelected>>", self.on_filter_combo_select)
        self.filter_re.bind("<Key>", self.on_keypress_filters)

        # Apply filters button
        self.apply = tk.Button(self.options_frame)
        self.apply["text"] = "Apply"
        self.apply["command"] = self.on_apply_filters
        self.apply.grid(row=0, column=3)
              
        # ROW 1

        # Linenum checkbox
        self.HaveLineNums = tk.StringVar()
        self.HaveLineNums.set("on")
        self.LineNumCheck = ttk.Checkbutton(self.options_frame,
        variable = self.HaveLineNums, 
        text='Line #s',
        command=self.OnHaveLineNumsChanged, onvalue='on', offvalue='off')
        self.LineNumCheck.grid(row=1, column=0)

        # label
        tk.Label(self.options_frame, text="Mark Text (RegEx)").grid(row=1, column=1)
        
        # combo box
        self.marker_re = ttk.Combobox(self.options_frame, values=self.available_markers, textvariable = self.Mark_Re)
        self.marker_re.grid(row=1, column=2)
        self.marker_re.current(0)
        self.marker_re["width"] = 60
        self.marker_re.bind("<<ComboboxSelected>>", self.on_marker_combo_select)
        self.marker_re.bind("<Key>", self.on_keypress_markers)
        
        # Apply markers button
        self.apply = tk.Button(self.options_frame)
        self.apply["text"] = "Apply"
        self.apply["command"] = self.on_apply_markers
        self.apply.grid(row=1, column=3)

                

root = tk.Tk()
app = Application(master=root)
app.mainloop()