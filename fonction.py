#!/bin/env python
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

def conf2dict(liste):
    """ Convertit la liste renvoyée par le ConfigParser de python en dictionnaire.
    
    La liste est de la forme ((variable1, valeur1), (variable2, valeur2), ...)
    Voir http://docs.python.org/library/configparser.html#ConfigParser.RawConfigParser.items
    """
    dictionnaire = {}
    ## Parcours de la liste
    for lst in liste:
        dictionnaire.setdefault(lst[0], lst[1])
    
    ## Renvoie le dictionnaire
    return dictionnaire

def str2bool(string):
    """ Convertit une string True/False en booléen
    """
    print "coucou", string
    if string == 'True' or string == 'true':
        return True
    elif string == 'False' or string == 'false':
        return False
    else:
        raise ValueError("'%s' n'est pas dans ['True', 'true', 'False', 'false']"%(string))

