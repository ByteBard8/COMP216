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

    def create_data(self, generator):
        self.start_id += 1
        platform_processor = platform.processor()
        current_temp = generator.value
        current_feels_like = random.gauss(current_temp, 1)
        latitude = random.uniform(-90.0, 90.0)
        longitude = random.uniform(-180.0, 180.0)
        humidity = random.randint(0, 100)
        weather_main = random.choice(['sunny','rain', 'thunderstorm', 'mist', 'snow','scattered clouds', 'broken clouds', 'windy'])
        temp_min = random.uniform(generator.min_value, current_temp)
        temp_max = random.uniform(current_temp, generator.max_value)
        unit = 'deg C'
        self.data = {'packet_id': self.start_id,
                     'time': asctime(),
                     'location': {
                         'lat': latitude,
                         'lng': longitude
                     },
                     'temperature': {
                         'current': round(current_temp, 1),
                         'feels_like': round(current_feels_like, 1),
                         'min': round(temp_min, 1),
                         'max': round(temp_max, 1),
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
