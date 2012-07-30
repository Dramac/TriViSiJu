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
import fnmatch
import os


class ScrolledLabelBox(gtk.VBox):
    def __init__(self,delay=1000,max_line=15,width=50,lines=[], foreground="white"):
        ## Initialise gtk.VBox, gtk.HBox
        gtk.VBox.__init__(self)
        self.lines = lines
        self.delay = int(delay)          # Temps en ms entre deux appels de la fonction onTimeout
        self.max_line = int(max_line)    # Nombre de lignes à afficher au maximum
        self.width = int(width)          # Nombre de caractères par lignes
        self.phase = "init"         # si init, affiche des NO rouges, sinon affiche des OK verts
        self.timer = None
        self.cursor = 0
        self.team = ""
        self.updated_team = []
        self.foreground = foreground

        self.text = gtk.Label()
        self.text.set_alignment(0,0)
        self.add(self.text)
        gobject.signal_new("team-update",DecryptBox,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING,gobject.TYPE_BOOLEAN])
        gobject.signal_new("interne-stop", ScrolledLabelBox, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])

    def start(self,sender=None):
        if self.timer is None:
            self.timer = gobject.timeout_add(self.delay,self.onTimeout)

    def pause(self,sender=None):
        if self.timer:
            gobject.source_remove(self.timer)
            self.timer = None

    def changeMaxLine(self,sender,new_max_line):
        self.max_line = int(new_max_line)

    def changeWidth(self,sender,new_width):
        self.width = int(new_width)

    def changePhase(self,sender=None):
        if self.phase == "init":
            self.phase = "clear"
        else:
            self.phase = "init"

    def append(self,text_to_append, root="équipe "):
        """Ajouter du texte à la fin du texte déjà écrit"""

        # On ne garde que les N dernières lignes
        previous_text = self.text.get_label().split("\n")
        if len(previous_text) > self.max_line:
            previous_text = previous_text[-self.max_line:]
        previous_text = "\n".join(previous_text)

        # On supprime la mise en forme générale, qui vient perturber l'insertion
        ## d'abord le début
        previous_text = previous_text.replace("<span foreground='%s' font_desc='Monospace'>"%(self.foreground),"",1)
        ## puis la fin
        previous_text = self.rreplace(previous_text,"</span>","",1)

        # On comble en points jusqu'à obtenir la taille de ligne désirée
        if text_to_append == "":
            text_to_append = text_to_append+"\n"
        if not text_to_append[-1] == "\n":
            text_to_append = text_to_append+"\n"
        text_to_append, phase = self.cleanText2append(text_to_append)
        ## Update team
        if root in text_to_append:
            self.team = text_to_append.split(root)[1].replace("'", "").replace("\n", "")
        if not text_to_append == '\n' and not root in text_to_append and phase != None:
            if len(text_to_append) <= self.width - 4:
                dots = "".join(["." for i in range(self.width - len(text_to_append) - 4)])
                if phase:
                    text_to_append = text_to_append.replace("\n","") + dots + "[<span foreground='green'>OK</span>]\n"
                else:
                    text_to_append = text_to_append.replace("\n","") + dots + "[<span foreground='red'>NO</span>]\n"

        # Puis on met le tout en forme (police à chasse fixe)
        next_text = "<span foreground='%s' font_desc='Monospace'>"%(self.foreground)+previous_text+str(text_to_append)+"</span>"
        # et on affiche !
        self.text.set_markup(next_text)
    
    def cleanText2append(self, text_to_append):
        if fnmatch.fnmatch(text_to_append, "*OK*"):
            passwd = True
            text_to_append = text_to_append.replace("[OK]", "")
        elif fnmatch.fnmatch(text_to_append, "*KO*"):
            text_to_append = text_to_append.replace("[KO]", "")
            passwd = False
        else:
            passwd = None
        text_to_append = text_to_append.replace("\t", "")
        if passwd != None and not self.team in self.updated_team:
            self.emit("team-update", self.team, passwd)
            self.updated_team.append(self.team)
        return text_to_append, passwd


    def onTimeout(self, *args):
        """Fonction appelée toutes les self.delay ms"""
        if self.lines != []:
            line = self.lines[self.cursor]
            self.append(line)
            self.cursor += 1
            if self.cursor >= len(self.lines):
                self.emit("interne-stop")
                return False
            return True         # Si True, continue
        else:
            print "WARNING: self.lines = '%s'"%(self.lines)
            return False        # Stop scroll

    def rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

def update_pbar(self, percent=None, team_data=None):
    """ Met à jour le texte de la barre de progression
    """
    ## Met à jour percent
    if percent == None:
        percent = self.percent
    if percent > 1.0:
        percent = 1.0
    ## Met à jour le texte et la valeur de la barre
    self.pbar.set_fraction(percent)
    if team_data == None:
        team_data = self.team
    self.pbar.set_text("Équipe '%s' (%d/%d)"%(team_data[0], team_data[1], self.nteam))

