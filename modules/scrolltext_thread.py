#!/usr/bin/env python
#-*-coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import time
import gobject
import subprocess
import threading

class ScrollBuffer(threading.Thread):
    """ Classe :threading.Thread
    Permet de mettre à jour le buffer
    """
    def __init__(self, root, buffer, continuer=True, lines=[""], n=0):
        """ Initialise la classe
        """
        super(ScrollBuffer, self).__init__()
        ## Charge les variables
        self.root = root
        self.buffer = buffer
        self.continuer = continuer
        self.lines = lines
        self.n = n
        self.line = self.lines[self.n]

    def update_buffer(self, text):
        """ Met à jour le buffer
        """
        return False

    def run(self):
        """ Lance le Thread
        """
        print "run"
        while self.continuer:
            # Met à jour le buffer
            self.buffer.set_text(self.line)
            ## Met à jour le buffer
            gobject.idle_add(self.update_buffer, self.line)
            
            # Fait défiler le texte
            adj = self.root.get_vadjustment()
            adj.set_value( adj.upper - adj.page_size )
            
             #Incrémente n (lecteur de ligne dans le fichier)
            self.n = self.n + 1
            if self.n >= len(self.lines):
                self.n = 0
                self.line = "\n".join(self.line.split('\n')[-100:]) ## Pour le moment il reste un saut quand le bufer a plus de 100 linges
            
            # Ajout de la ligne suivante
            self.line = self.line + self.lines[self.n]
            
            # Attend avant la ligne suivante
            time.sleep(0.1)

    def quit(self):
        self.continuer = False
        return self.n


class ScrollText(gtk.ScrolledWindow):
    """ Classe permettant de faire défiler du text indéfiniment
    """
    def __init__(self, filename=__file__):
        """ Initialisation de la classe
        
        root     : Conteneur
        filename : Fichier à faire défiler (defaut le code lui même)
        """
        ## Initialisation des variables
        self.continuer = True
        self.filename = filename
        print filename
        self.launch = False
        self.buffertext = 0

        ## Initialisation de gtk.ScrolledWindow
        gtk.ScrolledWindow.__init__(self)
        
        ## Initialisation de gtk.ScrolledWindow pour contenir un gtk.TextView
        self.get_vscrollbar().set_child_visible(False) # Cache la barre verticale
        self.get_hscrollbar().set_child_visible(False) # Cache la barre horizontale
        
        ## Initialisation de gtk.TextView()
        self.textview = gtk.TextView()
        self.textview.set_editable(False)       # TextView inéditable
        self.textview.set_cursor_visible(False) # Curseur invible
        
        ## Récupération de gtk.Buffer
        self.buffer = self.textview.get_buffer()
        
        ## Ajout de TextView à ScrolledWindow
        self.add(self.textview)

        
    def loadfile(self, *parent):
        """ Charge un fichier et fait défiler son contenu
        """
        ## Lit le fichier à faire défiler
        f = open(self.filename, 'r')
        lines = f.readlines()
        f.close()

        return lines

    def scroll(self, *parent):
        if not self.launch:
            lines = self.loadfile()
            ## init ScrollBuffer
            self.scroll_buffer = ScrollBuffer(self, self.buffer, continuer=self.continuer, lines=lines, n=self.buffertext)
            self.scroll_buffer.start()
            self.launch = True
        else:
            self.buffertext = self.scroll_buffer.quit()
            self.launch = False
            print self.buffertext
        

class RootWindows():
    """ Fenêtre principale pour tester ScrollText
    """
    def __init__(self):
        """ Initialise la fenêtre et chareg ScrollText
        """
        gobject.threads_init()
        ## Créer la fenêtre principale
        self.root = gtk.Window()
        self.root.set_title(__file__)
        self.root.set_default_size(500, 400)
        self.root.set_position(gtk.WIN_POS_CENTER)
        self.root.connect("destroy", self.quit)
        
        ## VBox avec ScrollText
        vbox = gtk.VBox()

        ## HBox avec le boutton de chargement
        load = gtk.Button(stock=("gtk-media-play"))
        vbox.pack_start(load, True, True, 0)
        
        # Charge ScrollText
        self.scrolltext = ScrollText()
        load.connect("clicked", self.scrolltext.scroll)
        vbox.pack_start(self.scrolltext, True, True, 0)
        
        ## On attache le tout à root
        self.root.add(vbox)
        
        ## On affiche tout
        self.root.show_all()
    
    def quit(self, *parent):
        """ Fonction qui permet de quitter proprement
        """
        ## Si le text defile, on l'arrête
        if self.scrolltext.launch: 
            self.scrolltext.scroll_buffer.quit()
        ## On quitte l'application
        gtk.main_quit()
        
    def loop(self):
        """ Boucle principale
        """
        gtk.main()

if __name__ == "__main__":
    r = RootWindows()
    r.loop()
