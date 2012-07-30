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
pygtk.require("2.0")
import gtk
import time
import gobject
import threading
import os
import hashlib

class ScrollBuffer(threading.Thread):
    """ Classe :threading.Thread

    Permet une gestion plus fine de gtk.TextBuffer
    """

    def __init__(self, root, buffer, lines=[""], n=0, speed=1.0, crypt=True, autostop_at_end=False):
        """ Initialise la classe

        - root            : Classe gtk.ScrolledWindow parente (permet le 'défilement')
        - buffer          : Classe gtk.TextBuffer
        - lines           : List de lines à faire défiler. (defaut: [""])
        - n               : Entier à partir duquel on lit la list 'lines'. (defaut: 0)
        - speed           : Vitesse de défilement (temps entre chaque ligne en seconde : (defaut 0.1))
        - crypt           : Si True, crypte le text (defaut True)
        - autostop_at_end : Si True, stop le défilement à la fin du texte (defaut False)
        """
        ## Permet de remplacer les méthodes de la classe parente (ici threading.Thread qui contient une méthode run)
        super(ScrollBuffer, self).__init__()

        ## Charge les variables
        self.root = root
        self.buffer = buffer
        self.continuer = True # Variable contrôlant le thread (si False, sort de la boucle infinie)
        self.lines = lines
        self.n = n
        self.speed = speed
        self.crypt = crypt
        if self.n <= len(self.lines):
            self.line = self.lines[self.n]
        else:
            self.line = ""
        if self.crypt:
            self.line = self.cryptage(self.line)
        self.autostop_at_end = autostop_at_end

    def update_buffer(self, texte):
        """ Met à jour le buffer

        - texte : Texte à mettre dans le buffer (remplace l'ancien texte)
        """
        ## Met à jour le buffer
        self.buffer.set_text(texte)

        ## Fait défiler le text
        adj = self.root.get_vadjustment()
        adj.set_value( adj.upper - adj.page_size )

        ## Retourne False pour gobject (évite que la fonction soit rappeller automatiquement)
        return False

    def cryptage(self, texte):
        """ Fonction de cryptage

        - texte : Texte à crypter
        """
        ## Déclaration du cryptage
        h = hashlib.md5()
        h.update(texte)

        return h.hexdigest()

    def incremente(self):
        """ Incrémente n de 1 et vérifie le nombre de ligne
        """
        ## Incrémente n (lecteur de ligne dans le fichier)
        self.n = self.n + 1
        if self.n+1 >= len(self.lines):
            if self.autostop_at_end:
                self.quit()
            else:
                self.n = 0
                ## Pour le moment il reste un saut quand le bufer a plus de 100 lignes
                self.line = "\n".join(self.line.split('\n')[-100:])


    def run(self):
        """ Lance le Thread (ré-écriture de la méthode inhérente à threading.Thread)
        """
        ## Boucle 'infinie'
        while self.continuer:
            ## Met à jour le buffer
            gobject.idle_add(self.update_buffer, self.line)

            ## Incrémente self.n
            self.incremente()

            ## Ajout de la ligne suivante
            if self.crypt:
                ajout = ""
                ## Ajoute des lignes cryptées pour remplir la boîte
                while len(ajout) < 32.*5:
                    ajout = ajout + self.cryptage(self.lines[self.n])
                    ## Incrémente self.n
                    self.incremente()
                self.line = self.line + '\n' + ajout
            else:
                self.line = self.line + self.lines[self.n]

            ## Attend avant la ligne suivante
            time.sleep(self.speed/10.)

    def set_speed(self, speed):
        """ Change la vitesse de défilement

        - speed : Délai entre l'affichage de chaque ligne en seconde
        """
        self.speed = speed

    def quit(self):
        """ Quitte proprement le thread
        """
        ## Permet de sortir de la boucle while infinie
        self.continuer = False

        ## Renvoie self.n afin de recommencer au même endroit
        return self.n


