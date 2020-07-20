#! /usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import RPi.GPIO as GPIO
import subprocess, os, sys, select
from time import sleep

###########################
debug = False
###########################

# OMXCHILD
def child_start():
    proc=subprocess.Popen(['/home/pi/Documents/zigzag/omxchild.sh'], shell=False, \
          stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    pid = proc.pid
    if debug: print "PID: ", pid
    
    # wait until child has started otherwise commands sent get confused
    while proc.poll()!= None:
        sleep(0.1)
    if debug: print 'Subprocess ',pid,' started'
    return proc

# poll child process to see if it is running
def child_running(proc):
    return proc.poll() == None    

# wait for the child process to terminate
def child_wait_for_terminate(proc):
    while proc.poll()!= None:
        sleep(0.1)
    if debug: print 'Child terminated'

# send a command to the child
def child_send_command (command, proc ):
    if debug: print "To child: "+ command
    proc.stdin.write(command)

# PIPE TO OMXPLAYER
def omx_send_control(char,fifo):
    command="echo -n " + char + ">" + fifo
    #command="echo -n $'\x1b\x5b\x42' >" + fifo
    if debug: print "To omx: " + command
    subprocess.call(command, shell=True)

######################################################
###########################

def check_runnable():
    path = "/home/pi/Documents/zigzag/omxchild.sh"
    if os.path.exists(path) == False:
	print "omxchild.sh not found"
	print "arret du programme : bye !"
        sys.exit()
    subprocess.call("chmod +x " + path, shell=True)
    files_err=False
    for path in files:
        if debug: print path
        if os.path.exists(path) == False:
            files_err=True
            print "la video " + path + " n'existe pas"
    if files_err==True:
        print "arret du programme : bye !"
        sys.exit()
    if pins[0] != 0:
	print "la liste 'pins' doit commencer par un zero"
	print "arret du programme : bye !"
        sys.exit()
    if len(names)!=len(files):
	print "les listes 'pins' et 'names' n'ont pas le meme nombre d'elements"
	print "arret du programme : bye !"
        sys.exit()

def close_omx(proc):
    global track
    if os.path.exists(fifo):
        subprocess.call("echo -n q >" + fifo, shell=True)
        child_wait_for_terminate(proc)
        subprocess.call("rm " + fifo, shell=True)
        sleep(0.1)
    ci=0
    while subprocess.call("ps -A | grep omxplayer", shell=True)!=1 and ci<10:
        subprocess.call("killall omxplayer", shell=True)
        sleep(0.1)
        subprocess.call("killall omxplayer.bin", shell=True)
        ci = ci+1
        sleep(0.1)

def clic(id_movie):
    global track, clicked
    if started:
        with tlock: track = movies[id_movie]
        with clock: clicked = True
        if debug: print "ok"



############################################################################################################
# Settings
############################################################################################################
# liste des broches utilisées
pins=[0,23,24,21,25,-1,-1]    # le premier chiffre doit etre 0
# noms des videos
names='menuzz.mp4','chicago.mp4','tradi_inno.mp4','missi_nature_5.mp4','musique_danse_01-2017_9-vimeo.mp4','missi_delta.mp4','civil_rights.mp4'
# repertoire ou sont les videos
di='/home/pi/Documents/zigzag'
############################################################################################################



###########################
# Setup
###########################
if debug: print "initializing..."
files=[di+'/{nn}'.format(nn=name) for name in names]
fifo = "/home/pi/Documents/zigzag/tmp/omxcmd"
check_runnable()
movies = dict(zip(pins,files))
track = movies[0]
clicked = False
started = False
clock=threading.Lock()
tlock=threading.Lock()
###########################
if subprocess.call("ps -A | grep omxplayer", shell=True)!=1:
    subprocess.call("killall omxplayer", shell=True)
    sleep(1)
    subprocess.call("killall omxplayer.bin", shell=True)
sleep(1)
###########################
###########################
# GPIO setup 
###########################
if debug: print "starting GPIO ..."
GPIO.setmode(GPIO.BCM)
sleep(0.5)
for i in pins:
    if i!=0 and i!=-1:
        if debug: print "gpio : activation pin ",i
        GPIO.setup(i, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        sleep(0.1)
        GPIO.add_event_detect(i,GPIO.FALLING,clic,bouncetime=300)
        sleep(0.1)
######################################################
###########################
if debug: print "and GO !"
sleep(1)

while True:
    try:
        started = False 
        if os.path.exists(fifo): subprocess.call("rm " + fifo, shell=True)
        subprocess.call("mkfifo " + fifo, shell=True)
        proc=child_start()
        # send track and start command to omxplayer through the FIFO
        child_send_command("track " + track + "\n", proc )
        sleep(0.1)
        omx_send_control(' ',fifo)
        sleep(0.2)
        started = True
        while True:
            if debug and clicked: print "CLICK"
            if child_running(proc) == False:
                if debug: print "child now not running - fin video"
                subprocess.call("rm " + fifo, shell=True)
                if not clicked:
                    with tlock: track=movies[0]
                break
            if clicked:
                with clock: clicked = False
                close_omx(proc)
                break
            sleep(0.1)
    except KeyboardInterrupt:
        break
    sleep(0.1)

close_omx(proc)
print('byebye player')
GPIO.cleanup()
print('byebye gpio')
print('bisous les zigzags')

