'''
This Python3 script was written for Linux, connected
to a USB-to-RS485 device, daisy-chained to the D+, D-, 
and GND wires on a VTTOUCHW ERV/HRV control panel.

Command-line Usage:
  python3 vttouchw.py /dev/ttyUSB0 standby

Module import usage in script:
  from vttouchw import VTTOUCHW
  erv = VTTOUCHW('/dev/ttyUSB0')
  erv.commands()
  erv.smart()
  erv.standby()
  erv.state
  erv.status
  help(erv)
'''

import serial.rs485
from time import sleep

class VTTOUCHW:
    def __init__(self,port=None):
        self.port = port
        self.baudrate = 38400
        self.attempts = 8
        self.timeout = 0.1
        self.delay_before_tx = 0.005
        self.command_list = ['standby','smart','away','min','med','max','recircmin','recircmed','recircmax']
        self.Rx = b'\x01\x12\x10\x01\x05\x41\x08\x20\x00\x20\x4f\x04'

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
            self.ser.write(self.Tx)
            self.resp = self.ser.read_until(expected=self.Rx)  # Confirm Success with ERV Response Frame
            self.status += '.'  # Each dot represents one attempt in the while loop 
            if self.Rx.hex() in self.resp.hex():
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
        Standby (STB) - Stops ERV ventilation motor and closes internal dampers to outside ducts
        '''
        self.state = 'standby'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x01\x08\x20\x01\x00\x49\x04'
        self.send_frames()

    def smart(self):
        '''
        Smart (SMT) - Operates according to outdoor temperature and indoor humidity
        '''
        self.state = 'smart'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x11\x08\x20\x01\x00\x39\x04'
        self.send_frames()

    def min(self):
        '''
        Continuous Minimum - Continuous exchange ventilation at selected speed
        '''
        self.state = 'min'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x09\x08\x20\x01\x00\x41\x04'
        self.send_frames() 

    def med(self):
        '''
        Continuous Medium - Continuous exchange ventilation at selected speed
        '''
        self.state = 'med'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x0b\x08\x20\x01\x00\x3f\x04'
        self.send_frames()

    def max(self):
        '''
        Continuous Maximum - Continuous exchange ventilation at selected speed
        '''
        self.state = 'max'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x0a\x08\x20\x01\x00\x40\x04'
        self.send_frames()

    def recircmin(self):
        '''
        Recirculation Minimum - Closes dampers to outside ducts and recirculates air inside the house at MIN speed        
        '''
        self.state = 'recircmin'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x05\x08\x20\x01\x00\x45\x04'
        self.send_frames()

    def recircmed(self):
        '''
        Recirculation Medium - Closes dampers to outside ducts and recirculates air inside the house at MED speed
        '''
        self.state = 'recircmed'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x07\x08\x20\x01\x00\x43\x04'
        self.send_frames()

    def recircmax(self):
        '''
        Recirculation Maximum - Closes dampers to outside ducts and recirculates air inside the house at MAX speed
        '''
        self.state = 'recircmax'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x06\x08\x20\x01\x00\x44\x04'
        self.send_frames()

    def away(self):
        '''
        Away - 10 minutes outside ventilation / 50 minutes off every hour
        '''
        self.state = 'away'
        self.Tx = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x0f\x08\x20\x01\x00\x3b\x04'
        self.send_frames() 


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:  # No commands given
        erv = VTTOUCHW()
        print('Example command-line: python3 vttouchw.py /dev/ttyUSB0 standby')
        erv.commands()
    else:
        try:
            erv = VTTOUCHW(sys.argv[1])
            func = getattr(erv, sys.argv[2].lower())
            func()  # calls erv.command()
        except AttributeError as e:
            print(f'{sys.argv[2]} command not found')
            #print(e)
            erv.commands()

