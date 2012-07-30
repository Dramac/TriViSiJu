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

class EnigmeBox(gtk.VBox):
    """ Wrapper pour le texte des énigmes
    """
    def __init__(self, filename="../data/enigmes.txt", center=False, wrap=True, foreground="white"):
        """ Init"""
        gtk.VBox.__init__(self)

        label = gtk.Label()
        text = self.parseEnigmeText(filename, foreground=foreground)
        if wrap:
            label.set_line_wrap(True)
        label.set_markup(text)
        if center:
            label.set_justify(gtk.JUSTIFY_CENTER)
        self.pack_start(label, False, False, 5)
        self.show_all()

    def parseEnigmeText(self, filename, foreground="white"):
        """ Parse le texte des énigmes
        """
        ## Lit le fichier
        with open(filename, 'r') as f:
            lines = f.readlines()

        ## Parse
        text = []
        text.append("<span foreground='%s' font_desc='Monospace'>"%(foreground))
        for line in lines:
            if "Eng" in line:
                text_to_append = "<b>"+line.replace("Eng", "Énigme ")+"</b>"
            #~ elif "##FIN##" in line:
                #~ text_to_append = "</center>\n"
            else:
                text_to_append = line
            text.append(text_to_append)

        text = "".join(text)
        text = text + "\n</span>"
        return text

class PopupWindow(gtk.Window):
    """ Fenêtre d'affichage
    """

    def __init__(self, filename="data/enigme.txt", forcebutton=False, foreground="white", background="black"):
        ## Charge la fenêtre
        self.root = None
        gtk.Window.__init__(self)
        self.set_title("Énigmes")
        bgcolor = gtk.gdk.color_parse(background)
        self.modify_bg(gtk.STATE_NORMAL, bgcolor)

        ## Composants
        vbox = gtk.VBox()
        self.enigmebox = EnigmeBox(filename, foreground=foreground)

        ## Pack
        vbox.pack_start(self.enigmebox, True, True, 0)

        ## Boutton
        if forcebutton:
            button = gtk.Button("Start")
            vbox.pack_start(button, True, True, 0)

        ## Connexion
        self.connect("destroy", self.quit)
        if forcebutton:
            button.connect("clicked", self.start)

        self.add(vbox)

    #def quit(self, *parent):
        #self.destroy()

    def start(self, sender=None):
        """ Affiche la fenêtre si utiliser depuis un boutton
        """
        if isinstance(sender, gtk.Button):
            print "Boutton '%s' cliqué"%(sender)
        self.show_all()

    def main(self, root=True):
        """ Lance la boucle principale de gtk
        """
        self.root = root
        gtk.main()

    def quit(self, sender):
        """ Quitte la boucle principale de gtk ou ferme la popup
        """
        if self.root:
            gtk.main_quit()
        else:
            self.hide_all()

if __name__ == "__main__":
    root = PopupWindow(filename="../data/enigme.txt", forcebutton=True)
    root.show_all()
    root.main(root=True)
