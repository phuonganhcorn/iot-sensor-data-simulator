import random
import datetime
from nicegui import ui

values = []
tabs = None
table_container = None
chart_container = None
is_chart_drawn = False

def tab_change_handler(value):
    if value == "Diagramm": # mit ENUM ersetzen
        draw_chart()

# Create the UI
with ui.splitter() as splitter:
    splitter.classes('w-full')

    # Create the left column
    with splitter.before:
        with ui.column() as column:
            ui.label('IoT Hub Data Simulator')
            ui.label('Dieses Tool generiert zufällige Temperaturwerte und sendet diese an den Azure IoT Hub.')
            
            device_id_input = ui.input(label='Geräte-ID', value='sim00001')
            base_value_input = ui.number(label='Basiswert', value=25.00, format='%.2f')
            ui.number(label='Variationsbereich', value=5.00, format='%.2f')
            interval_input = ui.number(label='Interval [s]', value=10.00, format='%.2f')

            ui.button('Daten generieren', on_click=lambda: generate_handler())

    # Create the right column
    with splitter.after:
        with ui.tabs(on_change=lambda e: tab_change_handler(e.value)).classes('w-full') as tabs:
            tabs = tabs
            one = ui.tab('Tabelle')
            two = ui.tab('Diagramm')
        with ui.tab_panels(tabs, value=one).classes('w-full') as panels:
            with ui.tab_panel(one):
                table_container = ui.row()
            with ui.tab_panel(two):
                chart_container = ui.row()
                
        ui.button('Zu Azure senden')

ui.run()

# Generate the temperature values
def generate_temperature(num_values):
    global values, is_chart_drawn

    is_chart_drawn = False
    base_value = base_value_input.value
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

    values = temperatures
    return temperatures

# creates a list of timestamp values every n (interval) seconds beginning now
def generate_timestamps(num_values, interval=10):
    now = datetime.datetime.now()
    timestamps = [(now + datetime.timedelta(seconds=i*interval)).isoformat() for i in range(0, num_values)]

    return timestamps

# clears the output
def clear_output():
    global table_container, values

    values = []

    if table_container is not None:
        table_container.clear()
    
    if chart_container is not None:
        chart_container.clear()

# prints the passed values
def print_values(temperature_values, timestamp_values):
    global table_container, tabs

    # Print the generated temperature values
    columns = [
        {
            'name': 'device_id',
            'label': 'Geräte-ID',
            'field': 'device_id',
            'required': True,
            'align': 'left',
        },
        {
            'name': 'temperature',
            'label': 'Temperatur',
            'field': 'temperature',
            'required': True,
        },
        {
            'name': 'timestamp',
            'label': 'Zeitstempel',
            'field': 'timestamp',
            'required': True,
        }
    ]

    # map the temperature values to the columns
    rows = [{
        'device_id': device_id_input.value,
        'temperature': str(temperature_values[i]) + ' °C',
        'timestamp': timestamp_values[i],
    } for i in range(0, len(temperature_values))]

    with table_container:
        ui.table(columns=columns, rows=rows).classes('w-full shadow-none')

    if tabs.value == "Diagramm":
        draw_chart()

# draws the chart
def draw_chart():
    global values, is_chart_drawn, chart_container

    if is_chart_drawn:
        return

    with chart_container:
        ui.chart({
            'title': False,
            'series': [
                {'name': 'Temperatur', 'data': values},
            ],
        }).classes('w-full h-64')

    is_chart_drawn = True

# generates the values and prints them
def generate_handler():
    clear_output()
    temperature_values = generate_temperature(10)  # Generate 10 temperature values
    timestamp_values = generate_timestamps(10, interval_input.value)  # Generate 10 timestamp values

    print_values(temperature_values, timestamp_values)
