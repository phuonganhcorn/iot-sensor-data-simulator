import random
import datetime
import json
from iot_hub_helper import IoTHubHelper
from enum import Enum
from nicegui import ui

CONNECTION_STRING = "HostName=IoT-Hub-Tobias1.azure-devices.net;DeviceId=sim000001;SharedAccessKey=5y6hx8YYZC6oLEO2/Jbrd8UGLpf4dKA7gf2et1gxm6s="
iot_hub_helper = IoTHubHelper(CONNECTION_STRING)

values = []
tabs = None
table_container = None
chart_container = None
send_button = None
is_chart_drawn = False

class Tab(Enum):
    TABLE = "Tabelle"
    CHART = "Diagramm"

def tab_change_handler(value):
    if value == Tab.CHART.value:
        draw_chart()

# Update root UI element
ui.query('.nicegui-content').classes('p-0')

# Create the UI
with ui.splitter().classes('h-screen') as splitter:
    splitter.classes('w-full')

    # Create the left column
    with splitter.before:
        with ui.column().classes('p-4'):
            ui.label('ADX - Datensimulator').classes('text-2xl font-bold')
            ui.label('Dieses Tool generiert zufällige Temperaturwerte und sendet diese an den Azure IoT Hub.')
            
            with ui.grid(columns=3).classes('w-full'):
                count_input = ui.number(label='Anzahl an Werten', value=10, min=1, max=100)
                device_id_input = ui.input(label='Geräte-ID', value='sim00001')
            
            with ui.column().classes('w-full mt-4 gap-0'):
                ui.label('Simulationswerte').classes('text-base font-bold')
                with ui.grid(columns=3).classes('w-full'):
                    base_value_input = ui.number(label='Basiswert', value=25.00, format='%.2f')
                    variation_range_input = ui.number(label='Variationsbereich', value=5.00, min=0, format='%.2f')
                    interval_input = ui.number(label='Interval [s]', value=10, min=0, max=3600)

            with ui.expansion('Erweiterte Optionen').classes('w-full bg-gray-100 rounded-sm'):
                with ui.grid(columns=3).classes('w-full px-4 pb-4'):
                    with ui.number(label='Änderungsrate +/-', value=0.5, min=0, max=10) as input:
                        change_rate_input = input
                        ui.tooltip('Die Änderungsrate gibt an, wie stark sich ein Wert pro Interval bezogen auf den vorherigen Wert maximal ändern kann.').classes('mx-4')
            
            with ui.column().classes('w-full mt-4 gap-0'):
                ui.label('Anomalien').classes('text-base font-bold')
                with ui.grid(columns=3).classes('w-full'):
                    anomaly_select = ui.select({1: "Keine Anomalien", 2: "Einmalig", 3: "Bleibend"}, value=1, on_change=lambda e: anomaly_max_count_input.set_visibility(e.value == 2))
                    anomaly_max_count_input = ui.number(label='Maximale Anzahl', value=1, min=0, max=100)
                    anomaly_max_count_input.set_visibility(False)

            with ui.expansion('Erweiterte Optionen').classes('w-full bg-gray-100 rounded-sm'):
                with ui.row().classes('px-4 gap-0'):
                    with ui.column().classes('gap-1'):
                        ui.label('Wahrscheinlichkeiten').classes('mt-2 font-bold')
                        ui.label('Definiere mit welcher Wahrscheinlichkeit Anomalien auftreten sollen.').classes('text-[13px] opacity-80')
                    with ui.grid(columns=3).classes('mt-3 mb-4 w-full'):
                        probability_pos_anomaly_input = ui.number(label='Wkt. für pos. Anomalien', value=5, min=0, max=100, suffix='%')
                        probability_neg_anomaly_input = ui.number(label='Wkt. für neg. Anomalien', value=2, min=0, max=100, suffix='%')

                    with ui.column().classes('gap-1'):
                        ui.label('Abweichungsbereiche').classes('mt-4 font-bold')
                        ui.label('Definiere den Wertebereich, in dem Anomalien entstehen können.').classes('text-[13px] opacity-80')
                    with ui.grid(columns=3).classes('mt-3 pb-4 w-full'):
                        with ui.column().classes('gap-0'):
                            ui.label('Positiv').classes('font-medium opacity-70')
                            pos_anomaly_upper_range_input = ui.number(label='Maximal', value=20, min=0, max=100).classes('w-full')
                            pos_anomaly_lower_range_input = ui.number(label='Minimal', value=10, min=0, max=100).classes('w-full')

                        with ui.column().classes('gap-0'):
                            ui.label('Negativ').classes('font-medium opacity-70')
                            neg_anomaly_upper_range_input = ui.number(label='Maximal', value=15, min=0, max=100).classes('w-full')
                            neg_anomaly_lower_range_input = ui.number(label='Minimal', value=5, min=0, max=100).classes('w-full')
            
            ui.button('Daten generieren', on_click=lambda: generate_handler()).classes('mt-8')
            # TODO: Button für Standardwerte wiederherstellen

    # Create the right column
    with splitter.after:
        with ui.column().classes('relative pl-4 pt-16 pb-20 h-full'):
            with ui.tabs(on_change=lambda e: tab_change_handler(e.value)).classes('absolute top-4 left-4 right-4') as tabs:
                tabs = tabs
                one = ui.tab(Tab.TABLE.value)
                two = ui.tab(Tab.CHART.value)
            with ui.tab_panels(tabs, value=one).classes('w-full') as panels:
                with ui.tab_panel(one):
                    table_container = ui.row()
                with ui.tab_panel(two):
                    chart_container = ui.row()

            if len(values) == 0:
                with ui.row().classes('w-full justify-center') as row:
                    tab_note_container = row
                    with ui.row().classes('h-64 flex items-center self-center'):
                        with ui.column().classes('gap-2'):
                            ui.label('Keine Daten generiert').classes('text-lg font-bold text-center w-full')
                            ui.label('Bitte generiere zuerst auf der linken Seite Daten.').classes('text-center w-full')
            
            with ui.row().classes('absolute left-0 bottom-0 px-4 w-full h-20 flex flex-col justify-center shadow-[0_35px_60px_-15px_rgba(0,0,0,1)]'):
                send_button = ui.button('An Azure senden', on_click=lambda: send_handler())
                send_button.disable()

