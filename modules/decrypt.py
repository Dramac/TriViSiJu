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
import gobject
import teams
import time

class DecryptBox(gtk.VBox):
    """ Fenêtre de décryptage
    """

    def __init__(self, passwd="passwd", team_list=[teams.team("Orion1", passwd="asswd"), teams.team("Pegase2", passwd="Passwd"), teams.team("Ariane3", passwd="")],data_folder="data/"):
        """ Initialisation
        """
        ## Initialise la fenetre
        gtk.VBox.__init__(self)

        ## Charge les variables
        self.has_at_least_one_time = False
        self.passwd = passwd
        self.team_list = team_list
        self.nteam = len(self.team_list)
        self.percent = 0.0
        self.data_folder = data_folder

        ## Initialise la barre de progression
        self.pbar = gtk.ProgressBar()
        self.pbar.set_size_request(500, 50)
        self.update_pbar(team_data=("", 0))
        self.continuer=True

        ## Scroll text
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.textview)
        self.scrolledwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        self.set_size_request(500, 300)

        ## Buffer
        self.buffer = self.textview.get_buffer()

        ## Affichage sur self
        self.pack_start(self.pbar, expand=False, fill=True, padding=0)
        self.pack_start(self.scrolledwindow, True, True, 0)

        ## Signaux
        gobject.signal_new("team-update",DecryptBox,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING,gobject.TYPE_BOOLEAN])

    def setTeams(self,team_list):
        self.team_list = team_list
        self.nteam = len(self.team_list)

    def phase1(self):
        """ La phase 1 consiste à tester le mot de passe de toute les équipes
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
        if self.nteam == 0:
            self.continuer = False

        ## Boucle sur toutes les équipes
        while self.continuer:
            ## Recupere la classe de l'équipe
            team = self.team_list[num]
            passwd_check = False
            if self.passwd == team.passwd:
                at_least_one_passwd = True
                passwd_check = True

            ## Met à jour le texte de la barre
            self.update_pbar(team_data=(team.name, num+1))

            ## Génère le texte de l'équipe
            text = self.team_text(team).split('\n')

            ## Boucle sur les lignes
            for line in text:
                time.sleep(1)
                count = count + 1
                self.update_pbar(percent=float(count)/total)
                self.text = self.text + '\n' + line
                self.update_buffer(self.text)

            self.emit("team-update",team.name,passwd_check)

            ## Incrémente le compteur
            num = num + 1

            ## Arrêt de la boucle while
            if num >= self.nteam:
                self.continuer = False
            time.sleep(2)

        ## Renvoie at_least_one_passwd
        return at_least_one_passwd

    def update_buffer(self, text):
        """ Met à jour le buffer et fait défiler le texte
        """
        ## Met à jour le buffer
        self.buffer.set_text(text)
        ## Fait défiler le text
        adj = self.scrolledwindow.get_vadjustment()
        adj.set_value( adj.upper - adj.page_size )
        while gtk.events_pending():
            gtk.main_iteration()

    def show_warning_and_continue(self, msg):
        """ Montre que le mot de passe a été trouvé et valide le décryptage
        """
        label = gtk.Label(msg.decode('utf-8'))
        dialog = gtk.Dialog("Décryptage réussi")
        dialog.vbox.pack_start(label)
        label.show()
        dialog.run()
        dialog.destroy()

    def phase2(self):
        """ Montre des messages d'erreur et lance une procédure de récupération 
        du mot de passe à partir de tous ceux trouvé par chaque équipe
        """
        ## Lecture du fichier 'phase2'
        with open(self.data_folder+'decrypt_msg_phase2.txt') as f:
            lines = f.readlines()

        ## Activation de la barre de progression en mode activité
        self.pbar.set_text("")
        self.pbar.set_orientation(gtk.PROGRESS_RIGHT_TO_LEFT)

        ## Affichage du fichier 'phase2'
        nlines = len(lines)
        n = 0
        while self.continuer:
            line = lines[n]
            time.sleep(0.1)
            self.update_pbar(percent=float(n+1)/float(nlines))
            self.text = self.text + line
            self.update_buffer(self.text)
            n = n + 1
            if n >= nlines:
                self.continuer = False

    def start(self):
        """ Lance la procédure de décryptage
        """
        ## Set has_at_least_one_time
        self.has_at_least_one_time = True

        ## Reset les variables
        self.text = ""
        self.continuer = True
        self.update_pbar(team_data=("", 0))
        self.pbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)

        ## Lancement de la phase 1
        win = self.phase1()

        ## Test la réussite
        if win:
            msg = self.msg_from_file(self.data_folder+'decrypt_msg_phase1win.txt')
            self.show_warning_and_continue(msg)
        else:
            self.continuer = True
            self.phase2()
            msg = self.msg_from_file(self.data_folder+'decrypt_msg_phase2win.txt')
            self.show_warning_and_continue(msg)

    def msg_from_file(self, filename):
        """ Lit un message depuis un fichier
        """
        with open(filename, 'r') as f:
            msg = f.readlines()
        msg = "".join(msg)
        return msg

    def update_pbar(self, percent=None, team_data=None):
        """ Met à jour le texte de la barre de progression
        """
        ## Met à jour percent
        if percent != None:
            if percent > 1.0:
                percent = 1.0
            self.percent = percent
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
        with open(self.data_folder+'decrypt_team.txt', 'r') as fichier:
            lines = fichier.readlines()
        lines = ''.join(lines)
        return lines

    def team_text(self, team):
        """ Renvoie le texte mis en forme pour l'équipe donnée
        """
        ## Lit le template
        lines = self.get_template()

        ## Met en forme le texte
        lines = lines.replace("NOM", team.name)
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

class popupWindow(gtk.Window):
    """ Fenêtre principale pour tester le module
    """
    def __init__(self,showcontrol=False,dataf="data/", passwd="passwd"):
        ## Charge gobject (Important pour ScrollTextBox)
        gobject.threads_init()
        gobject.signal_new("team-ask-teams",popupWindow,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("team-update",popupWindow,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING, gobject.TYPE_BOOLEAN])
        gobject.signal_new("main-enigme", popupWindow, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_INT])

        ## Charge la fenêtre
        gtk.Window.__init__(self)
        self.set_title("Décryptage")
        self.ready = False

        ## Boutton
        button = gtk.Button(label="start")

        ## DecryptBox
        self.decryptbox = DecryptBox(data_folder=dataf, passwd=passwd)
        self.decryptbox.connect("team-update",self.onUpdateTeam)

        ## Affichage
        if showcontrol:
            vbox = gtk.VBox()
            vbox.pack_start(self.decryptbox, True, True, 0)
            vbox.pack_start(button, True, True, 0)
            self.add(vbox)
        else:
            self.add(self.decryptbox)

        ## Connexion
        self.connect("destroy", self.quit)
        button.connect("clicked", self.start)

    def onUpdateTeam(self,sender,team_name,check):
        self.emit("team-update",team_name,check)

    def start(self, *parent):
        self.emit("team-ask-teams")

    def getTeams(self,sender,team_list):
        self.decryptbox.setTeams(team_list)
        self.show_all()
        self.decryptbox.start()

    def quit(self, *parent):
        """ Fonction qui permet de quitter proprement
        """
        ## Affichage des énigmes
        self.emit("main-enigme", 0)

        ## Ferme ScrollTextBox
        #self.decryptbox.quit()
        self.hide_all()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    r = popupWindow(showcontrol=True,dataf="../data/")
    r.show_all()
    r.main()
