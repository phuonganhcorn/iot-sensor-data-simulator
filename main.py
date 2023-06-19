import random

def generate_temperature(num_values):
    base_value = 25.0
    variation_range = 5.0
    previous_temperature = base_value
    temperatures = []

    while len(temperatures) < num_values:
        temperature_change = random.uniform(-1.0, 1.0)  # Change within a smaller range
        temperature = previous_temperature + temperature_change
        
        # Limit the temperature within the defined range
        temperature = max(base_value - variation_range, min(base_value + variation_range, temperature))
        
        previous_temperature = temperature  # Update the previous temperature
        
        # Introduce anomalies
        if random.random() < 0.05:  # Adjust the anomaly occurrence probability as needed
            temperature += random.uniform(10, 20)  # Add a positive anomaly
            
        if random.random() < 0.02:  # Adjust the anomaly occurrence probability as needed
            temperature -= random.uniform(5, 15)  # Add a negative anomaly
        
        temperature = round(temperature, 2)  # Round off the temperature value to 2 decimal places
        temperatures.append(temperature)

    return temperatures

# Example usage
temperature_values = generate_temperature(10)  # Generate 10 temperature values

# Print the generated temperature values
for temperature in temperature_values:
    print(temperature)
