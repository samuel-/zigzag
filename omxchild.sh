#!/bin/sh

read CC FF
echo child: $CC $FF

if [ $CC = "track" ]; then
	# play the requested file taking commands from /tmp/omxcmd
	# remove >/dev/null to see stdout from omxplayer

	#echo $CC $FF
	#omxplayer -o local -r -b --win "0 0 640 480" $FF < /home/pi/Documents/zigzag/tmp/omxcmd
	omxplayer -o local -r -b $FF < /home/pi/Documents/zigzag/tmp/omxcmd
  	#echo child terminated
	exit
fi

#echo DISCARDED $CC $SS $FF
