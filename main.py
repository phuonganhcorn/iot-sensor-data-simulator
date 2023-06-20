import random
import datetime
from enum import Enum
from nicegui import ui

values = []
tabs = None
table_container = None
chart_container = None
is_chart_drawn = False

class Tab(Enum):
    TABLE = "Tabelle"
    CHART = "Diagramm"

def tab_change_handler(value):
    if value == Tab.CHART.value:
        draw_chart()

# Create the UI
with ui.splitter() as splitter:
    splitter.classes('w-full')

    # Create the left column
    with splitter.before:
        with ui.column() as column:
            ui.label('ADX - Data Simulator').classes('text-2xl font-bold')
            ui.label('Dieses Tool generiert zufällige Temperaturwerte und sendet diese an den Azure IoT Hub.')
            
            count_input = ui.number(label='Anzahl', value=10, min=1, max=100)
            device_id_input = ui.input(label='Geräte-ID', value='sim00001')
            base_value_input = ui.number(label='Basiswert', value=25.00, format='%.2f')
            ui.number(label='Variationsbereich', value=5.00, min=0, format='%.2f')
            interval_input = ui.number(label='Interval [s]', value=10, min=0, max=3600)

            ui.button('Daten generieren', on_click=lambda: generate_handler())

    # Create the right column
    with splitter.after:
        with ui.tabs(on_change=lambda e: tab_change_handler(e.value)).classes('w-full') as tabs:
            tabs = tabs
            one = ui.tab(Tab.TABLE.value)
            two = ui.tab(Tab.CHART.value)
        with ui.tab_panels(tabs, value=one).classes('w-full') as panels:
            with ui.tab_panel(one):
                table_container = ui.row()
            with ui.tab_panel(two):
                chart_container = ui.row()

        if len(values) == 0:
            with ui.row() as row:
                tab_note_container = row
                with ui.row().classes('mx-auto h-64 flex items-center'):
                    with ui.column().classes('gap-2'):
                        ui.label('Keine Daten generiert').classes('text-lg font-bold text-center w-full')
                        ui.label('Bitte generiere zuerst auf der linken Seite Daten.').classes('text-center w-full')
                
        ui.button('Zu Azure senden').classes('mt-4 mx-4')

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
    global values

    values = []

    if table_container is not None:
        table_container.clear()
    
    if chart_container is not None:
        chart_container.clear()

# prints the passed values
def print_values(temperature_values, timestamp_values):
    tab_note_container.clear()

    # Print the generated temperature values
    columns = [
        {
            'name': 'id',
            'label': 'ID',
            'field': 'id',
            'required': True,
            'align': 'left',
        },
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
        'id': i + 1,
        'device_id': device_id_input.value,
        'temperature': str(temperature_values[i]) + ' °C',
        'timestamp': timestamp_values[i],
    } for i in range(0, len(temperature_values))]

    with table_container:
        ui.table(columns=columns, rows=rows).classes('w-full shadow-none')

    if tabs.value == Tab.CHART.value:
        draw_chart()

# draws the chart
def draw_chart():
    global is_chart_drawn

    if is_chart_drawn or len(values) == 0:
        return
    
    # generate the data for the chart
    data = [[
        i * int(interval_input.value), # x-axis value
        values[i], # y-axis value
     ] for i in range(0, len(values))]

    with chart_container:
        ui.chart({
            'title': False,
            'series': [
                {'name': device_id_input.value, 'data': data},
            ],
            'yAxis': {
                'title': {
                    'text': 'Temperatur'
                },
                'labels': {
                    'format': '{value} °C'
                }
            },
            'xAxis': {
                'title': {
                    'text': 'Zeit'
                },
                'labels': {
                    'format': '{value}s'
                }
            },
        }).classes('w-full h-64')

    is_chart_drawn = True

# generates the values and prints them
def generate_handler():
    clear_output()

    values_count = int(count_input.value)  # Get the number of values to generate
    temperature_values = generate_temperature(values_count)  # Generate 10 temperature values
    timestamp_values = generate_timestamps(values_count, interval_input.value)  # Generate 10 timestamp values

    print_values(temperature_values, timestamp_values)
