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
pygtk.require('2.0')
import gtk
import os
import time
import subprocess
import tempfile

## Variable utilisée pour stocker le fichier FIFO (pipe, voir Player)
PIPE_PATH = '/tmp'

class Player(gtk.Socket):
    """ Interface entre mplayer et le script principal

	gtk.Socket -> Frame cible pour un programme externe
    """

    def __init__(self, id):
        """ Initialise la classe Player

		Il est nécessaire de lui donner un 'id' de façon à faire un tunnel (pipe) entre le GUI et mplayer
        """
        ## Teste de la présence de mplayer sur la machine
        try:
            subprocess.check_call(['which','mplayer'])
        except:
            print 'mplayer n\'est pas installé sur cette machine.'
            exit(1)

        ## Init gtk.Socket instance
        gtk.Socket.__init__(self)

        ## Créé un fichier FIFO pour le tunnel (pipe)
        self.pipe = tempfile.mktemp(suffix='video'+str(id), prefix='pipe', dir=PIPE_PATH)
        # Créer le fichier FIFO
        os.mkfifo(self.pipe)
        os.chmod(self.pipe, 0666)

        ## Sert à contrôler si mplayer est lancé
        self.start = False

    def cmdplayer(self, cmd):
        """ Commande mplayer
        
        Écris 'cmd' dans le fichier FIFO
        mplayer reçoit (via le tunnel) la commande et l'exécute
        """
        open(self.pipe, 'w').write(cmd+'\n')

    def setwid(self, wid):
        """ Lance mplayer en mode esclave (slave), utilisation d'un tunnel pour l'envoie de commande

        Pour les autres options de mplayer, voir le manuel de mplayer => man mplayer
        """
        ## Lance mplayer en mode esclave
        os.system("mplayer -nojoystick -nolirc -slave -vo x11 -wid %s -vf scale=400:200 -idle -input file=%s &"%(wid, self.pipe))
        ## Déclare mplayer comme étant lancé
        self.start = True

    def loadfile(self, filename):
        """ Charge un fichier
        """
        ## TODO: Créé un type d'erreur pour mieux la déclarer
        if not self.start:
            print "Vous devez paramétrer une 'wid' pour mplayer... Voir Player.setwid(wid)"
            raise
        else:
            self.cmdplayer("loadfile %s"%(filename))
            self.cmdplayer("change_resctangle w=100:h=100")

    ## TODO: Ajouter un boutton pause
    def pause(self, parent):
        """ Envoie la commande pause à mplayer
        """
        ## Envoie pause à mplayer (si en pause reprend la lecture)
        self.cmdplayer("pause")
        ## Change le 'stock' du boutton play/pause
        if parent.get_label() == "gtk-media-pause":
            parent.set_label("gtk-media-play")
        elif parent.get_label() == "gtk-media-play":
            parent.set_label("gtk-media-pause")

    def forward(self, parent):
        """ Envoie la commande avancer de +10 0 (seek +10 0) à mplayer
        """
        self.cmdplayer("seek +10 0")

    def backward(self, parent):
        """ Envoie la commande reculer de -10 0 (seek -10 0) à mplayer
        """
        self.cmdplayer("seek -10 0")

    def quit(self):
        """ Encoie la commande quitter (suit) à mplayer
        """
        ## Envoie la commande quitter
        self.cmdplayer("quit")
        ## Déclare mplayer comme non actif
        self.start = False
        ## Supprime le fichier FIFO
        os.remove(self.pipe)

class PlayerFrame(gtk.Table):
    """ Génère une Frame contenant le lecteur, les bouttons de contrôle et tout ce qui va avec.
    """

    def __init__(self, root, id, quitb=True, forcebutton=False):
        """ Initialise la classe

        root        : Fenêtre principale (Besoin de quitter l'application proprement avec la fonction Root.quit())
        id          : Entier utiliser pour faire le tunnel entre mplayer et la classe Player
        quitb       : Booléen. Si True (Défaut), affiche le boutton quitter /!\ forcebutton doit être True
        forcebutton : Booléen. Si True, force l'affichage des boutton (lectue, avance et recule) (défaut False)
        """
        ## Root
        self.root = root
        ## Création d'une table
        if quitb and forcebutton:
            gtk.Table.__init__(self, rows=2, columns=5)
        elif forcebutton and not quitb:
            gtk.Table.__init__(self, rows=2, columns=4)
        elif not forcebutton and not quitb:
            gtk.Table.__init__(self, rows=1, columns=1)
        self.set_col_spacings(10)
        self.set_row_spacings(10)

        # Charge la classe Player
        self.Screen = Player(id)
        self.Screen.set_size_request(100, 100)
        self.attach(self.Screen, 0, 5, 0, 1, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, xpadding=5, ypadding=5)

        if forcebutton:
            # Boutton Ouvrir
            BttOpen = gtk.Button(stock=("gtk-open"))
            BttOpen.connect("clicked", self.open)
            self.attach(BttOpen, 0, 1, 1, 2)
            
            # Boutton Pause
            BttPause = gtk.Button(stock=("gtk-media-pause"))
            BttPause.connect("clicked", self.Screen.pause)
            self.attach(BttPause, 1, 2, 1, 2)

            # Boutton avancer
            BttFw = gtk.Button(stock=("gtk-media-forward"))
            BttFw.connect("clicked", self.Screen.forward)
            self.attach(BttFw, 3, 4, 1, 2)

            # Boutton reculer
            BttBw = gtk.Button(stock=("gtk-media-rewind"))
            BttBw.connect("clicked", self.Screen.backward)
            self.attach(BttBw, 2, 3, 1, 2)

            # Boutton quitter
            if quitb:
                Bttquit = gtk.Button(stock=('gtk-quit'))
                Bttquit.connect("clicked", lambda w: self.quit(self.root))
                self.attach(Bttquit, 4, 5, 1, 2)
            

    def quit(self, root):
        """ Fonction quitter (utilisation de root.quit())
        """
        root.quit()

    def open(self, parent):
        """ Ouvrir un fichier grâce à un explorateur de fichier
        """
        dialog = gtk.FileChooserDialog("Select File", gtk.Window(), gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.connect("destroy", lambda w: dialog.destroy())
        statut = dialog.run()
        if statut == gtk.RESPONSE_OK:
            self.Screen.loadfile(dialog.get_filename().replace(' ', '\ '))
        dialog.destroy()

class Root:
    """ Fenêtre principale contenant toute les Frame et sous-Frame
    """

    def __init__(self):
        ## Création de la fenêtre principale
        root = gtk.Window()
        root.set_title("Movie player")
        root.set_default_size(500, 400)
        root.set_position(gtk.WIN_POS_CENTER)
        root.connect("destroy", self.quit)

        ## Charegement de la classe Player et ajout du lecteur dans root
        self.screen = PlayerFrame(self, 1)
        root.add(self.screen)

        ## Affichage
        root.show_all()

        ## Envoie de l'id à mplayer après l'avoir afficher
        self.screen.Screen.setwid(long(self.screen.Screen.get_id()))

    def quit(self, *parent):
        """ Fonction quitter
        
        Tue proprement l'application root
        """
        ## Envoir le signal à mplayer
        self.screen.Screen.quit()
        ## Attend que mplayer se soit éteint
        time.sleep(1)
        ## Tue l'application root
        gtk.main_quit()

    def loop(self):
        """ Boocle d'évènement
        """
        gtk.main()
        
if __name__ == "__main__":
    r = Root()
    r.loop()
