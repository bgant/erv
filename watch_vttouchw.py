# Requires USB-to-RS485 device connected to D+, D-, and GND

import serial.rs485
import sys
sys.tracebacklimit = 0  # Avoid Traceback error on Ctrl+C exit

PORT = '/dev/ttyUSB0'

try:
    ser=serial.rs485.RS485(port=PORT,baudrate=38400)
    ser.rs485_mode = serial.rs485.RS485Settings(rts_level_for_tx=False,rts_level_for_rx=True)

    # Repeating sequences not related to control signals
    # A lot of random frames that change and are not related to control signals
    skip = [
           b'\x01\x10\x12\x01\x01\x04', b'\x01\x12\x10\x01\x01\x05\xd7\x04',
           b'\x01\x12\x10\x01\x01\x04', b'\x01\x10\x12\x01\x01\x05\xd7\x04',
           b'\x01\x12\x10\x01\x23\x21\x04', b'\x01\x10\x12\x01\x0b\x20\x04',
           b'\x01\x10\x12\x01\x0b\x20\x08\x30\x09\x30\x19\x50\x20\x50\x21\x50\xf7\x04',
           b'\x01\x12\x10\x01\x1b\x21\x21\x50\x01\x01\x20\x50\x01\x01\x19\x50\x01\x00\x09\x30\x04',
           b'\x01\x12\x10\x01\x14\x21\x09\x50\x04', 'b\x01\x10\x12\x01\x05\x20\x00\x30\x02\x30\x56\x04',
           b'\x01\x10\x12\x01\x0b\x20\x02\x22\x03\x22\x0a\x22\x0c\x22\x0e\x22\xdf\x04', b'\x01\x12\x10\x01\x1e\x21\x0c\x22\x04',
           b'\x01\x10\x12\x01\x09\x20\x0c\x21\x0d\x21\x08\x50\x09\x50\xa8\x04', 'b\x01\x10\x12\x01\x05\x20\x00\x30\x02\x30\x56\x04',
           b'\x01\x12\x10\x01\x09\x21\x02\x30\x01\x01\x00\x30\x01\x00\x4e\x04',
           b'\x01\x10\x12\x01\x07\x20\x12\x50\x13\x50\x14\x50\x8d\x04',
           b'\x01\x12\x10\x01\x0d\x21\x14\x50\x01\x00\x13\x50\x01\x01\x12\x50\x01\x02\x80\x04',
           b'\x01\x10\x12\x01\x09\x20\x12\x00\x1a\x00\x01\xe0\x0a\xf0\xad\x04',
           b'\x01\x10\x12\x01\x05\x20\x00\x30\x02\x30\x56\x04',
           b'\x01\x12\x10\x01\x15\x21\x10\x22\x01\x00\x0f\x22\x01\x00\x06\x21\x01\x01\x05\x21\x01\x01\x04',
           b'\x01\x10\x12\x01\x0f\x20\x00\x20\x02\x20\x06\x20\x07\x20\x08\x20\x03\x30\x04',
           b'\x01\x10\x12\x01\x0f\x40\x04',
           b'\x01\x10\x12\x01\x0f\x20\x00\x20\x02\x20\x06\x20\x07\x20\x08\x20\x03\x30\x04',
           b'\x01\x12\x10\x01\x03\x41\x00\x50\x49\x04', b'\x01\x10\x12\x01\x04',
           b'\x01\x12\x10\x01\x08\x21\x14\x00\x04',
           b'\x01\x12\x10\x01\x05\x41\x05\x50\x04', b'\x01\x10\x12\x01\x03\x20\x14\x00\xa6\x04',
           b'\x01\x12\x10\x01\x91\x21\x0a\xf0\x78\x01\x00\x00\x00\xa8\x16\x1f\x0a\x0e\x8b\x1f\x0a\x01\x00\x00\x00\x01\x13\x60\x3e\x67\x87\x60\x3e\x32\x00\x00\x00\x37\xdb\x4b\x0f\xe2\x46\x60\x0f\x32\x00\x00\x00\x19\xb3\x18\x0a\x2e\x58\x3a\x0a\x32\x00\x00\x00\x9e\xe9\xbc\x09\x30\xfa\xbc\x09\x32\x00\x00\x00\x71\xab\xb9\x09\xe5\x12\xbb\x09\x32\x00\x00\x00\x5e\x74\xb6\x09\xcc\x0e\xb9\x09\x32\x00\x00\x00\x8b\xc5\x04']
  
    # Watch frames scroll by...
    while True:
        frame = ser.read_until(b'\x04')  # Frame Footer is usually x04
        if (frame not in skip) and (frame.hex()[0] == '0') and (frame.hex()[1] == '1'):  # Frame Header is x01
            print(frame.hex())

except Exception or KeyboardInterrupt:
    ser.close()

