import random
from time import asctime
from json import dumps
import platform

class Util:
    max_temp = 26
    min_temp = 16

    def __init__(self):
        self.start_id = 111
        self.data = {}

    def create_data(self):
        self.start_id += 1
        platform_processor = platform.processor()
        current_temp = self.min_temp + (self.max_temp - self.min_temp) * random.uniform(0, 1)
        current_feels_like = random.gauss(current_temp)
        latitude = random.uniform(-90.0, 90.0)
        longitude = random.uniform(-180.0, 180.0)
        humidity = random.randint(0, 100)
        weather_main = random.choice(['sunny','rain', 'thunderstorm', 'mist', 'snow','scattered clouds', 'broken clouds', 'windy'])
        temp_min = random.uniform(self.min_temp, current_temp)
        temp_max = random.uniform(current_temp, self.max_temp)
        unit = 'deg C'
        self.data = {'id': self.start_id,
                     'time': asctime(),
                     'platform': platform_processor,
                     'location': {
                         'lat': latitude,
                         'lng': longitude
                     },
                     'temperature': {
                         'current': current_temp,
                         'feels_like': current_feels_like,
                         'min': temp_min,
                         'max': temp_max,
                         'unit': unit
                     },
                     'humidity': humidity,
                     'weather': weather_main
                     }
        return self.data

    def print_data(self, data):
        print(dumps(data, indent=4))

# gen = Util()
# for x in range(5):
#     y = gen.create_data()
#     gen.print_data(y)
