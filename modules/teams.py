#!/usr/bin/env python
# *-* coding:utf-8 *-*

import pygtk
pygtk.require("2.0")
import gtk

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
    def __init__(self):
        gtk.Label.__init__(self)
        self.set_text("Vide")
        self.team_list = []

    def addTeam(self,name):
        newTeam = team(name)
        self.team_list.append(newTeam)

    def printTeam(self):
        if len(self.team_list):
            self.set_alignment(0,0)
            self.set_use_markup(True)
            self.set_padding(5,5)
            tmp = ""
            for team in self.team_list:
                tmp += "<b>"+team.nom+":</b> "+team.passwd+"\n"
            self.set_text(tmp)
            self.set_use_markup(True)

    def selectTeam(self,team):
        filter = lambda x: x.nom == team
        for i in self.team_list:
            if filter(i):
                return i 
        raise TeamError(team,"Cette équipe n'existe pas")

    def addPasswd(self,team,passwd):
        try:
            team_to_modify = self.selectTeam(team)
            team_to_modify.passwd = passwd
        except TeamError as err:
            print err

if __name__ == "__main__":
    rootWindow = gtk.Window()
    rootWindow.set_default_size(300,400)
    rootWindow.set_position(gtk.WIN_POS_CENTER)
    rootWindow.connect("destroy",gtk.main_quit)

    teams = teamBox()

    teams.addTeam("blabla")
    teams.addTeam("blublu")
    teams.addPasswd("blibli","aaa") # Ne marche pas (équipe inexistante)
    teams.addPasswd("blublu","aaa") # Modification effective du passwd de l'équipe
    teams.printTeam()

    rootWindow.add(teams)

    rootWindow.show_all()
    gtk.main()
