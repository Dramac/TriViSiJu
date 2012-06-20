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
import subprocess
import gobject
from teams import team

class DecryptBox(gtk.VBox):
    """ Fenêtre de décryptage
    """

    def __init__(self, passwd="passwd", team_list=[team("Orion1", passwd="passwd"), team("Pegase2", passwd="Passwd"), team("Ariane3", passwd="")]):
        """ Initialisation
        """
        ## Initialise la fenetre
        gtk.VBox.__init__(self)
        
        ## Charge les variables
        self.passwd = passwd
        self.team_list = team_list
        self.nteam = len(self.team_list)
        self.percent = 0.0

        ## Initialise la barre de progression
        self.pbar = gtk.ProgressBar()
        self.update_pbar(team_data=("", 0))

        ## Scroll text
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.textview)
        self.scrolledwindow.get_vscrollbar().set_child_visible(False) # Cache la barre verticale
        self.scrolledwindow.get_hscrollbar().set_child_visible(False)

        ## Buffer
        self.buffer = self.textview.get_buffer()

        ## Affichage sur self
        self.pack_start(self.pbar, True, True, 0)
        self.pack_start(self.scrolledwindow, True, True, 0)

    def phase1(self):
        """ La pahse 1 consiste à tester le mot de passe de toute les équipes
        """
        ## Variable de detection des mot de passe
        at_least_one_passwd = False

        ## Nombre de lignes / équipe
        nligne = float(len(self.get_template().split('\n')))
        
        ## Nombre total d'action
        total = nligne*self.nteam
        
        ## Compteur
        count = 0
        num = 0

        ## Boucle sur toutes les équipes
        while self.continuer:
            ## Recupere la classe de l'équipe
            team = self.team_list[num]
            if self.passwd == team.passwd:
                at_least_one_passwd = True
            
            ## Met à jour le texte de la barre
            self.update_pbar(team_data=(team.nom, num+1))

            ## Génère le texte de l'équipe
            text = self.team_text(team).split('\n')
        
            ## Boucle sur les lignes
            for i,line in enumerate(text):
                time.sleep(0.1)
                count = count + 1
                self.percent = float(count)/total
                self.update_pbar()
                self.text = self.text + '\n' + line
                self.update_buffer(self.text)

            ## Incrémente le compteur
            num = num + 1

            ## Arrêt de la boucle while
            if num >= self.nteam:
                self.continuer = False

        ## Renvoie at_least_one_passwd
        return at_least_one_passwd

    def update_buffer(self, text):
        ## Met à jour le buffer
        self.buffer.set_text(text)
        ## Fait défiler le text
        adj = self.scrolledwindow.get_vadjustment()
        adj.set_value( adj.upper - adj.page_size )

    def show_warning_and_continue(self):
        """ Montre que le mot de passe a été trouvé et valide le décryptage
        """
        label = gtk.Label("Le décryptage a réussi, bravo à tous et en particulier à ceux qui ont trouvé la solution.\n\
                          Nous pouvons maintenant avoir accès aux commandes de lancement.")
        self.dialog = gtk.Dialog("Décryptage réussi")
        self.dialog.vbox.pack_start(label)
        label.show()
        self.dialog.run()
        self.dialog.destroy()

    def phase2(self):
        """ Montre des messages d'erreur et lance une procédure de récupération 
        du mot de passe à partir de tous ceux trouvé par chaque équipe
        """
        pass

    def start(self):
        """ Lance la procédure de décryptage
        """
        ## Reset les variables
        self.text = ""
        self.continuer = True
        self.update_pbar(team_data=("", 0))

        ## Lancement de la phase 1
        win = self.phase1()

        ## Test la réussite
        if win:
            self.show_warning_and_continue()
        else:
            self.phase2()

    def update_pbar(self, percent=None, team_data=None):
        """ Met à jour le texte de la barre de progression
        """
        ## Met à jour percent
        if percent != None:
            self.perent = percent
        ## Met à jour le texte et la valeur de la barre
        self.pbar.set_fraction(self.percent)
        if team_data != None:
            self.pbar.set_text("Équipe '%s' (%d/%d)"%(team_data[0], team_data[1], self.nteam))
        ## On fordce la mise à jour de la fenêtre
        while gtk.events_pending():
            gtk.main_iteration(False)

    def get_template(self):
        """ Charge le template du texte
        """
        with open('../data/decrypt_team.txt', 'r') as fichier:
            lines = fichier.readlines()
        lines = ''.join(lines)
        return lines

    def team_text(self, team):
        """ Renvoie le texte mis en forme pour l'équipe donnée
        """
        ## Lit le template
        lines = self.get_template()

        ## Met en forme le texte
        lines = lines.replace("NOM", team.nom)
        lines = lines.replace("TAB", "\t")
        if self.passwd == team.passwd:
            lines = lines.replace('[OK/KO]', '[OK]')
        else:
            lines = lines.replace('[OK/KO]', '[KO]')

        ## Renvoie
        return lines

    def quit(self, *parent):
        """ Fonction qui permet de quitter proprement
        """
        if self.continuer:
            self.continuer = False

class RootWindow(gtk.Window):
    """ Fenêtre principale pour tester le module
    """
    def __init__(self):
        ## Charge gobject (Important pour ScrollTextBox
        gobject.threads_init()

        ## Charge la fenêtre
        gtk.Window.__init__(self)
        self.set_title("Décryptage")
        vbox = gtk.VBox()

        ## Boutton
        button = gtk.Button(label="start")
        
        ## DecryptBox
        self.decryptbox = DecryptBox()

        ## Affichage
        vbox.pack_start(self.decryptbox, True, True, 0)
        vbox.pack_start(button, True, True, 0)
        self.add(vbox)
        self.show_all()

        ## Connexion
        self.connect("destroy", self.quit)
        button.connect("clicked", self.start)

    def start(self, *parent):
        self.decryptbox.start()
    
    def quit(self, *parent):
        """ Fonction qui permet de quitter proprement
        """
        ## Ferme ScrollTextBox
        self.decryptbox.quit()

        ## On quitte l'application
        gtk.main_quit()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    r = RootWindow()
    r.main()
