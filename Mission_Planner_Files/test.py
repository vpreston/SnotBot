# Victoria Preston
# Created: January 26, 2015
# SnotBot,Ocean Alliance Project

#Script to test working communications between multicopter and Mission Planner, will launch off the ground x meters, then proceed to land

#Initiate the script, zero all comms channels
print 'Start Script'
for chan in range(1,9):
    print chan
    Script.SendRC(chan,1500,False) #Neutralize everything
    Script.SendRC(3,Script.GetParam('RC3_MIN'),True) #Find the RC minimum for the controller
    Script.Sleep(5000) 

#Include this commented out section if outside and can obtain GPS lock, if not, leave commented out if at benchtop
#while cs.lat == 0:
#   print 'Waiting for GPS' 
#   Script.Sleep(1000) 
#   print 'Got GPS' 

#SendRC(Channel, Command, Sendnow) where SendNow is telling it whether or not to actuallly enact the number you've put in
Script.SendRC(3,1000,False) #This sets the throttle to 0
Script.SendRC(4,2000,True)  #This sets holds the yaw over, to initiate motor arming
cs.messages.Clear() 
Script.WaitFor('ARMING MOTORS',3000) 
Script.SendRC(4,1500,True) #Put yaw back to neutral
print 'Motors Armed!'
Script.SendRC(3,1700,True) #This sets the motors to neutrally spinning

while cs.alt < 1: #Would probably want to change this to LiDAR measures in future
    #Get to altitude
    print 'Flying'
    Script.Sleep(50)  # Take measurements every 50ms
    Script.SendRC(5,1500,True) # mode - stabilize     
    Script.SendRC(1,2000,False) # roll    
    Script.SendRC(3,1400,True) # throttle 

while cs.alt > 0.3:
    print 'Lowering'
    Script.Sleep(500) #Take a moment to stabilize
    Script.SendRC(3,1300,True) #set throttle lower

while cs.alt > 0.1: 
    #Land
    print 'Landing'
    Script.Sleep(3000) #Needs to be a multiple of the WaitFor command
    Script.SendRC(3,1000,False) #Set throttle to 0
    Script.SendRC(4,1000,True) #Disarm motors by putting yaw all the way over
    Script.WaitFor('DISARMING MOTORS', 3000)
    Script.SendRC(4,1500,True) #Reset the system

print 'Test Complete'

