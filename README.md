# autoTxInhibit
This python script was first made to inhibit Tx of a full tx **ts590** when the transmit frequency is outside ham bands to avoid to transmit illegaly inadvertently.

Then the possiblity was added to automaticaly set Tx power and ATU status by band or band segment for each antenna. Changes are made when entering band segment. You can modify power and ATU status, they will be restored when returning to that band.

As the USB CAT port is generaly used by other software (hamlib), you can use the second RS232 CAT port on the TS590 (via USB to RS232 adapter if necessary) for this software.

Tested only in ubuntu by should work in most OSes.
Should be easly adapted for other transceivers.

# Configuration
Set port and baud variables to match your port and speed
Set bandData according to your preferences and local regulation.
bandData is a list of tuples :

(fmin,fmax,pwr ant1, pwr ant2, ATU ant1, ATU ant2)

fmin : min frequency of that band segment in kHz
fmax : max frequency of that band segment in kHz
pwr ant1 : power setting when ant1 is selected. 0 to inhibit Tx.
pwr ant2 : power setting when ant2 is selected.
ATU ant1 : 'ON' if used , 'OFF' if not used on that band
ATU ant2 : 'ON' if used , 'OFF' if not used on that band


Example :

 Tx not allowed on 160m, full power on all band except 15W on 60m,
 Tx not allowed on ant1 on band below 20m and on 6m,
 ATU is not used on ANT2 on 80m and 40m and 15m,
 Ant1 needs ATU on 15m above 21170 and on 10m above 28180.

   
    bandData=( 
    (1810.0,1850.0,0,0,'OFF','OFF')  , (3500.0,3800.0,0,100,'OFF','OFF'),
    (5351.5,5366.5,0,15,'OFF','ON') , (10100.0,10150.0,0,100,'OFF','ON'),
    (7000.0,7200.0,0,100,'OFF','OFF'),(14000.0,14350.0,100,100,'ON','ON'),
    (18068.0,18168.0,100,100,'OFF','ON'),(21000.0,21170.0,100,100,'OFF','OFF'),
    (21170.0,21450.0,100,100,'ON','ON'),(24890.0,24990.0,100,100,'OFF','ON'),
    (28000.0,28180.0,100,100,'OFF','ON'),(28180.0,29700.0,100,100,'ON','OFF'),
    (50000.0,52000.0,0,100,'OFF','ON') 
)

# UDEV rules (linux only)

An udev rules is also provided to give a constant name to your TS590 ports :

 1. use `lsusb` or `dmesg` command to find *vendor-id* and *product-id* of your ts590 and RS232/USB adapter.
 2. use `dmesg` command to find serial numbers.
 3. modify the file 99-kenwood-ts590.rules to match what you have found and names if you want.
 4. copy it on ** `/etc/udev/rules/`**
 5. restart udev : `sudo udevadm control --reload `
 6. two new port should show up :   ls /dev/ts* -l  
           /dev/ts590 -> ttyUSBx  
           /dev/ts590RS232 -> ttyUSBy

# Licence 
This project is licensed under the GPL licence This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.





