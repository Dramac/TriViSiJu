#!/usr/bin/env python
#-*-coding: utf8 -*-

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
import pygst
pygst.require("0.10")
import gst
import os


class SongPlayer():
    """ Classe permettant de lire un fichier audio """

    def __init__(self, filename=None):
        """ Chargement du lecteur """
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        self.filename = None
        if filename:
            self.loadfile(filename)

    def loadfile(self, filename):
        """ Charge un fichier """
        if os.path.isfile(filename):
            self.filename = filename
            self.player.set_property("uri", "file://"+filename)
        else:
            self.filename = None

    def play(self, sender=None, file=None):
        """ Lit le fichier """
        if isinstance(file, str):
            self.loadfile(file)
        if self.filename:
            self.player.set_state(gst.STATE_PLAYING)

    def stop(self):
        """ Stop la lecture en cours """
        self.player.set_state(gst.STATE_NULL)

    def on_message(self, bus, message):
        """ Permet de récupérer les messages de Gstreamer """
        t = message.type
        if t == gst.MESSAGE_EOS:
            print "Fin du fichier"
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Erreur: %s" % err, debug

def open():
    """ Explorateur de fichier """
    dialog = gtk.FileChooserDialog("Choisir un fichier", gtk.Window(), gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.connect("destroy", lambda w: dialog.destroy())
    statut = dialog.run()
    if statut == gtk.RESPONSE_OK:
        ## On a un fichier
        filename = dialog.get_filename()
        dialog.destroy()
        return filename.replace(' ', '\ ')
    else:
        ## Annulation
        dialog.destroy()

if __name__ == "__main__":
    """ Attention joue le fichier jusqu'à la fin... """
    ## Charge la classe SongPlayer
    gsplayer = SongPlayer()

    ## Choix d'un fichier
    filename = open()
    
    ## Si on a un fichier on le joue
    if filename:
        if os.path.isfile(filename):
            gsplayer.play(file=filename)
            gtk.main() ## Obligatoire pour que gstreamer puisse fonctionner
