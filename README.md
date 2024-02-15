#Energy Recovery Ventilation (ERV) / Heat Recovery Ventilation (HRV) Control via Python

DISCLAIMER: This script does not replace the VAUTOW or VTTOUCHW control devices. One of them is still required to be connected to the ERV/HRV device and can be used along with these scripts.

Script Usage:


Hardware:


Goals:
Due to heavy smoke from wildfires in 2023, I wanted a way to automatically turn off the ERV (to avoid sucking the smoke into the house) if the EPA Air Quality Index (AQI) was too high. I contacted the ERV vendor support and they recommended sending a 12V DC (high) signal to the OVR wire on the ERV. This would "Override" the ERV and run it at Maximum speed to clear the smoke out of the house... ?!?

I realized this would be a fun project to learn how to view digital signals using a cheap Logic Analyzer. Even if I didn't know what the controls were saying to the ERV, I should be able to isolate which RS485 bytes correspond with which button presses, and try sending those same bytes in Python.


Thanks:


