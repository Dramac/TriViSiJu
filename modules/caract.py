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
import gobject
import codecs
import re

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

class caractBox(gtk.VBox):
    def __init__(self,fichier="data/caract.txt"):
        ## Initialise gtk.VBox, gtk.HBox
        gtk.VBox.__init__(self)

        self.lines = codecs.open(fichier, encoding="utf-8").readlines()
        self.delay = 1000
        self.max_line = 30
        self.width = 50
        self.timer = None
        self.cursor = 0

        gobject.signal_new("message",caractBox,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING])

        self.text = gtk.Label()
        self.add(self.text)

    def start(self,sender=None):
        if self.timer is None:
            self.timer = gobject.timeout_add(self.delay,self.on_timeout)

    def append(self,text_to_append):
        """Ajouter du texte à la fin du texte déjà écrit"""

        # On ne garde que le N dernières lignes
        previous_text = self.text.get_label().split("\n")
        if len(previous_text) > self.max_line:
            previous_text = previous_text[-self.max_line:]
        previous_text = "\n".join(previous_text)

        # On supprime la mise en forme générale, qui vient perturber l'insertion
        ## d'abord le début
        previous_text = previous_text.replace("<span font_desc='Monospace'>","",1)
        ## puis la fin
        previous_text = rreplace(previous_text,"</span>","",1)

        # On comble en points jusqu'à obtenir la taille de ligne désirée
        if len(text_to_append) <= self.width - 4:
            dots = "".join(["." for i in range(self.width - len(text_to_append) - 4)])
            text_to_append = text_to_append.replace("\n","") + dots + "[<span foreground='green'>OK</span>]\n"

        # Puis on met le tout en forme (police à chasse fixe)
        next_text = "<span font_desc='Monospace'>"+previous_text+str(text_to_append)+"</span>"
        # et on affiche !
        self.text.set_markup(next_text)

    def on_timeout(self, *args):
        line = self.lines[self.cursor]
        self.append(line)
        self.cursor += 1
        if self.cursor >= len(self.lines):
            self.cursor = 0
        return True         #Nécessaire pour le timeout_add




if __name__ == "__main__":
    gobject.threads_init()
    a = gtk.Window()
    a.set_default_size(400,100)
    a.set_position(gtk.WIN_POS_CENTER)
    a.connect("destroy", gtk.main_quit)

    box = caractBox("../data/caract.txt")
    box.start()
    a.add(box)
    a.show_all()

    gtk.main()

