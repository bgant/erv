'''
This is a MicroPython script, running on an ESP32 device,
connected to a RS232-to-RS485 device, daisy-chained to the D+, D-, 
and GND wires on a VTTOUCHW ERV wall control panel.

Module import usage in script:
  from vttouchw import VTTOUCHW
  erv = VTTOUCHW()
  erv.commands()
  erv.smart()
  erv.standby()
  erv.state
  erv.status
  help(erv)
'''

from machine import UART
from time import sleep_ms

class VTTOUCHW:
    def __init__(self):
        self.attempts = 11
        self.command_list = ('standby','smart','away','min','med','max','recircmin','recircmed','recircmax')
        self.Rx1 = b'\x01\x12\x10\x01\x05\x41\x08\x20\x00\x20\x4f\x04'  # Same ERV response for all control commands
        self.buffer = bytearray(400)
        self.status = None
        self.state = None

        # UART Configuration 
        self.rx = 8
        self.tx = 9
        self.uart = UART(1, 38400)
        self.uart.init(38400, bits=8, parity=None, stop=1, rx=self.rx, tx=self.tx)

    def reset(self):
        '''
        Re-initialize RS485 Communication
        '''
        self.uart = UART(1, 38400)
        self.uart.init(38400, bits=8, parity=None, stop=1, rx=self.rx, tx=self.tx) 

    def commands(self):
        '''
        Print list of valid ERV/HRV control commands.
        '''
        self._command_string = ' | '.join(map(str,self.command_list))
        return print(f'Controls: {self._command_string}')

    def send_frames(self):
        '''
        Send command frames to the ERV/HRV over the RS485 wires.
        '''
        # May need a few attempts to change the control state...
        # pySerial RS485 support WARNING: This may work unreliably on some serial
        # ports (control signals not synchronized or delayed compared to data). Using
        # delays may be unreliable (varying times, larger than expected) as the OS
        # may not support very fine grained delays.
        self.status = ''
        for i in range(self.attempts):
            self.status += '.'  # Each dot represents one attempt in the while loop
            print('.', end='')
            self.sent = self.uart.write(self.Tx1)
            self.uart.readinto(self.buffer)
            if self.Rx1 in self.buffer:
                if i == 0: # Three times I have seen .OK and the ERV mode did not change
                    pass   # Ignore first attemp even if it is successful
                else:
                    self.status += 'OK'
                    print('OK')
                    break
            self.buffer[:] = b'\x00' * len(self.buffer)  # Clear buffer
            sleep_ms(250)
        else:
            self.status += 'FAILED'
            print('FAILED')

    def standby(self):
        '''
        Standby (STB) - Stops ERV ventilation motor and closes internal dampers to outside ducts.
        '''
        self.state = 'standby'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x01\x08\x20\x01\x00\x49\x04'
        self.send_frames()

    def smart(self):
        '''
        Smart (SMT) - Operates automatically based on outdoor temperature and indoor humidity.
        '''
        self.state = 'smart'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x11\x08\x20\x01\x00\x39\x04'
        self.send_frames()

    def min(self):
        '''
        Continuous Minimum - Continuous exchange ventilation at selected speed.
        '''
        self.state = 'min'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x09\x08\x20\x01\x00\x41\x04'
        self.send_frames() 

    def med(self):
        '''
        Continuous Medium - Continuous exchange ventilation at selected speed.
        '''
        self.state = 'med'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x0b\x08\x20\x01\x00\x3f\x04'
        self.send_frames()

    def max(self):
        '''
        Continuous Maximum - Continuous exchange ventilation at selected speed.
        '''
        self.state = 'max'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x0a\x08\x20\x01\x00\x40\x04'
        self.send_frames()

    def recircmin(self):
        '''
        Recirculation Minimum - Closes dampers to outside ducts and recirculates air inside house at MIN speed.
        '''
        self.state = 'recircmin'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x05\x08\x20\x01\x00\x45\x04'
        self.send_frames()

    def recircmed(self):
        '''
        Recirculation Medium - Closes dampers to outside ducts and recirculates air inside house at MED speed.
        '''
        self.state = 'recircmed'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x07\x08\x20\x01\x00\x43\x04'
        self.send_frames()

    def recircmax(self):
        '''
        Recirculation Maximum - Closes dampers to outside ducts and recirculates air inside house at MAX speed.
        '''
        self.state = 'recircmax'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x06\x08\x20\x01\x00\x44\x04'
        self.send_frames()

    def away(self):
        '''
        Away - 10 minutes outside ventilation / 50 minutes off every hour.
        '''
        self.state = 'away'
        self.Tx1 = b'\x01\x10\x12\x01\x09\x40\x00\x20\x01\x0f\x08\x20\x01\x00\x3b\x04'
        self.send_frames() 

