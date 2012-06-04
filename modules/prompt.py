#!/usr/bin/env python
# *-* coding:utf-8 *-*

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

        # Insertion des widgets dans la boîte
        self.pack_start(self.entry,expand=False,fill=True)
        self.pack_start(self.result,expand=True,fill=True)

if __name__ == "__main__":
    a = gtk.Window()
    a.set_default_size(400,100)
    a.set_position(gtk.WIN_POS_CENTER)
    a.connect("destroy", gtk.main_quit)
    
    box = promptBox()
    a.add(box)
    a.show_all()

    gtk.main()

