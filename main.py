#!/usr/bin/env python
# *-* coding:utf-8 *-*

import pygtk
pygtk.require("2.0")
import gtk
from modules import *
import time

class MainWindow(gtk.Window):
    """ Fenêtre principale
    """

    def __init__(self):
        """ Constructeur de la fenêtre principale
        """
        gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
        self.set_title("TriViSiJu")
        self.set_default_size(800,600)
        #self.fullscreen()
        self.set_position(gtk.WIN_POS_CENTER)

        ## Création de 4 boîtes
        # \-rootBox
        #   \-leftBox
        #       '-text1 : Vidéo Ariane V sur le pas de tir
        #       '-séparateur
        #       \-text2 : Vidéo Satellite/Sonde ou Modélisation 3D Ariane
        #   \-centerBox
        #       '-coutdown
        #       '-séparateur
        #       '-text4
        #       \-séparateur
        #   \-rightBox
        #       '-text6 : Caractéristiques techniques
        #       '-séparateur
        #       \-text7 : Liste des équipes
        rootBox = gtk.HBox(homogeneous=False,spacing=0)
        leftBox = gtk.VBox(homogeneous=False,spacing=0)
        centerBox = gtk.VBox(homogeneous=False,spacing=0)
        rightBox = gtk.VBox(homogeneous=False,spacing=0)

        ## Compte à rebours
        self.countdown = countdownBox()
        self.countdown.setStartTime(h=0,m=0,s=48,cs=0)
        self.countdown.showControl()
        #self.countdown.start()

        ## Textes provisoires
        #REMtext1 = gtk.Label("<b>Panneau haut gauche</b>\nVidéo Ariane V sur le pas de tir")
        #REMtext1.set_use_markup(True)
        #REMtext2 = gtk.Label("<b>Panneau bas gauche</b>\nVidéo Satellite/Sonde ou Modélisation 3D Ariane")
        #REMtext2.set_use_markup(True)
        text4 = gtk.Label("<b>Texte crypté</b>")
        text4.set_use_markup(True)
        text5 = gtk.Label("<b>Prompt</b>")
        text5.set_use_markup(True)
        text6 = gtk.Label("<b>Panneau haut droite</b>\nCaractéristiques techniques")
        text6.set_use_markup(True)
        text7 = gtk.Label("<b>Panneau bas droite</b>\nListe des équipes")
        text7.set_use_markup(True)
        
        ## Charge la classe Player
        self.screen1 = PlayerFrame(self, 1, quitB=False)
        self.screen2 = PlayerFrame(self, 2, quitB=False)

        ## Affichage des textes provisoires
        #leftBox
        #REMleftBox.pack_start(text1,True,True,0)
        leftBox.pack_start(self.screen1,True,True,0)
        leftBox.pack_start(gtk.HSeparator(),True,True)
        #REMleftBox.pack_start(text2,True,True)
        leftBox.pack_start(self.screen2,True,True,0)
        #centerBox
        centerBox.pack_start(self.countdown,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(text4,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(text5,True,True)
        #rightBox
        rightBox.pack_start(text6,True,True)
        rightBox.pack_start(gtk.HSeparator(),True,True)
        rightBox.pack_start(text7,True,True)

        ## Ajout des sous-boîtes (leftBox, centerBox, rightBox) dans rootBox
        rootBox.pack_start(leftBox,True,True,0)
        rootBox.pack_start(gtk.VSeparator(),True,True,0)
        rootBox.pack_start(centerBox,True,True,0)
        rootBox.pack_start(gtk.VSeparator(),True,True,0)
        rootBox.pack_start(rightBox,True,True,0)

        ## Ajout de rootBox sur la fenêtre principale
        self.add(rootBox)
        
        ## Affichage général
        self.show_all()
        
        ## Envoie de l'id à mplayer après l'avoir affiché
        self.screen1.Screen.setwid(long(self.screen1.Screen.get_id()))
        self.screen2.Screen.setwid(long(self.screen2.Screen.get_id()))
        
        ## Connexion de destroy à la fonction quit
        self.connect("destroy", lambda w: self.quit())

    def quit(self, *parent):
        """ Fonction quitter
        
        Tue proprement l'application root
        """
        ## Envoir le signal à mplayer
        self.screen1.Screen.quit()
        self.screen2.Screen.quit()
        ## Attend que mplayer se soit éteint
        time.sleep(0.1)
        ## Tue l'application root
        gtk.main_quit()

if __name__=="__main__":
    MainWindow()
    gtk.main()
