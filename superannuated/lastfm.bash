#!/bin/bash
/usr/bin/xprop -id `xlsclients -al | /bin/grep lastfm -B3 | /bin/grep "Window" | /usr/bin/cut -d ' ' -f 2| /usr/bin/tr -d ':'` | /bin/grep 'WM_NAME(COMPOUND'
