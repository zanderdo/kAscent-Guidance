#version 0.01
import krpc
from time import sleep

conn = krpc.connect(name="krpc connected")    #connect to krpc server
vessel = conn.space_center.active_vessel      #connect to active vessel
print("Current Vessel: ")
print(vessel.name)                            #print current vessel info

print("Enter Y to Launch Rocket")

userInput = ""

while userInput != "Y":                       #prompt user to begin launch and wait for them to enter Y
    sleep(0.1)
    userInput = input()

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


