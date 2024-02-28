'''
mpremote a0 mip install --target= github:bgant/erv/micropython/vttouchw.py
mpremote a0 mip install --target= github:bgant/micropython/projects/control_erv/main.py
mpremote a0 mip install --target= github:bgant/micropython/modules/wifi.py
mpremote a0 mip install --target= github:bgant/micropython/modules/key_store.py
mpremote a0 mip install --target= github:bgant/micropython/modules/timezone.py
mpremote a0 mip install --target= github:bgant/micropython/modules/AirNowAPI.py
mpremote a0 mip install --target= github:bgant/micropython/modules/OpenWeatherMap.py
mpremote a0 mip install --target= github:bgant/micropython/modules/PMS7003.py
'''

# Initialize Watchdog Timer
from machine import reset, WDT, Timer
wdt = WDT(timeout=600000)  # 10  Minute Hardware Watchdog Timer

# Connect to Wifi and set Clock
from wifi import WIFI
wifi = WIFI()
wifi.connect()

# Import Project Specific Modules
from vttouchw import VTTOUCHW
from OpenWeatherMap import WEATHER
from AirNowAPI import AQI
#from pms7003 import PM7003 
from utime import localtime
from timezone import tz

main_interval = 300000   # Minutes between Timer loops

class PROJECT:
    def __init__(self):
        self.erv = VTTOUCHW()
        self.weather = WEATHER()
        self.PM_EPA = AQI('PM')
        #self.PM_Local = PMS7003()

        # Thresholds
        self.night_start = 20  # ERV  on after 8PM
        self.night_end   =  7  # ERV off after 7AM
        self.too_cold    = 32  # ERV off below 32F
        self.too_hot     = 90  # ERV off above 90F
        self.high_aqi    = 100 # ERV off above 100 PM2.5

    def night(self):
        '''
        Is it night right now?
        '''
        self.night_hours = [h % 24 for h in range(self.night_start,self.night_end+24)]  # 8PM to 7AM
        if localtime(tz())[3] in self.night_hours:
            print('OFF: Nighttime')
            return True
        else:
            print('OK:  Daytime')
            return False

    def outside_too_hot_or_cold(self):
        '''
        Is it too hot or cold outside right now?
        '''
        self.response = self.weather.download('temp')
        if self.response:
            if (self.response < self.too_cold) or (self.response > self.too_hot):
                print(f'OFF: Too hot or cold at {self.response}F')
                return True
            else:
                print(f'OK:  Outside temperature is good at {self.response}F')
                return False
        else:
            print(f'ERROR: API Response is {self.response}')
            return False

    def epa_aqi_bad(self):
        '''
        Is the EPA Air Quality Index too high right now?
        '''
        if 20 < localtime(tz())[4] < 30:
            # Data updates about 10 to 30 minutes after each hour
            self.PM_EPA = AQI('PM')
        if not self.PM_EPA:
            print(f'ON:  EPA Air Quality Unknown (no data from API)') 
            return False
        elif self.PM_EPA > self.high_aqi:
            print(f'OFF: EPA Air Quality is too high at {self.PM_EPA}')
            return True
        else:
            print(f'OK:  EPA Air Quality is good at {self.PM_EPA}')
            return False

    def local_aqi_bad(self):
        '''
        Is the outside Air Quality device to high right now? (neighbors burning leaves?)
        '''
        # self.PM_Local = PMS7003()
        # if self.PM_Local > self.high_aqi:
        #     print(f'OFF: Local Air Quality is too high at {self.PM_Local}')
        #     return True    
        # else:
        #     print(f'OK:  Local Air Quality is good at {self.PM_Local}')
        #     return False
        print('OK:  Local AQI device not installed yet')
        return False
    
    def control(self):
        '''
        Check everything and decide whether to turn ERV On or Off
        '''
        if self.night():
            self.standby()
        elif not self.local_aqi_bad() and not self.epa_aqi_bad() and not self.outside_too_hot_or_cold():
            print('OK:  Daytime checks Passed')
            self.smart()
        else:
            print('OFF: Daytime checks Failed')
            self.standby()

    def smart(self):
        if (self.erv.state == 'smart') and ('OK' in self.erv.status):
            print('ERV already in Smart mode')
        else:
            print('Setting ERV to Smart mode...')
            self.erv.smart()    # Turn ON ERV

    def standby(self):
        if (self.erv.state == 'standby') and ('OK' in self.erv.status):
            print('ERV already in Standby mode.')
        else:
            print('Setting ERV to Standby Mode...')
            self.erv.standby()  # Turn OFF ERV


project = PROJECT()
timer_main = Timer(0)

def timer_function(timer_main):
    project.control()
    wdt.feed()

timer_function(timer_main)  # Initial Run on Boot
timer_main.init(period=main_interval, callback=timer_function)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

