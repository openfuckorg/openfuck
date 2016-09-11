OPENFUCK README



Frame 
A frame was constructed from aluminium extrusion. See demo video and parts list to figure out how to put together one for yourself. 




Air Handling
An Air Compressor (>1HP) compresses air which is then filtered and regulated and regulated to ~50PSI before being fed into the solenoid explained below. It is preferable to run the robot at as high a pressure as possible while ensuring that the compressor is able to pump sufficient air to keep the pressure constant while running at full speed (Run the robot at full speed and crank up the pressure until the compressor is no longer able to keep up, then dial back slightly). We are easily able to operate up to 100PSI with a powerful enough compressor. Bare in mind this means the piston is capable of producing *SIGNIFICANT* amounts of force at *EXTREMELY HIGH* speeds (this makes for some yummy fucking but is rather dangerous ;)

Pneumatic Pathway
Air compressor ->Regular -> Solenoid -> Front Piston Chamber -> Speed Control Valve -> Exhaust
                              |-------> Rear Piston CHamber  -> Speed Control Valve -> Exhaust  



Embedded Electronics

Flash each of the following files onto an Arduino compatible board. 

Arduino/Moses 
A nieve controller that controls the forward/backward solenoid. 
A pair of avalanche rated N channel MOSFETS (with a zener + rectifier diodes to control the negative voltage spike while dissipating it as quickly as possible) is used to drive a 5 port, 3 position , double acting pneumatic solenoid. 

We energize the forward coil (while de-energizing the backward coil) to move accordingly. 

We drive the solenoid with a 12V power supply (the solenoid we selected is pretty power hungry, please use an appropriately sized power supply ) 



Arduino/stepper_command_test 
Controls the forward and backward speed valves via a pair of AMIS 30543 stepper drivers connected to a pair of CLIPPARD SCPV speed control valves. We use accelstepper to accelerate and decelerate the stepper motors. 

Suggest powering the stepper drivers from as high a voltage source as they will take (30V) or as close as you can get to it. This enables use to move the valves quickly for obvious benefits.

Hookup : 

-> Connect each of the arduinos via USB to your control computer. 



Control Computer

A Raspberry PI is used as the control computer for this device. We recommend the Raspberry Pi 3.  We use Raspbian + Python to run the control "backend". The front end consists of either a TKINTER local app or a Websockets based web app.

1) Actuator Script

Piston/Actuator.py

This file actually runs the machine. It receives commands via the /tmp/stream io file (yes file based io is ugly - sorry :( ) and issues the corresponding commands via serial to the embedded electronics

2) User Interface Scripts

The user interface is provided either via TKINTER or a Web App. 
Both of these work great on Tablets and (larger screened) smartphones

Description of functions 
1) OFF/ON Switch - Obviously the Master Off On Switch
2) Sliders
    A) Max Depth - The maximum depth the piston will fuck (end stop)
    B) Stroke Length - How long the stroke will be (how far back from maximum it will pull back)
    C) Max and Min Delay - How long the piston will wait at its maximum extension (inside you) and             minimum extension (pulled back/out)
    D) Min/Max speed - Speed controls mode dependent.
    E) Speed Step/Ramp Size - How fast the speed crossing/speed ramp (fast slow) modes will ramp
3) Move (zero,min,max) - tells the piston to go to zero, its minimum extension or its maximum extension
4) Modes
    A) Go between -> goes forward and backward between, forward speed is max speed , backward speed is         min speed
    B) Speed Crossing -> Starts by fucking in quickly, pulling out slowly , gradually fucks more slowly        and pulls out faster and vice versa. Min speed and max speed specify the maximum and minimum            speeds that will be achieved and step size controls the step
    C) Speed Ramp/ Fast Slow -> starts by fucking in and out slowly , gradually increasing speed and           vice versa. Min speed and max speed specify the maximum and minimum speeds that will be achieved        and step size controls the step size.
    D) Slapper - In quickly , out slowly
    E) Threesome - Complex movement profile, read code to figure out what it does. 

Piston/tkinter_local_interface.py

Local interface based on TKINTER

Piston/web_interface.py

Web interface based on Websockets/Flask web app and jquery/javascript website

Running the robot 

1) Start a front end 
    A) Launch tkinter_local_interface.py in a terminal window
    
    B) Launch web_interface.py and navigate to http://localhost:5000 in a browser
        (obviously you can also expose this on the internet as a website - proceed with caution)
        
2) Start back end - launch actuator.py

3) CHECK EVERYTHING AGAIN

4)Profit and Orgasms ! 

Suggested Mode of Operation)

1) Set the Max Depth to somewhere in the middle . Use "Go Max" to command the piston to that location. 
2) Insert the dildo/fleshlight/whatever
3) Set "Stroke Length" Fairly short (but not the shortest - it gets a bit jittery at low speeds and extremely short strokes, you will see what happens, if its behaving weirdly just increase the stroke length a bit)
4) Set the speeds LOW
5) Turn on the robot
6) Adjust as desired. 

REMEMBER : IT DOESNT KNOW WHEN YOU HAVE CUM. IT WILL NOT STOP. IT WILL NOT GET TIRED.EVER. IF YOU WANT IT TO STOP YOU HAVE TO TELL IT TO STOP

CAUTION : IF YOU ARE THE KIND OF PERSON WHO GETS FUCKED SO DEEP INTO HEADSPACE THAT YOU MAY NOT BE ABLE TO TURN THE ROBOT OFF OR STOP - FOR FUCKS SAKE HAVE SOMEBODY NEARBY TO HELP!!!!! 

    








