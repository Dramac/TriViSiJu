#!/usr/bin/env python
# *-* coding:utf-8 *-*

import pygtk
pygtk.require("2.0")
import gtk
import pickle
import os

class TeamError(Exception):
    """Exception levée lors de la mauvaise manipulation d'équipe"""
    def __init__(self,team,message):
        self.team = team
        self.message = message
    def __str__(self):
        return "Équipe {}: {}".format(self.team,self.message)

class team():
    def __init__(self,nom):
        self.nom = nom
        self.passwd = ""
    def __repr__(self):
        """Surcharge de l'opérateur repr"""
        return self.nom
    def __str__(self):
        """Surcharge de l'opérateur print"""
        return "Équipe {}".format(self.nom)

class teamBox(gtk.Label):
    def __init__(self,fichier=os.path.join(os.path.dirname(__file__), "teams.dat")):
        gtk.Label.__init__(self)
        self.set_text("Vide")
        self.team_list = []
        self.fichier = fichier

    def addTeam(self,name):
        """Ajouter une équipe à la liste"""
        newTeam = team(name)
        self.team_list.append(newTeam)
        self.printTeams()

    def addPasswd(self,team_name,passwd):
        try:
            team = self.selectTeam(team_name)
            team.passwd = passwd
        except TeamError as err:
            print err
        self.printTeams()

    def printTeams(self):
        """Affichage des équipes dans le panneau"""
        if len(self.team_list):
            self.set_alignment(0,0)     # Alignement à gauche
            self.set_use_markup(True)   # Mise en forme Markup
            self.set_padding(5,5)       # Marge de 5px avec les bords

            ## Mise en forme de la sortie
            tmp = ""
            for team in self.team_list:
                tmp += "<b>"+team.nom+":</b>\t\t "+team.passwd+"\n"
            self.set_text(tmp)
            self.set_use_markup(True)

    def selectTeam(self,team_name):
        """Sélecteur d'équipe pour modification"""
        filter = lambda x: x.nom == team_name # Création du filtre
        for team in self.team_list:
            if filter(team):
                return team
        raise TeamError(team_name,"Cette équipe n'existe pas")

    def save(self):
        """Sauvegarde des équipes créées"""
        with open(self.fichier,'w') as fichier:
            pickle.Pickler(fichier).dump(self.team_list)

    def load(self):
        """Chargement des équipes sauvées"""
        with open(self.fichier,'r') as fichier:
            self.team_list = pickle.Unpickler(fichier).load()
        self.printTeams()

if __name__ == "__main__":
    # Fenêtre de test et d'exemple
    rootWindow = gtk.Window()
    rootWindow.set_default_size(300,400)
    rootWindow.set_position(gtk.WIN_POS_CENTER)
    rootWindow.connect("destroy",gtk.main_quit)

    teams = teamBox()
    teams.addTeam("SpaceX")
    teams.addTeam("ESA")
    teams.addTeam("NASA")
    teams.addTeam("JAXA")
    teams.addPasswd("ESA","123456")
    teams.save()

    rootWindow.add(teams)

    rootWindow.show_all()
    gtk.main()
