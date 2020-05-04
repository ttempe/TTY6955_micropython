Micropython driver for the TTY6955/TTY6945 capacitive touch key sensor IC
Copyright 2020, Thomas TEMPE

The TTY6945 and TTY6955 are respectively 13- and 16-pad capacitive touche sensor ICs produced by Tontec. 
They are able to read up to 3 sliders (or wheels), giving a resolution of 8 bits. Pins not used for sliders can be used for binary touch buttons.
The IC requires very few external components (decoupling capacitor, measuerement capacitor, and optional 1k resistors between the pads and the chip). Its supply 
voltage is 2.5 to 5.5V. Its rated power consumption is 1.1mA (wake) to 5.3~10.0 uA 
(sleep mode.)

This chip features software-enabled auto-calibration, auto-threshold, and are used through i2c. 
They are apparently widely available in China, but I could unfortunately not find an English-language datasheet. However, part of the Chinese datasheet is written in 
English. I've made a reasonable attempt at covering for the missing critical bits 
here.

These are two IC apparently have the same features and protocole, and differ only by the number of pads they can drive.


Calibration instructions from the user manual:
==============================================

Step 1: start with CS = 33nF for slider applications and 10nF for key-only applications
		(bigger is more sensitive)

Step 2: try the keys out, with normal finger speed, either with a finger or a 
		metal rod.
       If detection happens before the finger touches the surface, it means sensitivity
       is set too high. The threshold value needs to be increased.
       If no detection unless you press hard on the surface, sensitivity is too low. The
       threshold value needs to be decreased.
       When testing sliders, you want to maintain detection even in the less sensitive
       teeth area between pads, where sensitivity will be naturally lower; so be sure to
       put your finger there to adjust the threshold.
	   
Step 3: Test the key speed response
       While trying out the touch keys, if they "don't feel responsive enough", you need
       to determine if that sensation comes from response time or sensitivity.
       Hold your finger still for ~1 second to determine whether detection is sufficient.
       If there is no detection, it means sensitivity is too low. Go back to step 2.
       If there is detection, it means speed is too low. Move to step 4.
	   
Step 4: Adjust reaction speed
       The number of readings before detection (KAT) is set to 4 by default.
       Try changing it to 3. If that's still not enough, try reducing the CS capacitor value.
       After changing your capacitor, go back to step 2. Be aware that a smaller capacitor
       will also be less sensitive.
