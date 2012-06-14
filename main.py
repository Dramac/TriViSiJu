#!/usr/bin/env python
# *-* coding:utf-8 *-*

""" TriViSiJu: Graphical interface for the AstroJeune Festival
    
	Copyright (C) 2012  Jules DAVID, Tristan GREGOIRE, Simon NICOLAS and Vincent PRAT

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pygtk
pygtk.require("2.0")
import gtk
from modules import *
from fonction import conf2dict, str2bool
import time
import os
import ConfigParser
import sys
import argparse

class MainWindow(gtk.Window):
    """ Fenêtre principale
    """

    def __init__(self, **kwarg):
        """ Constructeur de la fenêtre principale
        """
        ## Initialise la fenêtre
        gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
        self.set_title("TriViSiJu")
        self.set_default_size(800,600)
        self.set_position(gtk.WIN_POS_CENTER)

        ## Création de 4 boîtes
        # \-rootBox
        #   \-leftBox
        #       '-text1 : Vidéo Ariane V sur le pas de tir
        #       '-séparateur
        #       \-text2 : Vidéo Satellite/Sonde ou Modélisation 3D Ariane
        #   \-centerBox
        #       '-coutdown
        #       '-séparateur
        #       '-text4
        #       \-séparateur
        #   \-rightBox
        #       '-text6 : Caractéristiques techniques
        #       '-séparateur
        #       \-text7 : Liste des équipes
        rootBox = gtk.HBox(homogeneous=False,spacing=0)
        leftBox = gtk.VBox(homogeneous=False,spacing=0)
        centerBox = gtk.VBox(homogeneous=False,spacing=0)
        rightBox = gtk.VBox(homogeneous=False,spacing=0)

        # Vidéos
        ## Charge la classe Player
        self.screen1 = PlayerFrame(self, 1, quitb=kwarg['quitb'], forcebutton=kwarg['forcebutton'])
        self.screen2 = PlayerFrame(self, 2, quitb=kwarg['quitb'], forcebutton=kwarg['forcebutton'])

        ## Compte à rebours
        self.countdown = countdownBox(forcebutton=kwarg['forcebutton'])
        self.countdown.setStartTime(h=0,m=0,s=48,cs=0)

        ## Texte crypté
        self.scrolltextbox = ScrollTextBox(forcebutton=kwarg['forcebutton'], speed=kwarg['speed'], crypt=kwarg['crypt'])

        ## Prompt
        self.prompt = promptBox(self)

        ## Caractéristiques techniques
        text6 = gtk.Label("<b>Panneau haut droite</b>\nCaractéristiques techniques")
        text6.set_use_markup(True)

        ## Liste des équipes
        self.teamBox = teamBox()
        self.prompt.connect("add-team", self.teamBox.addTeam)
        #self.teamBox.addTeam("SpaceX")
        #self.teamBox.addTeam("ESA")
        #self.teamBox.addTeam("NASA")
        #self.teamBox.addTeam("JAXA")
        #self.teamBox.addPasswd("ESA","123456")
        #self.teamBox.save()
        #self.teamBox.load()
        
        ## Affichage des textes provisoires
        #leftBox
        leftBox.pack_start(self.screen1,True,True,0)
        leftBox.pack_start(gtk.HSeparator(),True,True)
        leftBox.pack_start(self.screen2,True,True,0)
        #centerBox
        centerBox.pack_start(self.countdown,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(self.scrolltextbox,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(self.prompt,True,True)
        #rightBox
        rightBox.pack_start(text6,True,True)
        rightBox.pack_start(gtk.HSeparator(),True,True)
        rightBox.pack_start(self.teamBox,True,True)

        ## Ajout des sous-boîtes (leftBox, centerBox, rightBox) dans rootBox
        rootBox.pack_start(leftBox,True,True,0)
        rootBox.pack_start(gtk.VSeparator(),True,True,0)
        rootBox.pack_start(centerBox,True,True,0)
        rootBox.pack_start(gtk.VSeparator(),True,True,0)
        rootBox.pack_start(rightBox,True,True,0)

        ## Ajout de rootBox sur la fenêtre principale
        self.add(rootBox)
        
        ## Affichage général
        self.show_all()
        
        ## Envoie de l'id à mplayer après l'avoir affiché
        self.screen1.Screen.setwid(long(self.screen1.Screen.get_id()))
        self.screen2.Screen.setwid(long(self.screen2.Screen.get_id()))
        
        ## Charge la/les vidéo(s)
        self.loadmovie(kwarg['videopath1'], 1)
        self.loadmovie(kwarg['videopath2'], 2)

        ## Lance le timer et le défilement
        if not kwarg['forcebutton']:
            # Lance le timer
            self.countdown.start()
            # Défilement
            self.scrolltextbox.scroll()
        
        ## Connexion de destroy à la fonction quit
        self.connect("destroy", lambda w: self.quit())

    def loadmovie(self, videoPath, id):
        """ Charge la video si elle existe
        """
        ## Test videoPath
        if os.path.isfile(videoPath):
            exec("self.screen%s.Screen.loadfile('%s')"%(id, videoPath.replace(' ', '\ ')))

    def quit(self, *parent):
        """ Fonction quitter
        
        Tue proprement l'application root
        """
        ## Envoie le signal à mplayer
        self.screen1.Screen.quit()
        self.screen2.Screen.quit()
        ## Envoie le signal à ScrollTextBox
        self.scrolltextbox.quit()
        ## Attend que mplayer se soit éteint
        time.sleep(0.1)
        ## Tue l'application root
        gtk.main_quit()

if __name__=="__main__":
    ## Licence
    licence = """
    TriViSiJu  Copyright (C) 2012 Jules DAVID, Tristan GREGOIRE, Simon NICOLAS and Vincent PRAT
    This program comes with ABSOLUTELY NO WARRANTY; for details type `./main.py -h'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `./main.py -h' for details.
    """
    print licence

    ## Descrition
    description = """ Application Grand Jeu : TriViSiJu
    
    Développé pour le Festival AstroJeune 2012
    """
    class Arg(object):
        """ Permet de renvoyer les arguments du parser sans utiliser de liste
        Voir http://docs.python.org/library/argparse.html#argparse.Namespace
        """
        pass
    
    ## Parse  les arguments
    args = Arg() # Conteneur pour les arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--config', metavar='FILE', type=str,\
                        default=os.path.join(os.getcwd(), 'TriViSiJu.cfg'), action='store',\
                        help="Fichier de configuration")
    parser.add_argument('-s', '--section', metavar='STRING', type=str,\
                        default='Default', action='store',\
                        help="Section de paramètres à charger")
    parser.parse_args(sys.argv[1:], namespace=args) # Parse les arguments dans la classe conteneur
    
    ## Charge les paramètres
    if args.config != None and os.path.isfile(args.config):
        config = ConfigParser.RawConfigParser()
        config.read(args.config)
        if 'section' in dir(args) and config.has_section(args.section):
            kwarg = conf2dict(config.items(args.section))
        else:
            print "ATTENTION : la secion '%s' n'existe pas dans le fichier de configuration '%s'"%(args.section, args.config)
            kwarg = conf2dict(config.items('Default'))

    
    ## Convertit les string True/False en booléen
    for key, val in kwarg.iteritems():
        if val in ['True', 'False', 'true', 'false']:
            kwarg[key] = str2bool(val)
        else:
            try:
                kwarg[key] = float(val)
            except ValueError:
                pass

    ## Charge gobject (Important pour ScrollTextBox
    gobject.threads_init()
    
    ## arg et kwarg
    MainWindow(**kwarg)
    gtk.main()
