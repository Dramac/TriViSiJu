#!/usr/bin/env python
# *-* coding:utf-8 *-*

import pygtk
pygtk.require("2.0")
import gtk
from modules import *

class MainWindow(gtk.Window):
    """Fenêtre principale"""

    def __init__(self):
        """Constructeur de la fenêtre principale"""
        gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
        self.set_title("TriViSiJu")
        self.set_default_size(800,600)
        #self.fullscreen()
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", gtk.main_quit)

        rootBox = gtk.HBox(homogeneous=False,spacing=0)
        leftBox = gtk.VBox(homogeneous=False,spacing=0)
        centerBox = gtk.VBox(homogeneous=False,spacing=0)
        rightBox = gtk.VBox(homogeneous=False,spacing=0)

        text1 = gtk.Label("<b>Panneau haut gauche</b>\nVidéo Ariane V sur le pas de tir")
        text1.set_use_markup(True)
        text2 = gtk.Label("<b>Panneau bas gauche</b>\nVidéo Satellite/Sonde ou Modélisation 3D Ariane")
        text2.set_use_markup(True)

        countdown = countdownBox()

        text4 = gtk.Label("<b>Texte crypté</b>")
        text4.set_use_markup(True)
        text5 = gtk.Label("<b>Prompt</b>")
        text5.set_use_markup(True)
        text6 = gtk.Label("<b>Panneau haut droite</b>\nCaractéristiques techniques")
        text6.set_use_markup(True)
        text7 = gtk.Label("<b>Panneau bas droite</b>\nListe des équipes")
        text7.set_use_markup(True)

        leftBox.pack_start(text1,True,True,0)
        leftBox.pack_start(gtk.HSeparator(),True,True)
        leftBox.pack_start(text2,True,True)

        centerBox.pack_start(countdown,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(text4,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(text5,True,True)

        rightBox.pack_start(text6,True,True)
        rightBox.pack_start(gtk.HSeparator(),True,True)
        rightBox.pack_start(text7,True,True)

        rootBox.pack_start(leftBox,True,True,0)
        rootBox.pack_start(gtk.VSeparator(),True,True,0)
        rootBox.pack_start(centerBox,True,True,0)
        rootBox.pack_start(gtk.VSeparator(),True,True,0)
        rootBox.pack_start(rightBox,True,True,0)

        self.add(rootBox)
        self.show_all()

if __name__=="__main__":
    MainWindow()
    gtk.main()
