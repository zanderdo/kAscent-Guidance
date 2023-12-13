
#version 0.01
import krpc
import math
from time import sleep

tgtApo = 85000
topGravityTurn = 7000
numSeparatrons = 0
timeBeforeApo = 25
actualApoAlt = 0
velAtApo = 0
xVel = 0
gravConst = 6.67 * pow(10, -11)
mKerbin = 5.29 * pow(10, 22)
rKerbin = 600000
timeBurnStartBeforeApo = 0
hasCalced = False




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

def gravity_turn(ap):
    hdg_target = 90
    pitch_target = 80 - (35 * (vessel.flight().mean_altitude / topGravityTurn))
    ap.target_pitch_and_heading(pitch_target, hdg_target)

def high_ascent(ap):
    ap.target_direction = (0,1,0)

def orbital_injection(ap, circAlt):
        ap.target_direction = (0,1,0)
        if (vessel.orbit.time_to_apoapsis > timeBurnStartBeforeApo):
            set_throttle(0)
        elif (abs(vessel.orbit.apoapsis_altitude - vessel.orbit.periapsis_altitude > 1000)):
            set_throttle(100)
        else:
            set_throttle(0)

def calc_burn(hasCalced):
    if not hasCalced:
        actualApoAlt = vessel.orbit.apoapsis
        calcSurfRefFrame = vessel.orbit.body.reference_frame
        apoRadius = vessel.orbit.apoapsis_altitude + rKerbin
        proAngle = math.asin(vessel.flight(calcSurfRefFrame).vertical_speed / vessel.orbit.speed)
        xVel = vessel.orbit.speed * math.cos(proAngle)
        velAtApo = xVel
        mShip = vessel.mass

        forceKerbin = gravConst * ((mShip * mKerbin) / pow(apoRadius, 2))
        accelerationAtApo = forceKerbin / mShip
        vOrbit = accelerationAtApo * apoRadius

        totalThrust = 0
        activeEngines = [e for e in vessel.parts.engines if e.active and e.has_fuel]
        totalThrust = sum(engine.max_thrust for engine in activeEngines)
        initAcceleration = totalThrust / vessel.mass
        print("total thrust: ")
        print(totalThrust)
        print("mass: ")
        print(vessel.mass)
        print("init acceleration: ")
        print(initAcceleration)
        desiredChange = vOrbit - velAtApo
        approxTimeBurn = desiredChange / initAcceleration
        timeBurnStartBeforeApo = approxTimeBurn / 2
        hasCalced = True



def check_stage(currResources, currStage):
    if (currResources.has_resource("SolidFuel")):
        if (currResources.amount("SolidFuel") <= 1 + (numSeparatrons * 8)):
            stage()
            currStage = currStage - 1
            currResources = vessel.resources_in_decouple_stage(currStage, False)
    if (currResources.has_resource("LiquidFuel")):
        if (currResources.amount("LiquidFuel") <= 1):
            stage()
            currStage = currStage - 1
            currResources = vessel.resources_in_decouple_stage(currStage, False)
    return currStage


conn = krpc.connect(name="krpc connected")    #connect to krpc server
vessel = conn.space_center.active_vessel      #connect to active vessel
print("Current Vessel: ")
print(vessel.name)                            #print current vessel info
print("Please enter the number of separatrons on the rocket: ")
userInput = input()
numSeparatrons = int(userInput)
print(numSeparatrons)
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

while 1:
    if (vessel.flight().mean_altitude <= 500):
        initial_ascent(ap)
    elif (vessel.flight().mean_altitude <= topGravityTurn and vessel.flight().mean_altitude >500):
        gravity_turn(ap)
    elif (vessel.orbit.apoapsis_altitude <= tgtApo and vessel.flight().mean_altitude > topGravityTurn):
        if (ap.reference_frame != vessel.orbital_reference_frame):
            ap.reference_frame = vessel.orbital_reference_frame
        high_ascent(ap)
    elif (vessel.orbit.apoapsis_altitude > 70000):
        if (not hasCalced and vessel.flight(vessel.surface_reference_frame).mean_altitude > 70000):
            calc_burn(hasCalced)
            hasCalced = True
        if (ap.reference_frame != vessel.orbital_reference_frame):
            ap.reference_frame = vessel.orbital_reference_frame
        orbital_injection(ap, tgtApo)
    currStage = check_stage(currResources, currStage)
    currResources = currResources = vessel.resources_in_decouple_stage(currStage, False)
    sleep(0.01)
