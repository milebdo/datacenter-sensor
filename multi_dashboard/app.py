import time
import os
import signal
import sys

from reporter import Reporter
import unicornhat as UH

def clear_uh():
    UH.clear()
    UH.show()

def sigterm_handler(_signo, _stack_frame):
    clear_uh()
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

# UH.set_layout(UH.PHAT)
#max_pixels = 4
max_pixels = 8

host = os.getenv("REDIS_HOST")
if(host == None):
    host = "redis"

baseline_threshold = os.getenv("TEMP_THRESHOLD")
if(baseline_threshold != None):
    baseline_threshold = float(baseline_threshold)
else:
    baseline_threshold = 0.5

quiet = os.getenv("QUIET")
if(quiet!=None):
    quiet = True
else:
    quiet = False

clear_uh()

r = Reporter(host, "6379")
last_members = []

def on(column, r,g,b):
    x = column
    for y in range(0, max_pixels):
        UH.set_pixel(x, y, r, g, b)
    UH.show()

def safeFloat(motion):
    if motion != None:
        return float(motion)

def is_hot(temp, baseline):
    diff = 0
    if(temp != None and baseline != None):
        baseline_float = round(float(baseline), 2)
        temp_float = round(float(temp), 2)

        diff = abs(temp_float - baseline_float)
        if(quiet == False):
            print("["+str(diff) + "] "+  str(temp_float) + " - " + str(baseline_float))
    return diff > baseline_threshold

def paint():
    global last_members
    index = 0
    members = r.find_members()
    if(len(last_members) != len(members)):
        UH.clear()
        UH.show()

    last_members = members
    for member in members:
        temp = r.get_key(member + ".temp")
        baseline = r.get_key(member + ".temp.baseline")
        motion = r.get_key(member + ".motion")

        if safeFloat(motion) > 0:
            if(quiet == False):
                print("moved")
            on(index, 0, 0, 255)
        elif is_hot(temp, baseline):
            on(index, 255, 0, 0)
            if(quiet == False):
                print("HOT")
        else:
            on(index, 0, 255, 0)
        index = index +1

def on_sensor_data(channel, data):
    if(quiet == False):
        print(channel, data)
    paint()

r.set_on_sensor_data(on_sensor_data)
r.subscribe()

while True:
    if(quiet == False):
        print (r.find_members())
    if(len(r.find_members()) == 0):
        clear_uh()

