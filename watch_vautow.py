# Requires USB-to-RS485 device connected to D+, D-, and GND

import serial.rs485
import sys
sys.tracebacklimit = 0  # Avoid Traceback error on Ctrl+C exit

PORT = '/dev/ttyUSB0'

try:
    ser=serial.rs485.RS485(port=PORT,baudrate=38400)
    ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=False,rts_level_for_rx=True)

    # Repeating sequences not related to control signals
    # You will still see some kind of timing/counter packet every 10 seconds...
    skip = [
        b'\x01\x10\x11\x01\x01\x04\xd9\x04', b'\x01\x10\x11\x01\x01\x05\xd8\x04',
        b'\x01\x11\x10\x01\x01\x04\xd9\x04', b'\x01\x11\x10\x01\x01\x05\xd8\x04',
        b'\x01\x11\x10\x01\x54\x21\x0f\x50\x04', b'\x01\x11\x10\x01\x03\x41\x07\x50\x43\x04',
        b'\x01\x10\x11\x01\x08\x40\x07\x50\x04\xff\xff\xff\xff\x3f\x04',
        b'\x01\x10\x11\x01\x03\x20\x14\x00\xa7\x04', b'\x01\x11\x10\x01\x03\x41\x00\x50\x4a\x04',
        b'\x01\x10\x11\x01\x04\x40\x00\x50\x00\x4a\x04',
        b'\x01\x10\x11\x01\x1d\x20\x02\x20\x0c\x21\x0a\x22\x0f\x22\x00\x30\x02\x30\x00\x22\x17\x00\x0e\x50\x0f\x50\x0a\x50\x0b\x50\x08\x22\x06\x22\x96\x04']
  
    # Watch frames scroll by...
    while True:
        frame = ser.read_until(b'\x04')  # Packet Footer is x04
        #frame = ser.read_until(expected=b'\x04\x00')[:-1]  # Packet Footer is x04
        if (frame not in skip) and (frame.hex()[0] == '0') and (frame.hex()[1] == '1'):  # Packet Header is x01
            print(frame.hex())

except Exception or KeyboardInterrupt:
    ser.close()

