#!/usr/bin/env python
# *-* coding:utf-8 *-*

""" TriViSiJu: Graphical interface for the AstroJeune Festival
    
	Copyright (C) 2012  Jules DAVID, Tristan GREGOIRE, Simon NICOLAS and Vincent PRAT

	This file is part of TriViSiJu.

    TriViSiJu is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    TriViSiJu is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TriViSiJu.  If not, see <http://www.gnu.org/licenses/>.
"""

import pygtk
pygtk.require("2.0")
import gtk

class promptBox(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)

        # Créations des widgets
        self.entry = gtk.Entry()
        self.entry.set_text(">")
        self.result = gtk.TextView()
        self.result.set_editable(False)
        self.result.set_cursor_visible(False)

        resultWindow = gtk.ScrolledWindow()
        resultWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        resultWindow.add(self.result)

        # Insertion des widgets dans la boîte
        self.pack_start(self.entry,expand=False,fill=True)
        self.pack_start(resultWindow,expand=True,fill=True)

        # Buffer du textView
        self.buffer = self.result.get_buffer()

        # Connexion des signaux
        self.entry.connect("activate",self.parseEntry)

    def parseEntry(self, entry):
        self.buffer.insert(self.buffer.get_end_iter(), entry.get_text() + "\n")
        self.result.scroll_to_iter(self.buffer.get_end_iter(), 0)

if __name__ == "__main__":
    a = gtk.Window()
    a.set_default_size(400,100)
    a.set_position(gtk.WIN_POS_CENTER)
    a.connect("destroy", gtk.main_quit)
    
    box = promptBox()
    a.add(box)
    a.show_all()

    gtk.main()

