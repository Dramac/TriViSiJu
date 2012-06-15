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
import Image

class countdownBox(gtk.VBox):
    def __init__(self,path_to_images="images/", forcebutton=True, width=29, height=50):
        ## Initialise gtk.VBox, gtk.HBox
        gtk.VBox.__init__(self)
        hbox = gtk.HBox()

        # Initialisation des variables
        self.path_to_images = path_to_images
        self.forcebutton = forcebutton
        # Taille des images initiale
        self.WDi = width
        self.HGi = height
        # Taille des images
        self.WD = width
        self.HG = height

        # Création des conteneurs d'images
        self.img_10h = gtk.Image()       
        self.img_h = gtk.Image()
        self.img_col1 = gtk.Image()
        self.img_10m = gtk.Image()
        self.img_m = gtk.Image()
        self.img_col2 = gtk.Image()
        self.img_10s = gtk.Image()
        self.img_s = gtk.Image()
        self.img_col3 = gtk.Image()
        self.img_10cs = gtk.Image()
        self.img_cs = gtk.Image()

        # État de l'horloge (0 et 1 = décroissant, 2 = croissant)
        # Permet également le changement de couleur de l'horloge
        self.way = 0

        # Chemins des différentes images
        self.folder = [self.path_to_images+"orange_",self.path_to_images+"red_",self.path_to_images+"green_"]
        self.digits = ["0.png","1.png","2.png","3.png","4.png","5.png","6.png","7.png","8.png","9.png"]

        # Affichage des chiffres
        self.setStartTime()

        # Insertion des chiffres dans le block hbox
        hbox.pack_start(self.img_10h,False,False)
        hbox.pack_start(self.img_h,False,False)
        hbox.pack_start(self.img_col1,False,False)
        hbox.pack_start(self.img_10m,False,False)
        hbox.pack_start(self.img_m,False,False)
        hbox.pack_start(self.img_col2,False,False)
        hbox.pack_start(self.img_10s,False,False)
        hbox.pack_start(self.img_s,False,False)
        hbox.pack_start(self.img_col3,False,False)
        hbox.pack_start(self.img_10cs,False,False)
        hbox.pack_start(self.img_cs,False,False)

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

    def onSizeChange(self, fullscreen):
        """ Permet de redéfinir la taille des images en fonction de la taille allouée au widget
        """
        # Si fullscreen -> recupère la taille du widget
        # sinon remet la taille par defaut
        if fullscreen:
            allocation = self.get_allocation()
            widget_width = allocation.width
            image_width = float(widget_width)/11.
            self.set_image_size(width=image_width)
        else:
            self.HG = self.HGi 
            self.WD = self.WDi
        self.writeDigits()

    def set_image_size(self, width=None, height=None):
        """ Change la taille des images à la volée
        """
        # Estime la taille sans perdre le ratio
        if width != None and height == None:
            width = int(width)
            ratio = float(self.WD)/float(width)
            self.WD = width
            self.HG = int(self.HG/ratio)
        if width == None and height != None:
            height = int(height)
            ratio = float(self.HG)/float(height)
            self.HG = height
            self.WD = int(self.HG/ratio)
        # Force une taille 
        if width != None and height != None:
            self.HG = int(height)
            self.WD = int(width)


    def setStartTime(self,h=0,m=0,s=20,cs=0):
        self.h_start = h
        self.m_start = m
        self.s_start = s
        self.cs_start = cs
        self.h = h
        self.m = m
        self.s = s
        self.cs = cs
        self.writeDigits()

    def showControl(self):
        """
        Affiche les contrôles sous l'horloge
        TODO: possibilité de déporter dans un autre panneau
        """

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

    def reset(self,widget=None):
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

    def start(self):
        if self.timer is None:
            # Initialisation du timer
            self.timer = gobject.timeout_add(10, self.on_timeout)
            if self.forcebutton:
                self.buttonToggle()

    def pause(self):
        if self.timer:
            gobject.source_remove(self.timer)
            self.timer = None
            if self.forcebutton:
                self.buttonToggle()
            
    def toggle(self,widget=None):
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
        tenh = self.h/10
        h = self.h%10
        tenm = self.m/10
        m = self.m%10
        tens = self.s/10
        s = self.s%10
        tencs = self.cs/10
        cs = self.cs%10
        # Changement d'image
        #self.img_10h.set_from_file(self.folder[self.way]+self.digits[tenh])
        self.img_10h.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[tenh]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_h.set_from_file(self.folder[self.way]+self.digits[h])
        self.img_h.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[h]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_col1.set_from_file(self.folder[self.way]+"column.png")
        self.img_col1.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+"column.png").scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_10m.set_from_file(self.folder[self.way]+self.digits[tenm])
        self.img_10m.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[tenm]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_m.set_from_file(self.folder[self.way]+self.digits[m])
        self.img_m.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[m]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_col2.set_from_file(self.folder[self.way]+"column.png")
        self.img_col2.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+"column.png").scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_10s.set_from_file(self.folder[self.way]+self.digits[tens])
        self.img_10s.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[tens]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_s.set_from_file(self.folder[self.way]+self.digits[s])
        self.img_s.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[s]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_col3.set_from_file(self.folder[self.way]+"column.png")
        self.img_col3.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+"column.png").scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_10cs.set_from_file(self.folder[self.way]+self.digits[tencs])
        self.img_10cs.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[tencs]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))
        #self.img_cs.set_from_file(self.folder[self.way]+self.digits[cs])
        self.img_cs.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(self.folder[self.way]+self.digits[cs]).scale_simple(self.WD,self.HG,gtk.gdk.INTERP_BILINEAR))

if __name__ == "__main__":
    gobject.threads_init()
    a = gtk.Window()
    a.set_default_size(400,100)
    a.set_position(gtk.WIN_POS_CENTER)
    a.connect("destroy", gtk.main_quit)
    
    box = countdownBox("../images/")
    a.add(box)
    a.show_all()

    gtk.main()

