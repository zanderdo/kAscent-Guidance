
#version 0.01
import krpc
from time import sleep


def countdown ():
    print("Launching in:\n")
    sleep(0.5)
    print("5")
    sleep(1)
    print("4")
    sleep(1)
    print("3")
    sleep(1)
    print("2")
    sleep(1)
    print("1")
    sleep(1)

def init_rocket(ap):
    pitch_target = 90                                               #define pitch and heading targets
    hdg_target = 90
    set_throttle(100)

    ap.target_pitch_and_heading(pitch_target, hdg_target)
    ap.engage()

def set_throttle(tarThrottle):
    float_tarThrottle = float(tarThrottle / 100)
    vessel.control.throttle = float_tarThrottle

def stage():
    vessel.control.activate_next_stage()

def initial_ascent(ap):
    pitch_target = 80
    hdg_target = 90
    ap.target_pitch_and_heading(pitch_target, hdg_target)

def mid_ascent(ap):
    hdg_target = 90
    pitch_target = 80 - (35 * (vessel.flight().mean_altitude / 9500))
    ap.target_pitch_and_heading(pitch_target, hdg_target)


def high_ascent(ap):
    hdg_target = 90
    pitch_target = 45 - (45 * (vessel.flight().mean_altitude / 45000))
    ap.target_pitch_and_heading(pitch_target, hdg_target)

def orbital_injection(ap):
    ap.target_direction = (0,1,0)

def circularization(ap, circAlt, currResources, currStage):
    while abs(vessel.orbit.apoapsis_altitude - vessel.orbit.periapsis_altitude > 1000):
        ap.target_direction = (0,1,0)
        if (vessel.flight().mean_altitude < circAlt):
            set_throttle(0)
        elif (abs(vessel.orbit.apoapsis_altitude - vessel.orbit.periapsis_altitude > 1000)):
            set_throttle(100)
        else:
            set_throttle(0)
        currStage = check_stage(currResources, currStage)
        currResources = vessel.resources_in_decouple_stage(currStage, False)


def check_stage(currResources, currStage):
    print(currResources.amount("LiquidFuel"))
    print(currStage)
    if (currResources.has_resource("SolidFuel")):
        if (currResources.amount("SolidFuel") <= 49):
            print(currResources.amount("SolidFuel"))
            stage()
            currStage = currStage - 1
            print("CURRSTAGE: ")
            print(currStage)
            currResources = vessel.resources_in_decouple_stage(currStage, False)
    print(currStage)

    if (currResources.has_resource("LiquidFuel")):
        if (currResources.amount("LiquidFuel") <= 1):
            print(currResources.amount("LiquidFuel"))
            stage()
            currStage = currStage - 1
            currResources = vessel.resources_in_decouple_stage(currStage, False)
    return currStage


conn = krpc.connect(name="krpc connected")    #connect to krpc server
vessel = conn.space_center.active_vessel      #connect to active vessel
print("Current Vessel: ")
print(vessel.name)                            #print current vessel info
print("Enter Y to Launch Rocket")

userInput = ""
currStage = vessel.control.current_stage - 2
currResources = vessel.resources_in_decouple_stage(currStage, False)
print(currResources.amount("SolidFuel"))
print(currStage)

while userInput != "Y":                       #prompt user to begin launch and wait for them to enter Y
    sleep(0.1)
    userInput = input()

ap = vessel.auto_pilot




init_rocket(ap)
countdown()
stage()
sleep(0.01)
while vessel.flight().mean_altitude <= 1000:          #keep vessel 80 pitch 90 hdg until 1000m
    initial_ascent(ap)

while vessel.flight().mean_altitude <= 9500:         #reach 45 pitch 90 heading at 11000m
    mid_ascent(ap)
    currStage = check_stage(currResources, currStage)



while vessel.flight().mean_altitude <= 38000:
    high_ascent(ap)
    currStage = check_stage(currResources, currStage)

ap.reference_frame = vessel.orbital_reference_frame

while vessel.orbit.apoapsis_altitude <= 85000:
    orbital_injection(ap)
    currStage = check_stage(currResources, currStage)

set_throttle(0)

circAlt = 84000


circularization(ap, circAlt, currResources, currStage)
