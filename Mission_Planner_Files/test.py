#Initiate the script, Zero all comms channels
print 'Start Script'
for chan in range(1,9):
	Script.SendRC(chan,1500,False)
	Script.SendRC(3,Script.GetParam('RC3_MIN'),True)
	Script.Sleep(5000) 

#Include this commented out section if outside and can obtain GPS lock, if not, leave commented out if at benchtop
#while cs.lat == 0:
#	print 'Waiting for GPS' 
#	Script.Sleep(1000) 
#	print 'Got GPS' 
jo = 10 * 13
print jo
#Don't really know the significance of jo...
#SendRC(Channel, Command, Sendnow)
Script.SendRC(3,1000,False) 
Script.SendRC(4,2000,True) 
cs.messages.Clear() 
Script.WaitFor('ARMING MOTORS',30000) 
Script.SendRC(4,1500,True) 
print 'Motors Armed!'
Script.SendRC(3,1700,True) 

while cs.alt < 50:
    #Get to altitude
    Script.Sleep(50) 	
    Script.SendRC(5,2000,True) # acro 	
    Script.SendRC(1,2000,False) # roll  	
    Script.SendRC(3,1370,True) # throttle  	 

while cs.roll > -45: # top half 0 - 180 
    Script.Sleep(5) 

while cs.roll < -45: # -180 - -45  	
    Script.Sleep(5) 	
    Script.SendRC(5,1500,False) # stabilize  	
    Script.SendRC(1,1500,True) # level roll  	
    Script.Sleep(2000) # 2 sec to stabilize  	
    Script.SendRC(3,1300,True) # throttle back to land 	
    thro = 1350 # will descend 	 

while cs.alt > 0.1:
    #Land
    Script.Sleep(300)
    Script.SendRC(3,1000,False) 
    Script.SendRC(4,1000,True) 
    Script.WaitFor('DISARMING MOTORS',30000) 
    Script.SendRC(4,1500,True)

print 'Roll complete'
