#!/bin/bash

# Creation du fichier de vérouillage :
LOCKFILE="/home/pi/Documents/zigzag/lock/$(basename $0)" ;


# Si un fichier de lock existe ...
[ -e ${LOCKFILE} ] && {
        echo "Fichier de lock anterieur..." ;


#       Vérifions si le processus est en cours :
        [ -d /proc/$(cat ${LOCKFILE}) ] && {
                echo "Processus encore actif. Fin." ;
                exit 0 ;
        } || {
#               Si non le fichier à été oublié. Il est supprimé :
                echo "Processus termine. Nettoyage." ;
                rm ${LOCKFILE} ;
        }
}


# Ecriture du fichier de lock :
echo ${$} > ${LOCKFILE} ;

sleep 1 ;
setterm -clear all
sudo python /home/pi/Documents/zigzag/zig-03-17.py
sleep 1 ;

# Nettoyage du fichier de lock :
[ -e ${LOCKFILE} ] && rm ${LOCKFILE} ;










