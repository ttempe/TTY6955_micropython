# Micropython driver for the TTY6955/TTY6945
# Capacitive touch key sensor IC
# Copyright 2020, Thomas TEMPE
# DWTFYL license.
#
# The two IC apparently have the same features and protocole,
# and differ only by the number of pads they can drive.
# Warning: these chip can drive up to 3 sliders, but can't detect when you touch 2 sliders
# at the same time.

#Calibration instructions from the user manual:
#Step 1: start with CS = 33nF for slider applications and 10nF for key-only applications
#        (bigger is more sensitive)
#Step 2: try the keys out, with normal finger speed, either with a finger or a metal rod.
#        If detection happens before the finger touches the surface, it means sensitivity
#        is set too high. The threshold value needs to be increased.
#        If no detection unless you press hard on the surface, sensitivity is too low. The
#        threshold value needs to be decreased.
#        When testing sliders, you want to maintain detection even in the less sensitive
#        teeth area between pads, where sensitivity will be naturally lower; so be sure to
#        put your finger there to adjust the threshold.
#Step 3: Test the key speed response
#        While trying out the touch keys, if they "don't feel responsive enough", you need
#        to determine if that sensation comes from response time or sensitivity.
#        Hold your finger still for ~1 second to determine whether detection is sufficient.
#        If there is no detection, it means sensitivity is too low. Go back to step 2.
#        If there is detection, it means speed is too low. Move to step 4.
#Step 4: Adjust reaction speed
#        The number of readings before detection (KAT) is set to 4 by default.
#        Try changing it to 3. If that's still not enough, try reducing the CS capacitor value.
#        After changing your capacitor, go back to step 2. Be aware that a smaller capacitor
#        will also be less sensitive.

import errno

class TTY6955:
    def __init__(self, i2c, addr=0x50,
                 slider1_pads=0, slider2_pads=0, slider3_pads=0,
                 single_key_mode=False, power_save_mode=False, dynamic_threshold=True,
                 auto_reset_mode = 0x01, key_acknowledge_times = 4, nb_keys=None):
        """
        Addr = i2c address of the TTY6955 chip
        sliderX_pads = number of pads to be used for each slider. Default is none.
        auto reset time: 0=disabled; 1=15s (default); 2=30s; 3=1min
        key_acknowledge_times = nb of times to detect a touch before reporting it.
        Recommended 3 or 4
        By default, nb_keys will be set to the maximum. override it to speed up reading.

        For the other parameters, please refer to the datasheet. Good luck.
        """
        nb_slider_pads = slider1_pads+slider2_pads+slider3_pads
        if nb_slider_pads>16:
            raise InputError("Too many slider pads (16 max)")
        self.i2c = i2c
        self.addr = addr
        self.output = []
        self.nb_sliders = bool(slider1_pads)+bool(slider2_pads)+bool(slider3_pads)
        if None == nb_keys:
            self.nb_keys = 16-nb_slider_pads
        else:
            self.nb_keys = nb_keys
        self.init_seq = [0,0,0,0]
        self.init_seq[0] = ( 0x80 +                      #IICM + CT
                             0x20 * single_key_mode +    #KOM
                             0x10 +                      #AA : changed by set_thersholds() 
                             0x08 * power_save_mode +    #PSM
                             0x04 * dynamic_threshold +  #DT
                             auto_reset_mode             #ART
                             )
        self.init_seq[1] = ( ((self.nb_keys & 0x1F) << 3) +
                             (key_acknowledge_times -1 & 0x7) #KAT
                             )
        self.init_seq[2] =   (slider2_pads << 4) + slider1_pads
        self.init_seq[3] = ( 0 +                         #Key off num
                             slider3_pads
                             )
        self.i2c.writeto(self.addr, bytes(self.init_seq))
        
    def set_custom_thresholds(self, pad, L, M, H):
        """
        Each of L (low), M (Medium) and H (High) is a 4-bit integer
        """
        cust_seq = [
            0xC0 + (pad & 0x0F),
            ((M & 0x0F) << 4) + (L & 0x0F),
            (H & 0x0F)
            ]
        self.i2c.writeto(self.addr, bytes(cust_seq))        

    def set_sleep(self, M, L, H):
        "Set the TPSLP sleep thresholds (Low, Medium, High)"
        cust_seq = [
            0xD0,
            ((M & 0x0F) << 4) + (L & 0x0F),
            (H & 0x0F)
            ]
        self.i2c.writeto(self.addr, bytes(cust_seq))        
                    
    def read(self):
        "call this method to actually read the data from the sensor"
        self.output = list(self.i2c.readfrom(self.addr, 6))
        self.buttons = self.output[1] + (self.output[2]<<8)
        if not(self.output[0] & 0b10000000):
            raise Exception("The touch IC reports invalid calibration.")

    def slider(self, num):
        """
        Takes the slider number as input: 1, 2, or 3
        returns a tuple: (is_pressed, slider value)
        the slider value is an integer between 0 and 255.
        """
        return ((self.output[0]>>(num-1))&1, self.output[num+2])

    def button(self, num):
        """
        returns the state of the button.
        Note: button numbering skips any pads used for sliders.
        Eg: if you declare no sliders, then pin n. 2 (TP4) refers to button 4.
        However, if you declare a 3-pad slider, then the same pin n.2 (TP4) will become button 1.
        Buttons are counted from 0.
        """
        return (self.buttons>>num) & 1

    def output_debug(self):
        """
        Displays the contents of the sensor output in binary display.
        Useful for debugging your board.
        
        Summary:
        * the first bit should be 1; otherwise all you're getting is noise.
        * the 2nd bit is 1 on reset, gets pulled down by any form of configuration
        * the last 3 bits of the 1st octet indicate whether the 3 sliders are being touched
        * the next 2 octets indicate the bit-by-bit status of all touch keys
        * the last 3 octets are the analog reading of the finger position on the 3 sliders
        """
        for c in self.output:
            print("{:08b} ".format(c), end="")
        print()
