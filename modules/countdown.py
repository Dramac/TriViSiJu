#!/usr/bin/env python
# *-* coding:utf-8 *-*

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import time
import cStringIO
import gobject
import ImageFile
import Image

class countdownBox(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        hbox = gtk.HBox()

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
        self.way = 0

        self.folder = ["images/orange_","images/red_","images/green_"]
        self.digits = ["0.png","1.png","2.png","3.png","4.png","5.png","6.png","7.png","8.png","9.png"]
        self.img_10h.set_from_file(self.folder[0]+self.digits[0])
        self.img_h.set_from_file(self.folder[0]+self.digits[0])
        self.img_col1.set_from_file(self.folder[0]+"column.png")
        self.img_10m.set_from_file(self.folder[0]+self.digits[0])
        self.img_m.set_from_file(self.folder[0]+self.digits[0])
        self.img_col2.set_from_file(self.folder[0]+"column.png")
        self.img_10s.set_from_file(self.folder[0]+self.digits[0])
        self.img_s.set_from_file(self.folder[0]+self.digits[0])
        self.img_col3.set_from_file(self.folder[0]+"column.png")
        self.img_10cs.set_from_file(self.folder[0]+self.digits[0])
        self.img_cs.set_from_file(self.folder[0]+self.digits[0])

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

        self.button = gtk.Button("Stop")
        self.button.connect("clicked",self.toggle)

        self.pack_start(hbox)
        self.pack_start(self.button,False,False)

    def start(self,h=0,m=0,s=20,cs=0):
        self.h = h
        self.m = m
        self.s = s
        self.cs = cs
        self.timer = gobject.timeout_add(10, self.on_timeout)

    def toggle(self,widget):
        if self.timer is None:
            self.timer = gobject.timeout_add(10, self.on_timeout)
            self.button.set_label("Stop")
        else:
            gobject.source_remove(self.timer)
            self.timer = None
            self.button.set_label("Resume")

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
        if self.h == 0 and self.m == 0 and self.s == 10 and self.cs == 0 and self.way == 0:
            self.way = 1

        tenh_ = self.h/10
        h_ = self.h%10
        tenm_ = self.m/10
        m_ = self.m%10
        tens_ = self.s/10
        s_ = self.s%10
        tencs_ = self.cs/10
        cs_ = self.cs%10
        self.img_10h.set_from_file(self.folder[self.way]+self.digits[tenh_])
        self.img_h.set_from_file(self.folder[self.way]+self.digits[h_])
        self.img_col1.set_from_file(self.folder[self.way]+"column.png")
        self.img_10m.set_from_file(self.folder[self.way]+self.digits[tenm_])
        self.img_m.set_from_file(self.folder[self.way]+self.digits[m_])
        self.img_col2.set_from_file(self.folder[self.way]+"column.png")
        self.img_10s.set_from_file(self.folder[self.way]+self.digits[tens_])
        self.img_s.set_from_file(self.folder[self.way]+self.digits[s_])
        self.img_col3.set_from_file(self.folder[self.way]+"column.png")
        self.img_10cs.set_from_file(self.folder[self.way]+self.digits[tencs_])
        self.img_cs.set_from_file(self.folder[self.way]+self.digits[cs_])
        
        return True # Nécessaire pour le timeout_add

if __name__ == "__main__":
    gobject.threads_init()
    a = gtk.Window()
    a.set_default_size(400,100)
    a.set_position(gtk.WIN_POS_CENTER)
    a.connect("destroy", gtk.main_quit)
    
    box = countdownBox()
    a.add(box)
    a.show_all()

    gtk.main()

