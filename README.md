Micropython driver for the TTY6955/TTY6945 capacitive touch key sensor IC
Copyright 2020, Thomas TEMPE

The TTY6945 and TTY6955 are respectively 13- and 16-pad capacitive touche sensor ICs produced by Tontec. 
They are able to read up to 3 sliders (or wheels), giving a resolution of 8 bits. Pins not used for sliders
can be used for binary touch buttons.

This chip features software-enabled auto-calibration, auto-threshold, and are used through i2c. 
They are apparently widely available in China, but I could unfortunately not find an English-language datasheet.

These are two IC apparently have the same features and protocole, and differ only by the number of pads they can drive.
