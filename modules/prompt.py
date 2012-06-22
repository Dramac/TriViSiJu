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
import decrypt

class promptBox(gtk.VBox):
    """ Boîte contenant un prompt et une zone de texte pour afficher les résultats
    """
    def __init__(self, promptCharacter = '>'):
        gtk.VBox.__init__(self)
        
        # Initialisation des attributs
        self.promptCharacter = promptCharacter
        self.full = False

        # Créations des widgets
        self.entry = gtk.Entry()
        self.entry.set_text(self.promptCharacter)
        self.result = gtk.TextView()
        self.result.set_editable(False)
        self.result.set_cursor_visible(False)

        colour = gtk.gdk.color_parse("black")
        colour2 = gtk.gdk.color_parse("green")
        style = self.entry.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = colour
        style.base[gtk.STATE_NORMAL] = colour
        style.text[gtk.STATE_NORMAL] = colour2
        self.entry.set_style(style)
        self.result.set_style(style)

        resultWindow = gtk.ScrolledWindow()
        resultWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        resultWindow.add(self.result)

        # Insertion des widgets dans la boîte
        self.pack_start(self.entry,expand=False,fill=True)
        self.pack_start(resultWindow,expand=True,fill=True)

        # Buffer du textView
        self.buffer = self.result.get_buffer()

        # Création de signaux personnalisés
        gobject.signal_new("add-team", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING])
        gobject.signal_new("delete-team", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING])
        gobject.signal_new("passwd-team", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING, gobject.TYPE_STRING])
        gobject.signal_new("fullscreen", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("quit", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("start-timer", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("stop-timer", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("reset-timer", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("set-timer", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_INT, gobject.TYPE_INT, gobject.TYPE_INT, gobject.TYPE_INT])
        gobject.signal_new("load-video", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING])
        gobject.signal_new("pause-video", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("forward-video", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("backward-video", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("decrypt", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("load-teams", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("save-teams", promptBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])

        # Connexion des signaux
        self.entry.connect("activate", self.parseEntry)
        self.entry.connect("insert-text", self.onInsert)
        self.entry.connect("delete-text", self.onDelete)

        # Gestion des commandes
        self.parser = argparse.ArgumentParser("Process command-line")
        self.commands = {'bip': self.onBip, 'fullscreen': self.onFullscreen, 'team': self.onTeam, 'quit': self.onQuit, 'timer': self.onTimer, 'video': self.onVideo, 'decrypt': self.onDecrypt}
        self.parser.add_argument("command", help = "Command to launch", choices = self.commands.keys())
        self.parser.add_argument("arguments", help = "Arguments", nargs = "*")


    def parseEntry(self, entry):
        """ Méthode appelée lorsque l'on appuie sur la touche Entrée depuis le prompt
        """
        text = entry.get_text()
        if (text == self.promptCharacter):
            return
        self.iter = self.buffer.get_start_iter()
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
            self.result.scroll_to_iter(self.iter, 0)
            return

        # gestion des commandes
        self.commands[args['command']](args['arguments'])
        
        # on se place à la fin du texte
        self.result.scroll_to_iter(self.iter, 0)

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
        self.emit("fullscreen")

    def onTeam(self, args):
        """ Méthode de traitement de la commande "addteam" """
        nargs = len(args)
        if nargs < 1:
            self.buffer.insert(self.iter, "Erreur : pas assez d'arguments\n")
            return
        subcommand = args[0]
        if subcommand == 'add':
            if nargs == 2:
                self.emit("add-team", args[1])
            elif nargs < 2:
                # code qui indique qu'il n'y a pas assez d'arguments
                nargs = 0
            else:
                # code qui indique qu'il y a trop d'arguments
                nargs = -1
        elif subcommand == 'delete':
            if nargs == 2:
                self.emit("delete-team", args[1])
            elif nargs < 2:
                nargs = 0
            else:
                nargs = -1
        elif subcommand == 'passwd':
            if nargs == 3:
                self.emit("passwd-team", args[1], args[2])
            elif nargs < 3:
                nargs = 0
            else:
                nargs = -1
        elif subcommand == 'load':
            if nargs == 1:
                self.emit("load-teams")
            else:
                nargs = -1
        elif subcommand == 'save':
            if nargs == 1:
                self.emit("save-teams")
            else:
                nargs = -1
        else:
            self.buffer.insert(self.iter, "Erreur : sous-commande invalide\n")
            return
        # Erreurs
        if nargs == 0:
            self.buffer.insert(self.iter, "Erreur : pas assez d'arguments\n")
        elif nargs == -1:
            self.buffer.insert(self.iter, "Erreur : trop d'arguments\n")

    def onTimer(self, args):
        """ Méthode de traitement de la commande "timer" """
        nargs = len(args)
        if nargs < 1:
            self.buffer.insert(self.iter, "Erreur : pas assez d'arguments\n")
            return
        subcommand = args[0]
        if subcommand == 'start':
            if nargs == 1:
                self.emit("start-timer")
            else:
                # code qui indique qu'il y a trop d'arguments
                nargs = -1
        elif subcommand == 'stop':
            if nargs == 1:
                self.emit("stop-timer")
            else:
                nargs = -1
        elif subcommand == 'reset':
            if nargs == 1:
                self.emit("reset-timer")
            else:
                nargs = -1
        elif subcommand == 'set':
            h = 0
            m = 0
            s = 0
            cs = 0
            if nargs == 1:
                # code qui indique qu'il n'y a pas assez d'arguments
                nargs = 0
            try:
                if nargs > 1:
                    h = int(args[1])
                if nargs > 2:
                    m = int(args[2])
                if nargs > 3:
                    s = int(args[3])
                if nargs > 4:
                    cs = int(args[4])
            except:
                self.buffer.insert(self.iter, "Erreur : arguments invalides\n")
                return
            if nargs > 5:
                nargs = -1
            if nargs > 0:
                self.emit("set-timer", h, m, s, cs)
        else:
            self.buffer.insert(self.iter, "Erreur : sous-commande invalide\n")
            return
        # Erreurs
        if nargs == 0:
            self.buffer.insert(self.iter, "Erreur : pas assez d'arguments\n")
        elif nargs == -1:
            self.buffer.insert(self.iter, "Erreur : trop d'arguments\n")

    def onVideo(self, args):
        """ Méthode de traitement de la commande "addteam" """
        nargs = len(args)
        if nargs < 1:
            self.buffer.insert(self.iter, "Erreur : pas assez d'arguments\n")
            return
        subcommand = args[0]
        if subcommand == 'load':
            if nargs == 2:
                self.emit("load-video", args[1])
            elif nargs < 2:
                # code qui indique qu'il n'y a pas assez d'arguments
                nargs = 0
            else:
                # code qui indique qu'il y a trop d'arguments
                nargs = -1
        elif subcommand == 'pause':
            if nargs == 1:
                self.emit("pause-video")
            else:
                nargs = -1
        elif subcommand == 'forward':
            if nargs == 1:
                self.emit("forward-video")
            else:
                nargs = -1
        elif subcommand == 'backward':
            if nargs == 1:
                self.emit("backward-video")
            else:
                nargs = -1
        else:
            self.buffer.insert(self.iter, "Erreur : sous-commande invalide\n")
            return
        # Erreurs
        if nargs == 0:
            self.buffer.insert(self.iter, "Erreur : pas assez d'arguments\n")
        elif nargs == -1:
            self.buffer.insert(self.iter, "Erreur : trop d'arguments\n")

    def onDecrypt(self, args):
        """Initialisation de la décryption"""
        #popup = decrypt.popupWindow()
        #popup.start()
        self.emit("decrypt")

    def onExternalInsert(self,sender,message):
        """ Méthode pour ajouter du texte """
        self.buffer.insert(self.iter,message + "\n")

    def onQuit(self, args):
        """ Méthode de traitement de la commande quit """
        if len(args) > 0:
            self.buffer.insert(self.iter, "Erreur : trop d'arguments\n")
            return
        self.emit("quit")

if __name__ == "__main__":
    a = gtk.Window()
    a.set_default_size(400,100)
    a.set_position(gtk.WIN_POS_CENTER)
    a.connect("destroy", gtk.main_quit)
    
    box = promptBox()
    a.add(box)
    a.show_all()

    gtk.main()