class DecryptBox(gtk.VBox):
    """ Fenêtre de décryptage
    """

    def __init__(self, passwd="passwd", team_list=[teams.team("Orion1", passwd="passwd"), teams.team("Pegase2", passwd="Passwd"), teams.team("Ariane3", passwd="")],data_folder="data/", imagefile=None, background="black", foreground="white"):
        """ Initialisation
        """
        ## Initialise la fenetre
        gtk.VBox.__init__(self)

        ## Charge les variables
        self.has_at_least_one_time = False
        self.passwd = passwd
        self.setTeams(team_list)
        self.team = ("", 0)
        self.percent = 0.0
        self.data_folder = data_folder
        self.win = None
        self.imagefile = imagefile
        self.background = background
        self.foreground = foreground

        ## Label
        self.scrolledlabel = ScrolledLabelBox(foreground=self.foreground)

        ## Size request
        self.scrolledlabel.set_size_request(800, 300)

        ## Affichage sur self
        self.pack_start(self.scrolledlabel, True, True, 0)

        ## Signaux
        self.scrolledlabel.connect("interne-stop", self.onStop)

    def setTeams(self,team_list):
        """ Initialize les equipe """
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

        text = []
        ## Boucle sur toutes les équipes
        for num, team in enumerate(self.team_list):
            passwd_check = False
            if self.passwd == team.passwd:
                at_least_one_passwd = True
                passwd_check = True

            ## Génère le texte de l'équipe
            text = text + self.team_text(team).split('\n')

        ## Renvoie at_least_one_passwd
        return text, at_least_one_passwd

    def show_warning_and_continue(self, msg, root=None):
        """ Montre que le mot de passe a été trouvé et valide le décryptage
        """
        ## Message : Image + Texte
        hbox = gtk.HBox()
        # Image
        image = gtk.Image()
        if self.imagefile != None:
            if os.path.isfile(self.imagefile):
                pixbuf = gtk.gdk.pixbuf_new_from_file(self.imagefile)
                scaled_buf = pixbuf.scale_simple(150,150,gtk.gdk.INTERP_BILINEAR)
                image.set_from_pixbuf(scaled_buf)
            else:
                print "'%s' does not exist"%(self.imagefile)
        else:
            image.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
        # Texte
        label = gtk.Label()
        text = "<span foreground='%s' font_desc='Monospace'>"%(self.foreground)+msg.decode('utf-8')+"</span>"
        label.set_markup(text)
        label.set_line_wrap(True)
        # Pack_start
        hbox.pack_start(image, True, True, 5)
        hbox.pack_start(label, True, True, 5)

        ## Affiche la fenêtre
        dialog = gtk.Dialog("Décryptage réussi", root, gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_NO_SEPARATOR)
        bgcolor = gtk.gdk.color_parse(self.background)
        dialog.modify_bg(gtk.STATE_NORMAL, bgcolor)
        dialog.vbox.pack_start(hbox)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def phase2(self):
        """ Montre des messages d'erreur et lance une procédure de récupération 
        du mot de passe à partir de tous ceux trouvé par chaque équipe
        """
        ## Lecture du fichier 'phase2'
        with open(self.data_folder+'decrypt_msg_phase2.txt') as f:
            lines = f.readlines()
        return lines

    def start(self):
        """ Lance la procédure de décryptage
        """
        ## Set has_at_least_one_time
        self.has_at_least_one_time = True

        ## Génération du texte à faire défiler
        text1, self.win = self.phase1()
        if not self.win:
            text2 = self.phase2()
        else:
            text2 = []
        lines = text1 + text2

        ## Faire défiler le texte
        self.scrolledlabel.lines = lines
        self.scrolledlabel.start()

    def onStop(self, sender=None):
        """ Affiche le message final"""
        ## Test la réussite
        if self.win == None:
            print "Lancer start avant"
        if self.win:
            msg = self.msg_from_file(self.data_folder+'decrypt_msg_phase1win.txt')
            self.show_warning_and_continue(msg)
        else:
            msg = self.msg_from_file(self.data_folder+'decrypt_msg_phase2win.txt')
            self.show_warning_and_continue(msg)

    def msg_from_file(self, filename):
        """ Lit un message depuis un fichier
        """
        with open(filename, 'r') as f:
            msg = f.readlines()
        msg = "".join(msg)
        return msg

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

class popupWindow(gtk.Window):
    """ Fenêtre principale pour tester le module
    """
    def __init__(self,showcontrol=False,dataf="data/", passwd="passwd", imagefile=None, background="black", foreground="white"):
        ## Charge gobject (Important pour ScrollTextBox)
        gobject.signal_new("team-ask-teams",popupWindow,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [])
        gobject.signal_new("team-update",popupWindow,gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_STRING, gobject.TYPE_BOOLEAN])
        gobject.signal_new("main-enigme", popupWindow, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, [gobject.TYPE_INT])

        ## Charge la fenêtre
        gtk.Window.__init__(self)
        self.set_title("Décryptage")
        self.ready = False

        # Definition d'une couleur
        bgcolor = gtk.gdk.color_parse(background)
        self.modify_bg(gtk.STATE_NORMAL, bgcolor)

        ## DecryptBox
        self.decryptbox = DecryptBox(data_folder=dataf, passwd=passwd, imagefile=imagefile, background=background, foreground=foreground)
        self.decryptbox.scrolledlabel.connect("team-update",self.onUpdateTeam)

        ## Affichage
        if showcontrol:
            ## Boutton
            button = gtk.Button(label="start")

            vbox = gtk.VBox()
            vbox.pack_start(self.decryptbox, True, True, 0)
            vbox.pack_start(button, True, True, 0)
            self.add(vbox)
        else:
            self.add(self.decryptbox)

        ## Connexion
        self.connect("destroy", self.quit)
        if showcontrol:
            button.connect("clicked", self.start)

    def onUpdateTeam(self,sender,team_name,check):
        self.emit("team-update",team_name,check)

    def start(self, *parent):
        self.emit("team-ask-teams")
        self.decryptbox.start()

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

