'''
mpremote a0 mip install --target= github:bgant/erv/micropython/vttouchw.py
mpremote a0 mip install --target= github:bgant/erv/micropython/main.py
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
#from PMS7003 import PMS7003 
from utime import localtime
from timezone import tz

main_interval = 300000   # Minutes between Timer loops

class PROJECT:
    '''Main project script run by Timer'''
    def __init__(self):
        self.erv = VTTOUCHW()
        self.weather = WEATHER()
        self.aqi = AQI()
        self.PM_EPA = self.aqi.download('PM')  # Download on boot
        #self.pms7003 = PMS7003()

        # Thresholds
        self.spring      = 106 # Beginning of Summer Hours (Apr 15)
        self.fall        = 289 # Beginning of Winter Hours (Oct 15)
        self.night_end   =  6  # ERV  on after 6AM
        self.night_start = 22  # ERV off after 10PM
        self.too_cold    = 32  # ERV off below 32F
        self.too_hot     = 90  # ERV off above 90F
        self.high_aqi    = 100 # ERV off above 100 PM2.5

    def night(self):
        '''Is it night right now?'''
        self.night_hours = [h % 24 for h in range(self.night_start,self.night_end+24)]
        #if self.spring < localtime(tz())[7] < self.fall:
        #    print('OK:  Run 24x7 in Summer')
        #    return False
        if localtime(tz())[3] in self.night_hours:
            print('OFF: Nighttime')
            return True
        else:
            print('OK:  Daytime')
            return False

    def outside_too_hot_or_cold(self):
        '''Is it too hot or cold outside right now?'''
        self.outside_temp = self.weather.download('temp')
        if self.outside_temp:
            if (self.outside_temp < self.too_cold) or (self.outside_temp > self.too_hot):
                print(f'OFF: Too hot or cold at {self.outside_temp:.0f}F')
                return True
            else:
                print(f'OK:  Outside temperature is good at {self.outside_temp:.0f}F')
                return False
        else:
            print(f'ERROR: API Response is {self.outside_temp}')
            return False

    def epa_aqi_bad(self):
        '''Is the EPA Air Quality Index too high right now?'''
        if 20 < localtime(tz())[4] < 30:
            # Data updates about 10 to 30 minutes after each hour
            self.PM_EPA = self.aqi.download('PM')
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
        '''Is the outside Air Quality device to high right now? (neighbors burning leaves?)'''
        # self.PM_Local = self.pms7003.check()
        # if self.PM_Local > self.high_aqi:
        #     print(f'OFF: Local Air Quality is too high at {self.PM_Local}')
        #     return True    
        # else:
        #     print(f'OK:  Local Air Quality is good at {self.PM_Local}')
        #     return False
        print('OK:  Local AQI device not installed yet')
        return False
    
    def control(self):
        '''Check everything and decide whether to turn ERV On or Off'''
        if self.night():
            self.standby()
        elif not self.local_aqi_bad() and not self.epa_aqi_bad() and not self.outside_too_hot_or_cold():
            print('OK:  All Checks Passed')
            self.smart()
        else:
            print('OFF: One or More Checks Failed')
            self.standby()

    def smart(self):
        '''Change ERV mode to Smart'''
        if (self.erv.state == 'smart') and ('OK' in self.erv.status):
            print('ERV already in Smart mode')
        else:
            print('Setting ERV to Smart mode ', end='')
            self.erv.smart()    # Turn ON ERV

    def standby(self):
        '''Change ERV mode to Standby'''
        if (self.erv.state == 'standby') and ('OK' in self.erv.status):
            print('ERV already in Standby mode.')
        else:
            print('Setting ERV to Standby mode ', end='')
            self.erv.standby()  # Turn OFF ERV


project = PROJECT()
timer_main = Timer(0)

def timer_function(timer_main):
    project.control()
    wdt.feed()

timer_function(timer_main)  # Initial Run on Boot
timer_main.init(period=main_interval, callback=timer_function)
# View Timer value: timer_main.value()   Stop Timer: timer_main.deinit()

