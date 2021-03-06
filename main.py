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
import gobject

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
        self.all_is_fine = False

        # Definition d'une couleur
        bgcolor = gtk.gdk.color_parse(kwarg['background'])
        self.modify_bg(gtk.STATE_NORMAL, bgcolor)

        ## Table
        self.grid = gtk.Table(rows=6, columns=7, homogeneous=True)
        rightBox = gtk.VBox(homogeneous=False,spacing=0)

        ## Prompt
        self.prompt = promptBox(**kwarg)

        # Vidéos
        ## Charge la classe Player
        self.screen = PlayerFrame(self, 1, quitb=kwarg['quitb'], forcebutton=kwarg['forcebutton'], bgcolor=bgcolor)

        # Gstreamer
        self.gsplayer = SongPlayer(filename=kwarg['alarm_file'])

        ## Compte à rebours
        self.countdown = countdownBox(forcebutton=kwarg['forcebutton'],size=kwarg['timer_size'])
        #self.countdown.setStartTime(h=0,m=0,s=48,cs=0)

        ## Texte crypté
        self.scrolltextbox = ScrollTextBox(forcebutton=kwarg['forcebutton'], speed=kwarg['speed'], crypt=kwarg['crypt'], foreground=kwarg['foreground'], background=kwarg['background'])

        ## Caractéristiques techniques
        self.caractBox = caractBox(delay=kwarg['caract_delay'],max_line=kwarg['caract_max_line'],width=kwarg['caract_width'],foreground=kwarg['foreground'])

        ## Liste des équipes
        self.teamBox = teamBox(foreground=kwarg['foreground'])

        ## Popup window de décryptage
        self.decrypt = popupWindow(passwd=kwarg['passwd'], imagefile=kwarg['imagefile'], background=kwarg['background'], foreground=kwarg['foreground'])

        ## Poup window des énigmes
        self.enigme = PopupWindow(forcebutton=kwarg['forcebutton'], foreground=kwarg['foreground'], background=kwarg['background'])

        ## Table
        self.grid.attach(self.screen,        0, 4, 0, 3, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.teamBox,       0, 1, 3, 6, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.caractBox,     2, 4, 3, 6, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.countdown,     4, 7, 0, 1, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.scrolltextbox, 4, 7, 1, 4, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.prompt,        4, 7, 4, 6, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)

        ## Ajout de self.grid sur la fenêtre principale
        self.add(self.grid)

        ## Affichage général
        self.show_all()

        ## Envoie de l'id à mplayer après l'avoir affiché
        self.screen.Screen.setwid(long(self.screen.Screen.get_id()))

        # Signaux :
        ## vers main
        self.prompt.connect("main-minimize", self.onMinimize)
        self.prompt.connect("main-fullscreen", self.on_fullscreen)
        self.prompt.connect("main-quit", self.quit)
        self.scrolltextbox.connect("main-decrypt-suite", self.onDecrypt)
        self.decrypt.connect("main-enigme", self.onDecrypt)
        self.prompt.connect("main-start", self.onStart, kwarg['videoend'])
        self.prompt.connect("gsplayer-play", self.onAlarm)
        ## vers prompt
        self.teamBox.connect("prompt-message",self.prompt.onExternalInsert)
        self.teamBox.connect("decrypt-send-teams",self.decrypt.getTeams)
        self.countdown.connect("prompt-message",self.prompt.onExternalInsert)
        ## de prompt vers teambox
        self.prompt.connect("team-add", self.teamBox.addTeam)
        self.prompt.connect("team-delete", self.teamBox.deleteTeam)
        self.prompt.connect("team-passwd", self.teamBox.addPasswd)
        self.prompt.connect("team-load", self.teamBox.load)
        self.prompt.connect("team-save", self.teamBox.save)
        self.prompt.connect("team-clear", self.teamBox.clearTeams)
        ## de prompt vers decrypt
        self.prompt.connect("decrypt",self.decrypt.start)
        ## de prompt vers countdown
        self.prompt.connect("timer-start", self.countdown.start)
        self.prompt.connect("timer-stop", self.countdown.pause)
        self.prompt.connect("timer-reset", self.countdown.reset)
        self.prompt.connect("timer-set", self.countdown.setStartTime)
        self.prompt.connect("timer-resize", self.countdown.resize)
        ## de prompt vers video
        self.prompt.connect("video-load", self.screen.Screen.loadFile)
        self.prompt.connect("video-pause", self.screen.Screen.pause)
        self.prompt.connect("video-forward", self.screen.Screen.forward)
        self.prompt.connect("video-backward", self.screen.Screen.backward)
        ## de prompt vers scrolltext
        self.prompt.connect("scroll", self.scrolltextbox.scroll)
        self.prompt.connect("scroll-on", self.scrolltextbox.scroll_on)
        self.prompt.connect("scroll-crypt", self.scrolltextbox.toggle_crypt)
        self.prompt.connect("scroll-speed", self.scrolltextbox.set_speed)
        self.prompt.connect("scroll-file", self.scrolltextbox.set_filename)
        ## de prompt vers caract
        self.prompt.connect("caract-start",self.caractBox.start)
        self.prompt.connect("caract-max-line",self.caractBox.changeMaxLine)
        self.prompt.connect("caract-width",self.caractBox.changeWidth)
        ## de prompt vers enigme
        self.prompt.connect("indice", self.onIndice)
        ## de decrypt vers les autres
        self.decrypt.connect("team-ask-teams",self.teamBox.sendTeams)
        self.decrypt.connect("team-update",self.teamBox.updateTeam)
        ## Connexion de destroy à la fonction quit
        self.connect("destroy", self.quit)
        ## Connexion du signal de changement d'état de la fenêtre
        self.connect("window-state-event", self.onStateChange)

        ## Règle le timer
        self.prompt.onTimer(['set']+kwarg['timer'].split(' '))

    def on_fullscreen(self, sender=None):
        """ Slot de mise en plein écran """
        if self.full:
            self.unfullscreen()
        else:
            self.fullscreen()

    def onStateChange(self, window, event):
        """ Méthode appelée quand l'état de la fenêtre change
        """
        if event.new_window_state and gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.full = True
        else:
            self.full = False
        if event.changed_mask and gtk.gdk.WINDOW_STATE_ICONIFIED:
            if event.new_window_state and gtk.gdk.WINDOW_STATE_ICONIFIED:
                self.icon = True
            else:
                self.icon = False

    def loadmovie(self, videoPath):
        """ Charge la video si elle existe
        """
        ## Test videoPath
        if os.path.isfile(videoPath):
            self.screen.Screen.loadFile(filename = videoPath.replace(' ', '\ '))

    def onMinimize(self, sender=None):
        """ Minimise la fenêtre principale """
        if self.icon:
            self.deiconify()
        else:
            self.iconify()

    def onDecrypt(self, sender=None, step=0):
        """ Commence la phase de lancement """
        if step == 0:
            ## Fait ralentir le défilement du texte jusqu'à totalement s'arrêter
            gobject.timeout_add(1000, self.scrolltextbox.reduce2stop)
        elif step == 1:
            ## Caractéristique no->ok
            gobject.timeout_add(2000, self.onSchedule, self.caractBox.changePhase)
            ## Decrypte le texte
            gobject.timeout_add(2000, self.onSchedule, self.scrolltextbox.show_clear_text)
            ## Set all_is_fine -> True (self.onStart)
            self.all_is_fine = True

    def onStart(self, sender=None, video=None):
        """ Lance le décollage de la fusée """
        if self.all_is_fine:
            ## Sortie du plein écran
            if self.full:
                self.on_fullscreen()
            ## Réduction de la fenêtre
            gobject.timeout_add(500, self.onSchedule, self.onMinimize)
            ## Mplayer
            if video == None:
                video = ''
            print "Chargement de la video '%s'"%(video)
            os.system("mplayer -really-quiet -fs %s &"%(video))
            ## Timer
            runtimer = lambda : os.system("python modules/countdown.py -clf -s 10 &")
            gobject.timeout_add(2000, self.onSchedule, runtimer)
        else:
            print "Le texte n'est pas décrypté..."

    def onSchedule(self, function=None):
        """ Permet de lancer un fonction avec gobject.timeout_add après le délais de timeout_add
        """
        if function != None:
            function()
        return False

    def onAlarm(self, sender=None):
        """ Joue une alarm """
        if isinstance(self.gsplayer.filename, str):
            if os.path.isfile(self.gsplayer.filename):
                self.gsplayer.play()
            else:
                self.prompt.onExternalInsert(None, "Pas de fichier son")
        else:
            self.prompt.onExternalInsert(None, "Pas de fichier son")

    def onIndice(self, sender):
        """ Affiche les énigmes
        """
        if self.all_is_fine:
            self.enigme.start()
        else:
            self.prompt.onExternalInsert(None, "Erreur: commande non disponible pour l'instant")

    def quit(self, *parent):
        """ Fonction quitter

        Tue proprement l'application root
        """
        ## Envoie le signal à mplayer
        self.screen.Screen.quit()
        ## Envoie le signal à ScrollTextBox
        self.scrolltextbox.quit()
        ## Attend que mplayer se soit éteint
        time.sleep(0.1)
        ## Tue l'application root
        gtk.main_quit()

if __name__=="__main__":
    ## Python change curent repertory
    os.chdir(os.path.dirname(__file__))

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
