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

class countdownBox(gtk.VBox):
    def __init__(self,forcebutton=True, size=40):
        ## Initialise gtk.VBox, gtk.HBox
        gtk.VBox.__init__(self)
        hbox = gtk.HBox()

        # Initialisation des variables
        self.size = size
        self.forcebutton = forcebutton
        # Taille des images initiale

        gobject.signal_new("prompt-message",countdownBox,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING])

        # Création des conteneurs d'images
        self.text = gtk.Label("00:00:40:00")

        # État de l'horloge (0 et 1 = décroissant, 2 = croissant)
        # Permet également le changement de couleur de l'horloge
        self.way = 0

        # Affichage des chiffres
        self.setStartTime()

        # Insertion des chiffres dans le block hbox
        hbox.pack_start(self.text,False,False)

        # Alignement (permet de centrer le coutdown)
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        align.add(hbox)

        # Insertion des chiffres dans le block mère
        self.pack_start(align)
        self.timer = None
        self.playPause = None

        # Show control
        if self.forcebutton:
            self.showControl()

    def setStartTime(self, sender=None, h=0, m=0, s=20, cs=0):
        """Spécification de l'heure du timer"""
        # Vérification des conditions
        if h < 100 and h >= 0:
            self.h_start = h
            self.h = h
        else:
            self.emit("message","0 >= h > 100")
        if m < 60 and m >= 0:
            self.m_start = m
            self.m = m
        else:
            self.emit("message","0 >= m > 60")
        if s < 60 and s >= 0:
            self.s_start = s
            self.s = s
        else:
            self.emit("message","0 >= s > 60")
        if cs < 100 and cs >= 0:
            self.cs_start = cs
            self.cs = cs
        else:
            self.emit("message","0 >= cs > 100")
        self.writeDigits()

    def showControl(self):
        """Affiche les contrôles sous l'horloge"""

        # Création du bouton Play/Pause...
        self.button = gtk.Button(stock=("gtk-media-play"))
        self.button.connect("clicked",self.toggle)

        # ... et du bouton Reset
        back_button = gtk.Button(stock=("gtk-goto-first"))
        back_button.connect("clicked",self.reset)

        # Insertion
        hbox2 = gtk.HBox()
        hbox2.pack_start(self.button,False,False)
        hbox2.pack_start(back_button,False,False)

        self.add(hbox2)

    def reset(self, sender=None):
        """
        Remise à zéro du compteur
        """
        self.h = self.h_start
        self.m = self.m_start
        self.s = self.s_start
        self.cs = self.cs_start

        self.way = 0
        self.writeDigits()

    def buttonToggle(self):
        """ Toggle le gtk.Stock du boutton play/pause
        """
        if self.button.get_label() == "gtk-media-play":
            self.button.set_label("gtk-media-pause")
        elif self.button.get_label() == "gtk-media-pause":
            self.button.set_label("gtk-media-play")

    def start(self, sender=None):
        if self.timer is None:
            # Initialisation du timer
            self.timer = gobject.timeout_add(10, self.on_timeout)
            if self.forcebutton:
                self.buttonToggle()

    def pause(self, sender=None):
        if self.timer:
            gobject.source_remove(self.timer)
            self.timer = None
            if self.forcebutton:
                self.buttonToggle()

    def toggle(self, sender=None):
        """
        Play/Pause
        """
        if self.timer is None:
            self.start()
        else:
            self.pause()

    def on_timeout(self, *args):
        # Décrémentation
        if self.way == 0 or self.way == 1:
            self.cs -= 1
            if self.cs == -1:
                self.cs = 99
                self.s -= 1
                if self.s == -1:
                    self.s = 59
                    self.m -= 1
                    if self.m == -1:
                        self.m = 59
                        self.h -= 1
                        if self.h == -1:
                            self.way = 2
        # Incrémentation
        else:
            self.cs = self.cs+1
            if self.cs == 100:
                self.s += 1
                self.cs = 0
                if self.s == 60:
                    self.m += 1
                    self.s = 0
                    if self.m == 60:
                        self.h += 1
                        self.m = 0
                        if self.h == 24:
                            self.h = 0
        # Changement de couleur pour H-10 sec.
        if self.h == 0 and self.m == 0 and self.s == 10 and self.cs == 0 and self.way == 0:
            self.way = 1

        self.writeDigits()

        return True # Nécessaire pour le timeout_add

    def writeDigits(self):
        """
        Méthode de modification de l'affichage des digits
        """
        # Isolation des différents chiffres
        string = "<span font_desc='Digit "+str(self.size)+"'"
        if self.way == 0:
            string += " foreground='orange'>"
        elif self.way == 1:
            string += " foreground='red'>"
        else:
            string += " foreground='green'>"
        string += "%02d:%02d:%02d:%02d</span>   " % (self.h,self.m,self.s,self.cs)

        self.text.set_markup(string)

    def resize(self,sender,newsize):
        """Méthode de changement de taille à la volée"""
        try:
            self.size = int(newsize)
            self.writeDigits()
        except:
            msg = "Cette taille doit être un entier"
            print msg
            self.emit("message",msg)

class Root(gtk.Window):
    """ Fenêtre principale du compte à rebours
    """
    def __init__(self):
        """ Charge la fenêtre
        """
        ## gtk.Window
        gtk.Window.__init__(self)

        #self..set_decorated(False) ## Permet d'enlever la bordure -> impossible à détruire !
        self.set_default_size(400,100)
        self.connect("destroy", gtk.main_quit)

        ## Ajout du timer
        box = countdownBox("../images/")
        self.add(box)
        self.show_all()

        ## Permet de placer la fenêtre en haut à droite
        width, height = self.get_size()
        self.move(gtk.gdk.screen_width() - width, 0)

if __name__ == "__main__":
    ## gobject
    gobject.threads_init()

    ## Creation de la fenêtre
    root = Root()

    ## Main loop
    gtk.main()