class ScrollText(gtk.ScrolledWindow):
    """ Classe permettant de faire défiler du text indéfiniment
    """
    def __init__(self, filename="data/crypt_texte.txt", speed=1.0,\
                crypt=True, lines=None, autostop_at_end=False, foreground='white', background='black'):
        """ Initialisation de la classe

        - filename        : Fichier à faire défiler (defaut le code lui même)
        - speed           : Vitesse de défilement (temps entre chaque ligne en milliseseconde : (defaut 1.0))
        - crypt           : Si True, crypte le text (defaut True)
        - lines           : Liste de string à afficher au lieu de lire un fichier
        - autostop_at_end : Si True, stop le défilement à la fin du texte (defaut False)
        """
        ## Initialisation des variables
        self.filename = filename    # Fichier à faire défiler
        self.launch = False         # Permet de contrôler si le texte défile
        self.buffertext = 0         # Position de lecture lors de l'arrêt du défilement
        self.speed = speed          # Vitesse de défilement
        self.crypt = crypt          # Si True crypte le texte (defaut)
        self.lines = lines          # Lignes à mettre par defaut dans le buffer (defaut le fichier)
        self.autostop_at_end = autostop_at_end # Si True, stop scoll a la fin des ligne (defaut False)

        ## Initialisation de gtk.ScrolledWindow
        gtk.ScrolledWindow.__init__(self)

        ## Suppresssion de barre de défilement
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)

        ## Initialisation de gtk.TextView()
        self.textview = gtk.TextView()
        self.textview.set_editable(False)       # TextView inéditable
        self.textview.set_cursor_visible(False) # Curseur invible
        colour = gtk.gdk.color_parse(background)
        colour2 = gtk.gdk.color_parse(foreground)
        style = self.textview.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = colour
        style.base[gtk.STATE_NORMAL] = colour
        style.text[gtk.STATE_NORMAL] = colour2
        self.textview.set_style(style)

        ## Récupération de gtk.Buffer
        self.buffer = self.textview.get_buffer()

        ## Ajout de TextView à ScrolledWindow
        self.add(self.textview)

        ## Init ScrollBuffer
        self.scroll_buffer = ScrollBuffer(self, self.buffer) # Necessaire pour pouvoir connecter la fonction set_speed

    def loadfile(self, *parent):
        """ Charge un fichier et fait défiler son contenu
        """
        ## Lit le fichier à faire défiler
        f = open(self.filename, 'r')
        lines = f.readlines()
        f.close()

        ## Revnoie le contenu du fichier
        return lines

    def scroll(self, toggle = True):
        """ Fait défiler le text
        """
        if not self.launch:
            if self.lines == None:
                self.lines = self.loadfile()
            ## Reset ScrollBuffer
            self.scroll_buffer = ScrollBuffer(self, self.buffer, lines=self.lines, n=self.buffertext, speed=self.speed,\
                                             crypt=self.crypt, autostop_at_end=self.autostop_at_end)
            ## Charge les lignes à faire défiler
            self.scroll_buffer.lines = self.lines
            ## Lance le défilement
            self.scroll_buffer.start()
            self.launch = True
        elif toggle:
            ## Stop le défilement et du coup le thread et récupère le numéro de ligne actuel
            self.buffertext = self.scroll_buffer.quit()
            self.launch = False

    def set_speed(self, speed):
        """ Change la vitesse de défilement

        - speed : Délai entre l'affichage de chaque ligne en seconde
        """
        self.speed = speed
        self.scroll_buffer.set_speed(self.speed)

    def set_crypt(self):
        """ Cypte le texte s'il est clair ou decrypt s'il est crypté
        """
        if self.crypt:
            self.crypt = False
        else:
            self.crypt = True
        self.scroll_buffer.crypt = self.crypt

    def show_text(self):
        """ Affiche le texte en clair """
        self.buffer.set_text("".join(self.loadfile()))

    def quit(self):
        """ Quitte proprement
        """
        if self.launch:
            self.scroll()

