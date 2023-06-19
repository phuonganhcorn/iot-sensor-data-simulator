import random
from nicegui import ui

table_container = None
chart_container = None

# Create the UI
with ui.splitter() as splitter:
    splitter.classes('w-full')
    with splitter.before:
        with ui.column() as column:
            ui.label('IoT Hub Data Simulator')
            base_value_input = ui.number(label='Basiswert', value=25.00, format='%.2f')
            ui.number(label='Variationsbereich', value=5.00, format='%.2f')
            ui.button('Daten generieren', on_click=lambda: generate_handler())
    with splitter.after:
        with ui.tabs().classes('w-full') as tabs:
            one = ui.tab('Tabelle')
            two = ui.tab('Diagramm')
        with ui.tab_panels(tabs, value=two).classes('w-full'):
            with ui.tab_panel(one):
                table_container = ui.row()
            with ui.tab_panel(two):
                chart_container = ui.row()
                
        ui.button('Zu Azure senden')

ui.run()

def generate_temperature(num_values):
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

    return temperatures

def clear_output():
    global table_container

    if table_container is not None:
        table_container.clear()
    
    if chart_container is not None:
        chart_container.clear()

def print_values(temperature_values):
    # Print the generated temperature values
    columns = [{
        'name': 'temperature',
        'label': 'Temperatur',
        'field': 'temperature',
        'required': True,
    }]

    # map the temperature values to the columns
    rows = [{
        'temperature': str(temperature) + ' °C',
    } for temperature in temperature_values]

    with table_container:
        ui.table(columns=columns, rows=rows).classes('w-full shadow-none')

    with chart_container:
        ui.chart({
            'title': False,
            'series': [
                {'name': 'Temperatur', 'data': temperature_values},
            ],
        }).classes('w-full h-64')

def generate_handler():
    clear_output()
    temperature_values = generate_temperature(10)  # Generate 10 temperature values
    print_values(temperature_values)
