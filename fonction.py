#!/bin/env python
#-*-coding: utf8 -*-

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
    if string == 'True' or string == 'true':
        return True
    elif string == 'False' or string == 'false':
        return False
    else:
        raise ValueEroor("'%s' n'est pas dans ['True', 'true', 'False', 'false']"%(string))

