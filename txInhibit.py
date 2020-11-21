# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:43:12 2020

@author: philippe F5OWL

# TS590 auto transmit inhibit and  auto power and ATU setting by subband
"""
import serial
import time
import sys

port = '/dev/ts590RS232' # change for your current com port
baud = 9600 # adjust speed to your trx speed 
timeout=0
delayCommand= 0.2 # time to wait for answer 
updateDelay = 0.5 # delay between updates
# change to match your needs and your local regulation
# set power to 0 to inhibit tx inside ham band
#band data : (fmin,fmax,pwr ant1,pwr ant2,autoTune ant1, autoTune ant2) 
bandData=( 
    (1810.0,1850.0,0,0,'OFF','OFF')  , (3500.0,3800.0,0,100,'OFF','OFF'),
    (5351.5,5366.5,0,15,'OFF','ON') , (10100.0,10150.0,0,100,'OFF','ON'),
    (7000.0,7200.0,0,100,'OFF','OFF'),(14000.0,14350.0,100,100,'ON','ON'),
    (18068.0,18168.0,100,100,'OFF','ON'),(21000.0,21170.0,100,100,'OFF','OFF'),
    (21170.0,21450.0,100,100,'ON','ON'),(24890.0,24990.0,100,100,'OFF','ON'),
    (28000.0,28180.0,100,100,'OFF','ON'),(28180.0,29700.0,100,100,'ON','OFF'),
    (50000.0,52000.0,0,100,'OFF','ON') 
)


# indexes for bandData
FMIN=0
FMAX=1
PWR_ANT1=2
PWR_ANT2=3
AUTO_ANT1=4
AUTO_ANT2=5

curentTxPermited = True # default status Tx is allowed 
currentPwr = 0
currentATtune = 'OFF' 
lastBand=-1 

# return band index if freq is inside ham band ans -1 if out of band
def getCurrentBand(f):
    for i,band in enumerate(bandData) :
        if f>=band[FMIN] and f<=band[FMAX]:
            return i
    return -1


# send a command via serial port and return TRX response
def sendCommand(ser,command):
     command = bytes(command,'ASCII')
     ser.write(command)
     time.sleep(delayCommand)
     b = ser.read(100)
     s = b.decode()
     s=s[:-1] # remove final char ';'
     return s

# infinite loop : try again in case of communication problem
while 1 :
 try : 
  with serial.Serial(port=port, baudrate=baud, timeout=timeout) as ser:
    # trying to read FA to test communication 
    s=sendCommand(ser,'FA;')
    if s[:2]=='FA' :
        print('Communication test ok ', end='')
        freq = int(s[2:])/1e6
        print('VFO A : ',freq , 'Mhz')
    else :
        print('Unable to communicate witch rig : check cable and port config')
        sys.exit(-1)
    s=sendCommand(ser,'FV;')
    print('Firmware version:',s)
    
    sendCommand(ser,'EX06000000;') # tx allowed by default
    while 1 :
        # read Tx VFO :
        s=sendCommand(ser,'FT;')
        print(s)
        if s=='FT2':
            # as I use memories for beacons and utilities 
            # tx is inhibited in memory mode
            # comment it out if you want tx in memory mode
            print('memory mode : tx not allowed')
            sendCommand(ser,'EX06000001;')
            curentTxPermited= False
            time.sleep(updateDelay)
            continue
        # read current Tx VFO frequency
        if s=='FT0':
            sf=sendCommand(ser,'FA;')
        else :
            sf=sendCommand(ser,'FB;')
        print(s)
        sf=sf[2:] # suppress FA or FB
        f = float(sf)/1000 # current tx frequency in kHz
        band = getCurrentBand(f)
        print('Band index',band)
        
        if band ==-1 :
            if curentTxPermited==True :
                print('Outside ham band :set tx inhibited')
                sendCommand(ser,'EX06000001;')
                curentTxPermited= False
            continue
        
        if lastBand != band :
            # update AT tune status
            s=sendCommand(ser,'AC;')
            if s[3]=='0' :
                currentATtune = 'OFF'
            else :
                 currentATtune = 'ON'
            lastBand=band
            
        # read current ant
        s=sendCommand(ser,'AN;') #ANP1P2P3; P1=TX ant
        print('AN=',s)
        if s[2]=='1':
            currentANT=1
            pwrIndex=PWR_ANT1
            aTtuneIndex = AUTO_ANT1
        else :
            currentANT=2
            pwrIndex=PWR_ANT2
            aTtuneIndex = AUTO_ANT2
        print('data for band',band,'is',bandData[band])
        # read power for the selected ANT for the selected band
        bandPwr = bandData[band][pwrIndex]
        print('band power',bandPwr,'for ANT',currentANT)
        if currentPwr != bandPwr :
            print('change power to',bandPwr,'W')
            bandPwrStr = str(int(bandPwr))
            if bandPwr < 10 :
                bandPwrStr = '00'+bandPwrStr
            elif bandPwr < 100 :
                bandPwrStr = '0'+bandPwrStr
            print(bandPwrStr)
            s=sendCommand(ser,'PC'+bandPwrStr+';')
            currentPwr=bandPwr
            if bandPwr==0 :
                curentTxPermited=False
                print('pwr set to 0 :set tx inhibited')
                sendCommand(ser,'EX06000001;')
        if curentTxPermited==False :
            if bandPwr != 0 :
                print('Entering ham band :set tx permitted')
                sendCommand(ser,'EX06000000;')
                curentTxPermited= True
        #read auto tune status for the selected ANT for the selected band
        atTune = bandData[band][aTtuneIndex]
        print('AT tune for antenna',currentANT ,'on that band is ',atTune)
        if atTune!=currentATtune :
            print('set AT tune to',atTune)
            if atTune=='OFF' :
                sendCommand(ser,'AC000;')
            else :
                sendCommand(ser,'AC010;')
            currentATtune=atTune
            
        time.sleep(updateDelay)
 except :
    # ugly but simple 
    print('error occured, trying again...')
    time.sleep(4)
    curentTxPermited = True # default status Tx is allowed 
    currentPwr = 0

    
 
        
        
    
    
