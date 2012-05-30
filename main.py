#!/usr/bin/env python
# *-* coding:utf-8 *-*

import pygtk
pygtk.require("2.0")
import gtk
from modules import *
from fonction import conf2dict, str2bool
import time
import os
import ConfigParser
import argparse
import sys

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

        ## Compte à rebours
        self.countdown = countdownBox()
        self.countdown.setStartTime(h=0,m=0,s=48,cs=0)
        self.countdown.showControl()
        #self.countdown.start()

        ## Textes provisoires
        #REMtext1 = gtk.Label("<b>Panneau haut gauche</b>\nVidéo Ariane V sur le pas de tir")
        #REMtext1.set_use_markup(True)
        #REMtext2 = gtk.Label("<b>Panneau bas gauche</b>\nVidéo Satellite/Sonde ou Modélisation 3D Ariane")
        #REMtext2.set_use_markup(True)
        text4 = gtk.Label("<b>Texte crypté</b>")
        text4.set_use_markup(True)
        text5 = gtk.Label("<b>Prompt</b>")
        text5.set_use_markup(True)
        text6 = gtk.Label("<b>Panneau haut droite</b>\nCaractéristiques techniques")
        text6.set_use_markup(True)
        text7 = gtk.Label("<b>Panneau bas droite</b>\nListe des équipes")
        text7.set_use_markup(True)
        
        ## Charge la classe Player
        self.screen1 = PlayerFrame(self, 1, quitb=kwarg['quitb'], forcebutton=kwarg['forcebutton'])
        self.screen2 = PlayerFrame(self, 2, quitb=kwarg['quitb'], forcebutton=kwarg['forcebutton'])

        ## Affichage des textes provisoires
        #leftBox
        #REMleftBox.pack_start(text1,True,True,0)
        leftBox.pack_start(self.screen1,True,True,0)
        leftBox.pack_start(gtk.HSeparator(),True,True)
        #REMleftBox.pack_start(text2,True,True)
        leftBox.pack_start(self.screen2,True,True,0)
        #centerBox
        centerBox.pack_start(self.countdown,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(text4,True,True)
        centerBox.pack_start(gtk.HSeparator(),True,True)
        centerBox.pack_start(text5,True,True)
        #rightBox
        rightBox.pack_start(text6,True,True)
        rightBox.pack_start(gtk.HSeparator(),True,True)
        rightBox.pack_start(text7,True,True)

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
        
        ## Connexion de destroy à la fonction quit
        self.connect("destroy", lambda w: self.quit())

    def loadmovie(self, videoPath, id):
        """ Charge la video si elle existe
        """
        ## Test videoPath
        if os.path.isfile(videoPath):
            exec("self.screen%s.Screen.loadfile('%s')"%(id, videoPath.replace(' ', '\ ')))

    def fullscreen(self):
        """ Met en plein écran
        """
        ##TODO: connecter cette fonction à un racourcis clavier ou un menu
        self.fullscreen()
        
    def quit(self, *parent):
        """ Fonction quitter
        
        Tue proprement l'application root
        """
        ## Envoir le signal à mplayer
        self.screen1.Screen.quit()
        self.screen2.Screen.quit()
        ## Attend que mplayer se soit éteint
        time.sleep(0.1)
        ## Tue l'application root
        gtk.main_quit()

if __name__=="__main__":
    ## Descrition
    description = """ Application Grand Jeu : TriViSiJu
    
    Développé pour le Festival Astro Jeuve de Fleurance 2012
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
                        default=os.path.join(os.getcwd(), 'TriViSiJurc'), action='store',\
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
            kwarg = conf2dict(config.items('Default'))
    
    ## Convertit les string True/False en booléen
    for key, val in kwarg.iteritems():
        if val in ['True', 'False', 'true', 'false']:
            kwarg[key] = str2bool(val)
    
    ## arg et kwarg
    MainWindow(**kwarg)
    gtk.main()
