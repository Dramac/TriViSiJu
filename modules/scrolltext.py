#!/bin/env python
#-*-coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import time

class ScrollText():
    """ Classe permettant de faire défiler du text indéfiniment
    """
    def __init__(self, root, filename=__file__):
        """ Initialisation de la classe
        
        root     : Conteneur
        filename : Fichier à faire défiler (defaut le code lui même)
        """
        ## Initialisation des variables
        self.root = root
        self.continuer = 0
        self.line = ""
        self.n = 0
        self.filename = filename
        
        ## Initialisation de gtk.ScrolledWindow pour contenir un gtk.TextView
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.get_vscrollbar().set_child_visible(False) # Cache la barre verticale
        self.scrolledwindow.get_hscrollbar().set_child_visible(False) # Cache la barre horizontale
        
        ## Initialisation de gtk.TextView()
        self.textview = gtk.TextView()
        self.textview.set_editable(False)       # TextView inéditable
        self.textview.set_cursor_visible(False) # Curseur invible
        
        ## Récupération de gtk.Buffer
        self.buffer = self.textview.get_buffer()
        
        ## Ajout de TextView à ScrolledWindow
        self.scrolledwindow.add(self.textview)
        
        ## Ajout de Text à root
        self.root.add(self.scrolledwindow)
    
    def toggle(self, var):
        """ Change var de 0 à 1 et inversement
        """
        if var == 1:
            return 0
        elif var == 0:
            return 1
    
    
    def loadfile(self, *parent):
        """ Charge un fichier et fait défiler son contenu
        """
        ## Lit le fichier à faire défiler
        if self.continuer == 0:
            f = open(self.filename, 'r')
            lines = f.readlines()
            f.close()
        
        ## Change la valeur de continuer
        self.continuer = self.toggle(self.continuer)
        
        ## Boucle infini tant que continuer n'est pas changé
        while self.continuer:
            ## Ajout de la ligne suivante
            self.line = self.line + lines[self.n]
            ## Met à jour le buffer
            self.buffer.set_text(self.line)
            ## Fait défiler le texte
            adj = self.scrolledwindow.get_vadjustment()
            adj.set_value( adj.upper - adj.page_size )
            ## Met à jour l'affichage
            while gtk.events_pending():
                gtk.main_iteration()
            
            ## Incrémente n (lecteur de ligne dans le fichier)
            self.n = self.n + 1
            if self.n >= len(lines):
                self.n = 0
                self.line = "\n".join(self.line.split('\n')[-100:]) ## Pour le moment il reste un saut quand le bufer a plus de 100 linges
            ## Attend avant la ligne suivante
            time.sleep(0.1)
        
        
class RootWindows():
    """ Fenêtre principale pour tester ScrollText
    """
    def __init__(self):
        """ Initialise la fenêtre et chareg ScrollText
        """
        ## Créer la fenêtre principale
        self.root = gtk.Window()
        self.root.set_title(__file__)
        self.root.set_default_size(500, 400)
        self.root.set_position(gtk.WIN_POS_CENTER)
        self.root.connect("destroy", self.quit)
        
        ## HBox avec le boutton de chargement
        hbox = gtk.HBox()
        load = gtk.Button(label="load")
        hbox.add(load)
        
        ## VBox avec ScrollText
        vbox = gtk.VBox()
        # Charge ScrollText
        self.ScrollText = ScrollText(vbox)
        load.connect("clicked", self.ScrollText.loadfile)
        
        ## rootBox qui contient HBox et VBox
        rootBox = gtk.VBox()
        rootBox.pack_start(hbox, True, True, 0)
        rootBox.pack_start(vbox, True, True, 0)
        
        ## On attache le tout à root
        self.root.add(rootBox)
        
        ## On affiche tout
        self.root.show_all()
    
    def quit(self, *parent):
        """ Fonction qui permet de quitter proprement
        """
        ## Si le text defile, on l'arrête
        if self.ScrollText.continuer: 
            self.ScrollText.loadfile()
        ## On quitte l'application
        gtk.main_quit()
        
    def loop(self):
        """ Boucle principale
        """
        gtk.main()

if __name__ == "__main__":
    r = RootWindows()
    r.loop()
