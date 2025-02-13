import sys

# Conversion functions
def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * (5/9)

def fahrenheit_to_kelvin(fahrenheit):
    return (fahrenheit - 32) * (5/9) + 273.15

def celsius_to_fahrenheit(celsius):
    return (celsius * (9/5)) + 32

def celsius_to_kelvin(celsius):
    return celsius + 273.15

def kelvin_to_fahrenheit(kelvin):
    return (kelvin - 273.15) * (9/5) + 32

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

# Check for correct number of command-line arguments
if len(sys.argv) != 3:
    print("Invalid number of arguments!\nUsage: python3 degreesConverter.py degrees unit(capital)")
    sys.exit()

# Extract arguments
degrees = float(sys.argv[1])
unit = sys.argv[2]

# Conversion based on the provided unit
if unit == 'F':
    print("Celsius:")
    print(fahrenheit_to_celsius(degrees))
    print("\nKelvin:")
    print(fahrenheit_to_kelvin(degrees))
elif unit == 'C':
    print("Fahrenheit:")
    print(celsius_to_fahrenheit(degrees))
    print("\nKelvin:")
    print(celsius_to_kelvin(degrees))
elif unit == 'K':
    print("Fahrenheit:")
    print(kelvin_to_fahrenheit(degrees))
    print("\nCelsius:")
    print(kelvin_to_celsius(degrees))
else:
    print("Invalid unit entered!\nValid units include F, C, and K")
