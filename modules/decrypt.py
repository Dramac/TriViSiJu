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
from scrolltext import ScrollText
import gobject
from teams import team

class DecryptBox(gtk.VBox):
    """ Fenêtre de décryptage
    """

    def __init__(self, passwd="passwd", team_list=[team("Equipe1", passwd="passwd"), team("Equipe2", passwd="Passwd")]):
        """ Initialisation
        """
        ## Initialise la fenetre
        gtk.VBox.__init__(self)
        
        ## Charge les variables
        self.passwd = passwd

        ## Initialise la barre de progression
        self.pbar = gtk.ProgressBar()

        ## Génère le text
        self.text = self.text_gen(team_list)

        ## Scroll text
        self.scrolltext= ScrollText(lines=self.text, speed=6., crypt=False, autostop_at_end=True)

        ## Affichage sur self
        self.pack_start(self.pbar)
        self.pack_start(self.scrolltext)

        ## Lance le défilement
        self.scrolltext.scroll()


    def text_gen(self, team_list):
        """ Génère le texte à faire défiler pour une équipe
        """
        text = ""
        ## Génère le texte pour chaque équipe
        for team in team_list:
            if self.passwd == team.passwd:
                text = text + self.team_text(team, True)
            else:
                text = text + self.team_text(team, False)

        ## Renvoie
        return [ s+'\n' for s in text.split('\n') ]
    
    def get_template(self):
        """ Charge le template du texte
        """
        with open('../data/decrypt_team.txt', 'r') as fichier:
            lines = fichier.readlines()
        lines = ''.join(lines)
        return lines

    def team_text(self, team, good):
        """ Renvoie le texte mis en forme pour l'équipe donnée
        """
        ## Lit le template
        lines = self.get_template()

        ## Met en forme le texte
        lines = lines.replace("NOM", team.nom)
        lines = lines.replace("TAB", "\t")
        if good:
            lines = lines.replace('[OK/KO]', 'OK')
        else:
            lines = lines.replace('[OK/KO]', 'KO')

        ## Renvoie
        return lines

    def quit(self, *parent):
        """ Fonction qui permet de quitter proprement
        """
        ## Ferme ScrollTextBox
        self.scrolltext.quit()

class RootWindow(gtk.Window):
    """ Fenêtre principale pour tester le module
    """
    def __init__(self):
        ## Charge gobject
        gobject.threads_init()

        ## Charge la fenêtre
        gtk.Window.__init__(self)
        self.set_title("Décryptage")
        
        ## DecryptBox
        self.decryptbox = DecryptBox()

        ## Affichage
        self.add(self.decryptbox)
        self.show_all()

        ## Connexion
        self.connect("destroy", self.quit)
    
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
