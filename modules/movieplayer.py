#!/usr/bin/env python
#-*-coding: utf8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import os
import time

## Variable utilisée pour stocker le fichier FIFO (pipe, voir Player)
PIPE_PATH = '/tmp/mplayer'

class Player(gtk.Socket):
    """ Interface entre mplayer et le script principal

	gtk.Socket -> Frame cible pour un programme externe
    """

    def __init__(self, id):
        """ Initialise la classe Player

		Il est nécessaire de lui donner un 'id' de façon à faire un tunnel (pipe) entre le GUI et mplayer
        """
        ## Init gtk.Socket instance
        gtk.Socket.__init__(self)

        ## Créé un fichier FIFO pour le tunnel (pipe)
        self.pipe = PIPE_PATH + str(id)
        # Si fichier existe -> suppression
        ##TODO: Trouver un meilleur moyen de tester si le fichier FIFO existe 
        try:
            os.unlink(self.pipe)
        except:
            pass
        # Créé le fichier FIFO
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
        self.cmdplayer("pause")

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

class PlayerFrame(gtk.Table):
    """ Génère une Frame contenant le lecteur, les bouttons de contrôle et tout ce qui va avec.
    """

    def __init__(self, root, id, quitB=True):
        """ Initialise la classe

        root  : Fenêtre principale (Besoin de quitter l'application proprement avec la fonction Root.quit())
        id    : Entier utiliser pour faire le tunnel entre mplayer et la classe Player
        quitB : Booléen. Si True (Défaut), affiche le boutton quitter
        """
        ## Root
        self.root = root
        ## Création d'une table
        if quitB:
            gtk.Table.__init__(self, rows=2, columns=4)
        else:
            gtk.Table.__init__(self, rows=2, columns=3)
        self.set_col_spacings(10)
        self.set_row_spacings(10)

        # Charge la classe Player
        self.Screen = Player(id)
        self.Screen.set_size_request(100, 100)
        self.attach(self.Screen, 0, 5, 0, 1, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, xpadding=5, ypadding=5)

        # Boutton Ouvrir
        BttOpen = gtk.Button(stock=("gtk-open"))
        BttOpen.connect("clicked", self.open)
        self.attach(BttOpen, 0, 1, 1, 2)

        # Boutton avancer
        BttFw = gtk.Button(label="Avancer")
        BttFw.connect("clicked", self.Screen.forward)
        self.attach(BttFw, 2, 3, 1, 2)

        # Boutton reculer
        BttBw = gtk.Button(label="Reculer")
        BttBw.connect("clicked", self.Screen.backward)
        self.attach(BttBw, 1, 2, 1, 2)

        # Boutton quitter
        if quitB:
            Bttquit = gtk.Button(stock=('gtk-quit'))
            Bttquit.connect("clicked", lambda w: self.quit(self.root))
            self.attach(Bttquit, 3, 4, 1, 2)

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
