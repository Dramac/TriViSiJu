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
import argparse
import gobject

class promptBox(gtk.VBox):
    """ Boîte contenant un prompt et une zone de texte pour afficher les résultats
    """
    def __init__(self, mainWindow = None, promptCharacter = '>'):
        gtk.VBox.__init__(self)
        
        # Initialisation des attributs
        self.promptCharacter = promptCharacter
        self.mainWindow = mainWindow
        self.full = False

        # Créations des widgets
        self.entry = gtk.Entry()
        self.entry.set_text(self.promptCharacter)
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
        self.iter = self.buffer.get_end_iter()

        # Création de signaux personnalisés
        gobject.signal_new("add-team", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING])

        # Connexion des signaux
        self.entry.connect("activate", self.parseEntry)
        self.entry.connect("insert-text", self.onInsert)
        self.entry.connect("delete-text", self.onDelete)
        if mainWindow != None:
            mainWindow.connect("window-state-event", self.onStateChange)

        # Gestion des commandes
        self.parser = argparse.ArgumentParser("Process command-line")
        self.commands = {'bip': self.onBip, 'fullscreen': self.onFullscreen, 'addteam': self.onAddTeam}
        self.parser.add_argument("command", help = "Command to launch", choices = self.commands.keys())
        self.parser.add_argument("arguments", help = "Arguments", nargs = "*")


    def parseEntry(self, entry):
        """ Méthode appelée lorsque l'on appuie sur la touche Entrée depuis le prompt
        """
        text = entry.get_text()
        if (text == self.promptCharacter):
            return
        self.buffer.insert(self.iter, text + "\n")
        entry.delete_text(1,len(text))
        # met le curseur à la fin
        entry.set_position(-1)

        text = text[1:]
        # parsing de la ligne de commande
        try:
            args = vars(self.parser.parse_args(text.split()))
        except:
            self.buffer.insert(self.iter, "Erreur : commande invalide\n")
            self.result.scroll_to_mark(self.buffer.get_insert(), 0)
            return

        # gestion des commandes
        self.commands[args['command']](args['arguments'])
        
        # on se place à la fin du texte
        self.result.scroll_to_mark(self.buffer.get_insert(), 0)

    def onInsert(self, entry, newText, newTextLength, position):
        """ Méthode appelée lorsque l'on ajoute du texte dans le prompt
        """
        if entry.get_position() == 0:
            entry.stop_emission("insert-text")

    def onDelete(self, entry, start, end):
        """ Méthode appelée lorsque l'on supprime du texte dans le prompt
        """
        if start == 0:
            entry.stop_emission("delete-text")

    def onStateChange(self, window, event):
        """ Méthode appelée quand l'état de la fenêtre change
        """
        if event.new_window_state and gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.full = True
        else:
            self.full = False

    def onBip(self, args):
        """ Méthode de traitement de la commande "bip" """
        if len(args) > 0:
            self.buffer.insert(self.iter, "Erreur : trop d'arguments\n")
            return
        gtk.gdk.beep()

    def onFullscreen(self, args):
        """ Méthode de traitement de la commande "fullscreen" """
        if len(args) > 0:
            self.buffer.insert(self.iter, "Erreur : trop d'arguments\n")
            return
        if self.full:
            self.mainWindow.unfullscreen()
        else:
            self.mainWindow.fullscreen()

    def onAddTeam(self, args):
        """ Méthode de traitement de la commande "addteam" """
        nargs = len(args)
        if nargs == 0:
            self.buffer.insert(self.iter, "Erreur : pas assez d'arguments\n")
            return
        elif nargs > 1:
            self.buffer.insert(self.iter, "Erreur : trop d'arguments\n")
            return
        self.emit("add-team", args[0])

if __name__ == "__main__":
    a = gtk.Window()
    a.set_default_size(400,100)
    a.set_position(gtk.WIN_POS_CENTER)
    a.connect("destroy", gtk.main_quit)
    
    box = promptBox(a)
    a.add(box)
    a.show_all()

    gtk.main()

