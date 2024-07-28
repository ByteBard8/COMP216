import random
import matplotlib.pyplot as plt

class DataGenerator:
    """
    This class generates simulated sensor data using different methods
    """
    
    def __init__(self, min_value=18, max_value=21, mean=19.5, stddev=1.0, base=19.5, delta=0.15):
        """
        Initializes the DataGenerator with default values
        """
        self.min_value = min_value
        self.max_value = max_value
        self.mean = mean
        self.stddev = stddev
        self.base = base
        self.delta = delta
        self._increment = True

    def _generate_normalized_value(self):
        """
        Generates a random value between 0 and 1
        """
        return random.uniform(0, 1)

    def _generate_uniform_value(self):
        """
        Generates a uniformly distributed value within the specified range
        """
        return self.min_value + (self.max_value - self.min_value) * self._generate_normalized_value()

    def _generate_normal_value(self):
        """
        Generates a normally distributed value with the specified mean and standard deviation
        """
        return random.gauss(self.mean, self.stddev)

    def _generate_pattern_value(self):
        """
        Generates a value following a predictable pattern by incrementing or decrementing the base value
        """
        if self._increment:
            self.base += self.delta
        else:
            self.base -= self.delta
        
        # Toggle increment/decrement
        if self.base >= self.max_value or self.base <= self.min_value:
            self._increment = not self._increment
        
        return self.base

    @property
    def value(self):
        """
        Property that randomly selects a generation method (uniform, normal or pattern) and returns a value
        """
        method = random.choice(['uniform', 'normal', 'pattern'])
        if method == 'uniform':
            return self._generate_uniform_value()
        elif method == 'normal':
            return self._generate_normal_value()
        elif method == 'pattern':
            return self._generate_pattern_value()

# Create an instance of DataGenerator
generator = DataGenerator()

# Generate 500 data points
num_values = 500
values = [generator.value for _ in range(num_values)]

# Plotting the data points
plt.figure(figsize=(10, 5))
plt.plot(values, 'r+', label='Simulated Data')
plt.title('Simulated Sensor Data')
plt.xlabel('Data Point Index')
plt.ylabel('Value')
plt.legend()
plt.grid(True)
#plt.show()

