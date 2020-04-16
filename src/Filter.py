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
        self.file_contents = ""
        
    def LoadFileWithFilter(self):
        try:
            file_contents = []
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
                            file_contents.append(line)
                            self.textbox.AddLineNumTag(locateLineNum,0,locateLineNum,5)
                        else:
                            file_contents.append(line)
                        
                        for will_mark in re.finditer(marking, line):
                            print(locateLineNum,will_mark.start(),locateLineNum,will_mark.end())
                            self.textbox.AddMarkTag(locateLineNum,will_mark.start(),locateLineNum,will_mark.end())                        
                            
                        locateLineNum += 1
                    lineNum += 1
                        
                self.textbox.LoadData(file_contents)
                
        except AttributeError:
            pass

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
        
        self.linenumbers = TextLineNumbers(self.textbox_frame, width=30)
        self.linenumbers.attach(self.textbox)

        # place the scrollbar next to the text box
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.linenumbers.pack(side="left", fill="y")
        self.textbox.pack(side="right", fill="both", expand=True)
        # self.textbox.pack(side=tk.LEFT, expand = tk.YES, fill=tk.BOTH)       
        self.textbox.bind("<<Change>>", self._on_change)
        self.textbox.bind("<Configure>", self._on_change)

    def create_filter_frame(self):
        self.filter_frame = tk.Frame(self.master)

        # file dialog button
        self.file_select = tk.Button(self.filter_frame, text='File Open', command=self.GetFileName)
        self.file_select.pack(side=tk.LEFT)
                
        # label
        tk.Label(self.filter_frame, text="Filter Lines (RegEx)").pack(side=tk.LEFT)
        
        # Apply filters button
        self.apply = tk.Button(self.filter_frame)
        self.apply["text"] = "Apply"
        self.apply["command"] = self.on_apply_filters
        self.apply.pack(side=tk.RIGHT)

        # combo box
        self.filter_re = ttk.Combobox(self.filter_frame, values=self.available_filters, textvariable = self.Filter_Re)
        self.filter_re.pack(side=tk.RIGHT, fill=tk.X)
        self.filter_re.current(0)
        self.filter_re["width"] = 60
        self.filter_re.bind("<<ComboboxSelected>>", self.on_filter_combo_select)
        self.filter_re.bind("<Key>", self.on_keypress_filters)

    def create_markers_frame(self):
        self.markers_frame = tk.Frame(self.master)

        # label
        tk.Label(self.markers_frame, text="Mark Text (RegEx)").pack(side=tk.LEFT)
        
        # Apply markers button
        self.apply = tk.Button(self.markers_frame)
        self.apply["text"] = "Apply"
        self.apply["command"] = self.on_apply_markers
        self.apply.pack(side=tk.RIGHT)

        # combo box
        self.marker_re = ttk.Combobox(self.markers_frame, values=self.available_markers, textvariable = self.Mark_Re)
        self.marker_re.pack(side=tk.RIGHT, fill=tk.X)
        self.marker_re.current(0)
        self.marker_re["width"] = 60
        self.marker_re.bind("<<ComboboxSelected>>", self.on_marker_combo_select)
        self.marker_re.bind("<Key>", self.on_keypress_markers)
                
    def create_widgets(self):
              
        # Linenum checkbox
        self.HaveLineNums = tk.StringVar()
        self.HaveLineNums.set("on")
        self.LineNumCheck = ttk.Checkbutton(self.master,
        variable = self.HaveLineNums, 
        text='Incl. Line Numbers',
        command=self.OnHaveLineNumsChanged, onvalue='on', offvalue='off')
        self.LineNumCheck.pack(side=tk.BOTTOM)

        self.create_filter_frame()
        self.filter_frame.pack(side=tk.BOTTOM)

        self.create_markers_frame()
        self.markers_frame.pack(side=tk.BOTTOM)

        self.create_textbox_frame()
        self.textbox_frame.pack(side=tk.BOTTOM, expand = tk.YES, fill=tk.BOTH)

root = tk.Tk()
app = Application(master=root)
app.mainloop()