ui.run(title='ADX - Datensimulator')

# Generate the temperature values
def generate_temperature(num_values):
    global values, is_chart_drawn
    
    temperatures = []
    iteration = 0
    anomaly_count = 0
    is_chart_drawn = False # Reset flag

    # Get the input values
    base_value = base_value_input.value
    variation_range = variation_range_input.value
    change_rate = change_rate_input.value
    previous_temperature = base_value
    probability_pos_anomaly = probability_pos_anomaly_input.value / 100
    probability_neg_anomaly = probability_neg_anomaly_input.value / 100
    pos_anomaly_upper_range = pos_anomaly_upper_range_input.value
    pos_anomaly_lower_range = pos_anomaly_lower_range_input.value
    neg_anomaly_upper_range = neg_anomaly_upper_range_input.value
    neg_anomaly_lower_range = neg_anomaly_lower_range_input.value

    while len(temperatures) < num_values:
        temperature_change = random.uniform(-change_rate, change_rate)  # Change within a smaller range
        temperature = previous_temperature + temperature_change
        
        # Limit the temperature within the defined range
        temperature = max(base_value - variation_range, min(base_value + variation_range, temperature))
        
        previous_temperature = temperature  # Update the previous temperature
        
        # Introduce anomalies
        if iteration > 0 and ((anomaly_select.value == 2 and anomaly_count < anomaly_max_count_input.value) or (anomaly_select.value == 3 and anomaly_count == 0)):
            anomaly_appeared = False

            if random.random() < probability_pos_anomaly:  # Adjust the anomaly occurrence probability as needed
                temperature += random.uniform(pos_anomaly_lower_range, pos_anomaly_upper_range)  # Add a positive anomaly
                anomaly_appeared = True
                
            if random.random() < probability_neg_anomaly:  # Adjust the anomaly occurrence probability as needed
                temperature -= random.uniform(neg_anomaly_lower_range, neg_anomaly_upper_range)  # Add a negative anomaly
                anomaly_appeared = True

            if anomaly_appeared:
                print(f'Anomaly introduced at index {iteration}')

                if anomaly_select.value == 3 and anomaly_count == 0:
                    previous_temperature = temperature # Update the previous temperature
                    base_value = temperature # Update the base value to the new temperature
                
                anomaly_count += 1
        
        temperature = round(temperature, 2)  # Round off the temperature value to 2 decimal places
        temperatures.append(temperature)

        iteration += 1

    send_button.enable()

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

def send_handler():
    temperature_values = values
    timestamp_values = generate_timestamps(len(values), interval_input.value)

    # map values into a list of dictionaries
    data = [{
        'time': timestamp_values[i],
        'deviceId': device_id_input.value,
        'temperature': temperature_values[i],
    } for i in range(0, len(temperature_values))]

    response = iot_hub_helper.send_telemetry_messages(data)
    ui.notify(response.message, type='positive' if response.success else 'negative')