class ScrollTextBox(gtk.VBox):
    """ Conteneur pour la classe ScrollText (gtk.VBox)

    - filename : Fichier à faire défiler (defaut le code lui même)
    - speed    : Vitesse de défilement (temps entre chaque ligne en seconde : (defaut 0.1))
    """

    def __init__(self, filename="data/crypt_texte.txt", speed=1.0, forcebutton=True,\
                crypt=True, lines=None, foreground="white", background="black"):
        """ Initialisation de la classe
        """
        ## Inititalisation de la class gtk.VBox (conteneur)
        gtk.VBox.__init__(self)

        ## Signaux
        gobject.signal_new("main-decrypt-suite", ScrollTextBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_INT])

        ## Affichage optionnel des bouttons
        if forcebutton:
            ## HBox avec le boutton de chargement
            load = gtk.Button(stock=("gtk-media-play"))
            self.pack_start(load, True, True, 0)

            ## HBox (Label+HScale | Boutton)
            hbox = gtk.HBox()

            ## VBox (Label - HScale)
            vbox = gtk.VBox()

            ## Label
            label = gtk.Label("Vitesse en ms")
            vbox.pack_start(label, True, True, 0)

            ## Ajustement
            adj = gtk.Adjustment(speed, 0.01, 10.0, 0.01, 0.1, 1.0)

            ## HScale
            hscale = gtk.HScale(adj)
            hscale.set_digits(2)                # Change la précision (defaut: 1)
            hscale.set_value_pos(gtk.POS_RIGHT) # Change la posisition de la valeur (POS_RIGHT, POS_TOP, POS_BOTTOM, POS_LEFT)
            vbox.pack_start(hscale, True, True, 0)

            ## Pack vbox
            hbox.pack_start(vbox, True, True, 0)

            ## Boutton ouvrir
            boutton = gtk.Button(stock=("gtk-open"))
            hbox.pack_start(boutton, True, True, 0)

            ## Boutton cryptage
            bcrypt = gtk.ToggleButton(label="clair/crypt")
            hbox.pack_start(bcrypt, True, True, 0)

            ## Pack hbox
            self.pack_start(hbox, True, True, 0)

        ## Charge ScrollText
        self.scrolltext = ScrollText(filename=filename, speed=speed, crypt=crypt, lines=lines, foreground=foreground, background=background)
        self.scrolltext.set_size_request(10,300) ## Requête de taille obligatoire pour fixer la scrollbox sinon sans les barres de défilement la scrollbox s'agrandi
        self.pack_start(self.scrolltext, expand=False, fill=False, padding=0)

        ## Connexion
        if forcebutton:
            ## Défilement Start/stop
            load.connect("clicked", self.scroll)
            ## Récupération de la vitesse
            adj.connect("value_changed", lambda w: self.update(hscale))
            ## Ouvrir un nouveau fichier
            boutton.connect("clicked", self.open)
            ## Crypt
            bcrypt.connect("clicked", self.toggle_crypt)

    def scroll(self, *parent):
        """ Lance le défilement ou l'arrête s'il est lancé
        """
        self.scrolltext.scroll()

    def scroll_on(self, sender=None):
        """ Lance le défilement et ne l'arrête pas s'il est lancé """
        self.scrolltext.scroll(toggle = False)

    def scroll_off(self, sender=None):
        """ Arrête le défilement s'il est lancé """
        if self.scrolltext.launch:
            self.scrolltext.scroll()


    def toggle_crypt(self, *parent):
        """ Cypte le texte s'il est clair ou decrypt s'il est crypté
        """
        self.scrolltext.set_crypt()

    def crypt_off(self):
        """ Decrypte le texte """
        if self.scrolltext.crypt:
            self.toggle_crypt()

    def show_clear_text(self, filename=None):
        """ Affiche les énigmes en clair"""
        if filename != None:
            self.set_filename(filename)
        self.scrolltext.show_text()

    def open(self, parent):
        """ Ouvrir un fichier grâce à un explorateur de fichier
        """
        dialog = gtk.FileChooserDialog("Choisit un fichier", gtk.Window(), gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.connect("destroy", lambda w: dialog.destroy())
        statut = dialog.run()
        if statut == gtk.RESPONSE_OK:
            self.set_filename(filename=dialog.get_filename()) # Pas besoin de corriger les ' ' car la fonction open le fait déjà !
        dialog.destroy()

    def update(self, hscale):
        """ Met à jour la valeur de la vitesse gràce à HScale barre

        - hscale : gtk.HScale instance
        """
        self.set_speed(hscale.get_value())

    def set_speed(self, sender=None, speed=None):
        """ Change la vitesse de défilement (pourra être connectée au shell)

        - speed : Délai entre l'affichage de chaque ligne en seconde
        """
        if speed != None:
            self.scrolltext.set_speed(speed)

    def set_filename(self, sender=None, filename=None):
        """ Permet de changer le fichier à faire défiler

        - filename : Nom du fichier à lire
        """
        if filename != None:
            if os.path.isfile(filename):
                ## Arrêt du défilement s'il est lancé
                self.quit()
                self.scrolltext.filename = filename
                self.buffertext = 0
                self.scrolltext.lines = None ## Permet de forcer la lecture du nouveau fichier ça semble ne pas fonctionner...
                self.scroll()
            else:
                raise IOError("Le fichier '%s' n'existe pas"%(filename))

    def reduce2stop(self, stop=True):
        """ Réduit progressivement la vitesse et stop le scroll """
        ## Test si scroll is on
        if self.scrolltext.launch:
            ## Récupère la vitesse
            speed = self.scrolltext.speed
            ## Défini le pas de 'réduction' de la vitesse
            if speed < 1:
                step = 0.1
            elif speed < 5:
                step = 1
            else:
                step = 2
            ## Règle la vitesse
            if speed <= 10:
                self.set_speed(speed=speed+step)
                return True ## Continue à réduire
            else:
                if stop:
                    self.scroll_off()
                    self.scrolltext.show_text()
                    self.emit("main-decrypt-suite", 1)
                return False ## On arrète de réduire
        else:
            return False

    def quit(self, *parent):
        """ Quitte proprement
        """
        ## Arrêt du défilement et du thread associé
        self.scrolltext.quit()


if __name__ == "__main__":
    # Fenêtre principale pour tester ScrollText

    def quit(args):
        scrolltextbox.quit()
        gtk.main_quit()

    ## Charge gobject
    gobject.threads_init()

    ## Créer la fenêtre principale
    root = gtk.Window()
    root.set_title(__file__)
    root.set_default_size(500, 400)
    root.set_position(gtk.WIN_POS_CENTER)
    root.connect("destroy", quit)

    ## ScrollTextBox
    scrolltextbox = ScrollTextBox(filename="../data/crypt_texte.txt")

    ## On attache le tout à root
    root.add(scrolltextbox)

    ## On affiche tout
    root.show_all()
    gtk.main()
