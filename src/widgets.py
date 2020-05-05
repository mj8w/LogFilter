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

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)


class MarkTextBox(tk.Text):
    def __init__(self,  *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.tags_lineNum = []
        self.tags_mark = []

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        # let the actual widget perform the requested action
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        # generate an event if something was added or deleted,
        # or the cursor position changed
        if (args[0] in ("insert", "replace", "delete") or 
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        # return what the actual widget returned
        return result   

    def AddLineNumTag(self, startLine, startChar, endLine, endChar):
        startStr = "{}.{}".format(startLine, startChar)
        endStr = "{}.{}".format(endLine, endChar)
        self.tags_lineNum.append((startStr, endStr))

    def AddMarkTag(self, startLine, startChar, endLine, endChar):
        startStr = "{}.{}".format(startLine, startChar)
        endStr = "{}.{}".format(endLine, endChar)
        self.tags_mark.append((startStr, endStr))

    def LoadData(self, file_contents):
        self.delete(1.0, tk.END)
        self.insert(tk.END, "".join(file_contents))
        
        for tag in self.tags_lineNum:
            start,end = tag
            self.tag_add('LineNum',start,end)
            
        for tag in self.tags_mark:
            start,end = tag
            self.tag_add('Mark',start,end)

        self.tag_configure('LineNum', foreground='blue')
        self.tag_configure('Mark', background='yellow')

        # remove the source data for the next load
        self.tags_lineNum = []
        self.tags_mark = []
