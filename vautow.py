'''
This Python3 script was written for Linux, connected
to a USB-to-RS485 device, daisy-chained to the D+, D-, 
and GND wires on a VAUTOW ERV/HRV control panel.

Command-line Usage:
  python3 vautow.py /dev/ttyUSB0 standby

Module import usage in script:
  from vautow import VAUTOW
  erv = VAUTOW('/dev/ttyUSB0')
  erv.commands()
  erv.auto()
  erv.standby()
  erv.state
  erv.status
  help(erv)
'''

import serial.rs485
from time import sleep

class VAUTOW:
    def __init__(self,port=None):
        self.port = port
        self.baudrate = 38400
        self.attempts = 7
        self.timeout = 0.1
        self.delay_before_tx = 0.005
        self.command_list = ['standby','auto','turbo','recirc','int','min','med','max']

    def commands(self):
        '''
        Print list of valid ERV/HRV control commands.
        '''
        self._command_string = ' | '.join(map(str,self.command_list))
        return print(f'ERV Control Options: {self._command_string}')

    def send_frames(self):
        '''
        Send command frames to the ERV/HRV over the RS485 wires.
        '''
        try:
            self.ser=serial.rs485.RS485(port=self.port,baudrate=self.baudrate,timeout=self.timeout)
            self.ser.rs485_mode = serial.rs485.RS485Settings(
                rts_level_for_tx=False,
                rts_level_for_rx=True,
                delay_before_tx=self.delay_before_tx)
        except:
            return print(f'{self.port} serial port not found')

        # May need a few attempts to change the control state...
        # pySerial RS485 support WARNING: This may work unreliably on some serial
        # ports (control signals not synchronized or delayed compared to data). Using
        # delays may be unreliable (varying times, larger than expected) as the OS
        # may not support very fine grained delays.
        self.count = 0
        self.status = ''
        while self.count <= self.attempts:
            self.ser.write(self.Tx1)  # Send 1st Data Frame
            self.ser.write(self.Tx2)  # Send 2nd Data Frame
            self.ser.write(self.Tx3)  # Send 3rd Data Frame
            self.resp = self.ser.read_until(expected=self.Rx3)  # Confirm Success with 3rd Data Frame ERV Response
            self.status += '.'  # Each dot represents one attempt in the while loop
            if self.Rx3.hex() in self.resp.hex():
                self.status += 'OK'
                self.ser.close()
                return print(f'{self.status}')
            else:
                self.count += 1
                sleep(0.25)
        else:
            self.ser.close()
            self.status += 'FAILED'
            return print(f'{self.status}')

    def standby(self):
        '''
        Standby (STB) - Stops ERV ventilation motor and closes internal dampers to outside ducts.
        '''
        self.state = 'standby'
        self.Tx1 = b'\x01\x10\x11\x01\x04\x40\x03\x20\x00\x77\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x01\x77\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x01\x95\x04'
        self.send_frames()

    def auto(self):
        '''
        Auto (AUT) - Operates according to outdoor temperature:
                 < -13°F = 10 min/hr
           -13°F to 19°F = 20 min/hr
            19°F to 50°F = <not specified / maybe 30 min/hr>
            50°F to 77°F = MIN speed
            77°F to 82°F = 30 min/hr
            82°F to 91°F = 20 min/hr
                  > 91°F = 10 min/hr
        '''
        self.state = 'auto'
        self.Tx1 = b'\x01\x10\x11\x01\x04\x40\x03\x20\x00\x77\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x10\x68\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x10\x86\x04'
        self.send_frames()

    def turbo(self):
        '''
        Turbo (TUR) - Four hours of ventilation at MAX speed, then returns to previous setting.
        '''
        self.state = 'turbo' 
        self.Tx1 = b'\x01\x10\x11\x01\x08\x40\x00\x22\x04\x40\x38\x00\x00\xf8\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x0c\x6c\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x0c\x8a\x04'
        self.send_frames()

    def recirc(self):
        '''
        Recirculation (REC) - Closes dampers to outside ducts and recirculates air inside the house at MAX speed.
        '''
        self.state = 'recirc'
        self.Tx1 = b'\x01\x10\x11\x01\x04\x40\x03\x20\x00\x77\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x06\x72\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x06\x90\x04'
        self.send_frames()

    def int(self):
        '''
        Intermittent (INT) - Within a one hour period, operates at MIN speed for 20 minutes (20 min/hr).
        '''
        self.state = 'int'
        self.Tx1 = b'\x01\x10\x11\x01\x0b\x40\x03\x20\x00\x02\x22\x04\xb0\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x08\x70\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x08\x8e\x04'
        self.send_frames()

    def min(self):
        '''
        Minimum (MIN) - Continuous exchange ventilation at selected speed.
        '''
        self.state = 'min'
        self.Tx1 = b'\x01\x10\x11\x01\x04\x40\x03\x20\x00\x77\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x09\x6f\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x09\x8d\x04'
        self.send_frames()

    def med(self):
        '''
        Medium (MED) - Continuous exchange ventilation at selected speed.
        '''
        self.state = 'med'
        self.Tx1 = b'\x01\x10\x11\x01\x12\x40\x03\x20\x00\x08\x22\x04\x9a\x99\xe3\x42\x06\x22\x04\x9a\x99\xe3\x42\x5f\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x0b\x6d\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x0b\x8b\x04'
        self.send_frames()

    def max(self):
        '''
        Maximum (MAX) - Continuous exchange ventilation at selected speed.
        '''
        self.state = 'max'
        self.Tx1 = b'\x01\x10\x11\x01\x04\x40\x03\x20\x00\x77\x04'
        self.Tx2 = b'\x01\x10\x11\x01\x05\x40\x00\x20\x01\x0a\x6e\x04'
        self.Tx3 = b'\x01\x10\x11\x01\x03\x20\x01\x20\x9a\x04'
        self.Rx3 = b'\x01\x11\x10\x01\x05\x21\x01\x20\x01\x0a\x8c\x04'
        self.send_frames()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:  # No commands given
        erv = VAUTOW()
        print('Example command-line: python3 vautow.py /dev/ttyUSB0 standby')
        erv.commands()
    else:
        try:
            erv = VAUTOW(sys.argv[1])
            func = getattr(erv, sys.argv[2].lower())
            func()  # calls erv.command()
        except AttributeError:
            print(f'{sys.argv[2]} command not found')
            erv.commands()
