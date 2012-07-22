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
    def __init__(self,file="data/caract.txt",delay=1000,max_line=15,width=35,foreground="white"):
        ## Initialise gtk.VBox, gtk.HBox
        gtk.VBox.__init__(self)

        self.lines = codecs.open(file, encoding="utf-8").readlines()
        self.delay = int(delay)          # Temps en ms entre deux appels de la fonction onTimeout
        self.max_line = int(max_line)    # Nombre de lignes à afficher au maximum
        self.width = int(width)          # Nombre de caractères par lignes
        self.phase = "init"         # si init, affiche des NO rouges, sinon affiche des OK verts
        self.timer = None
        self.cursor = 0
        self.foreground = foreground

        self.text = gtk.Label()
        self.text.set_alignment(0,0)
        self.add(self.text)

    def start(self,sender=None):
        if self.timer is None:
            self.timer = gobject.timeout_add(self.delay,self.onTimeout)

    def pause(self,sender=None):
        if self.timer:
            gobject.source_remove(self.timer)
            self.timer = None

    def changeMaxLine(self,sender,new_max_line):
        self.max_line = int(new_max_line)

    def changeWidth(self,sender,new_width):
        self.width = int(new_width)

    def changePhase(self,sender=None):
        if self.phase == "init":
            self.phase = "clear"
        else:
            self.phase = "init"

    def append(self,text_to_append):
        """Ajouter du texte à la fin du texte déjà écrit"""

        # On ne garde que les N dernières lignes
        previous_text = self.text.get_label().split("\n")
        if len(previous_text) > self.max_line:
            previous_text = previous_text[-self.max_line:]
        previous_text = "\n".join(previous_text)

        # On supprime la mise en forme générale, qui vient perturber l'insertion
        ## d'abord le début
        previous_text = previous_text.replace("<span foreground='"+self.foreground+"' font_desc='Monospace'>","",1)
        ## puis la fin
        previous_text = rreplace(previous_text,"</span>","",1)

        # On comble en points jusqu'à obtenir la taille de ligne désirée
        if len(text_to_append) <= self.width - 4:
            dots = "".join(["." for i in range(self.width - len(text_to_append) - 4)])
            if self.phase == "init":
                text_to_append = text_to_append.replace("\n","") + dots + "[<span foreground='red'>NO</span>]\n"
            else:
                text_to_append = text_to_append.replace("\n","") + dots + "[<span foreground='green'>OK</span>]\n"

        # Puis on met le tout en forme (police à chasse fixe)
        next_text = "<span foreground='"+self.foreground+"' font_desc='Monospace'>"+previous_text+str(text_to_append)+"</span>"
        # et on affiche !
        self.text.set_markup(next_text)

    def onTimeout(self, *args):
        """Fonction appelée toutes les self.delay ms"""
        line = self.lines[self.cursor]
        self.append(line)
        self.cursor += 1
        if self.cursor >= len(self.lines):
            self.cursor = 0
        return True         # Si True, continue

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

