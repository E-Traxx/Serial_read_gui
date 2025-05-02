import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import requests

API_URL = "http://127.0.0.1:8024/incoming_data"

app = dash.Dash(__name__)

# Fehlerdefinitionen aus error_msg_can.csv
ERROR_SIGNALS = [
    "error_bspd_software",
    "error_can_bus",
    "error_general",
    "error_imd",
    "error_u2_inverter",
    "error_latching",
    "error_temperature",
    "error_undervoltage",
    "bms_error",
    "error_u1_inverter"
]

# Dark Theme Layout Einstellungen
DARK_LAYOUT = {
    'plot_bgcolor': '#2a2a2a',
    'paper_bgcolor': '#2a2a2a',
    'font': {'color': 'white'},
    'xaxis': {'showgrid': False, 'tickformat': '%H:%M:%S'},
    'yaxis': {'showgrid': False},
    'margin': dict(l=20, r=20, t=40, b=20)
}

app.layout = html.Div(
    children=[
        # Fehler-LEDs
        html.Div(
            children=[
                html.Div(
                    id=f"led{i}",
                    style={
                        "backgroundColor": "#00ff00",
                        "width": "30px",
                        "height": "30px",
                        "borderRadius": "50%",
                        "boxShadow": "0 0 15px rgb(255, 255, 0)",
                    }
                ) for i in range(1, 11)
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(10, 1fr)",
                "gap": "15px",
                "margin": "20px 0",
                "padding": "10px",
                "background": "#2a2a2a",
                "borderRadius": "15px"
            }
        ),

        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),

        # Hauptlayout
        html.Div(
            children=[
                # Linke Spalte
                html.Div(
                    children=[
                        dcc.Graph(id='speed-graph', style={'height': '300px', 'borderRadius': '15px'}),
                        html.Div(
                            children=[
                                dcc.Graph(id='throttle-brake-graph', style={'flex': 1, 'borderRadius': '15px'}),
                                dcc.Graph(id='inverter-graph', style={'flex': 1, 'borderRadius': '15px'}),
                            ],
                            style={'display': 'flex', 'gap': '20px', 'height': '300px'}
                        ),
                        dcc.Store(id='data-store', data={
                            "time": [],
                            **{signal: [] for signal in [
                                "speed",
                                "driver_input_brake",
                                "driver_input_demanded_throttle",
                                "voltage_left_inverter",
                                "voltage_right_inverter",
                                "temperature_highest_bms",
                                "temperature_u1_motor",
                                "temperature_u2_motor",
                                "temperature_u1_inverter",
                                "temperature_u2_inverter",
                                "info_soc",
                                "current_bms"
                            ]},
                            **{error: [] for error in ERROR_SIGNALS}
                        }),
                    ],
                    style={'width': '65%', 'paddingRight': '20px'}
                ),

                # Rechte Spalte
                html.Div(
                    children=[
                        dcc.Graph(id='temp-graph', style={'height': '400px', 'borderRadius': '15px'}),
                        dcc.Graph(id='soc-graph', style={'height': '300px', 'borderRadius': '15px', 'marginTop': '20px'}),
                    ],
                    style={'width': '35%'}
                )
            ],
            style={'display': 'flex', 'gap': '20px'}
        ),

        # Status-Indikatoren
        html.Div(
            children=[
                dcc.Graph(id='speed-text', style={'width': '24%', 'height': '150px'}),
                dcc.Graph(id='motor-temp-text', style={'width': '24%', 'height': '150px'}),
                dcc.Graph(id='inverter-temp-text', style={'width': '24%', 'height': '150px'}),
                dcc.Graph(id='soc-text', style={'width': '24%', 'height': '150px'}),
            ],
            style={'display': 'flex', 'gap': '10px', 'marginTop': '20px'}
        )
    ],
    style={
        "backgroundColor": "#1a1a1a",
        "color": "white",
        "padding": "20px",
        "minHeight": "100vh"
    }
)

def fetch_data():
    try:
        response = requests.get(API_URL)
        return response.json() if response.ok else {}
    except:
        return {}

@app.callback(
    Output('data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('data-store', 'data')
)
def update_store(n, data):
    new_data = fetch_data()
    time_stamp = pd.Timestamp.now().isoformat()
    
    data["time"].append(time_stamp)
    
    # Signalverarbeitung mit Fehlerbehandlung
    signal_config = {
        # Float-Signale mit Faktor
        "speed": {"type": float, "factor": 0.1},
        "info_soc": {"type": float, "factor": 1.0},
        "voltage_left_inverter": {"type": float, "factor": 1.0},
        "voltage_right_inverter": {"type": float, "factor": 1.0},
        "current_bms": {"type": float, "factor": 1.0},
        
        # Integer-Signale
        "driver_input_brake": {"type": int},
        "driver_input_demanded_throttle": {"type": int},
        "temperature_highest_bms": {"type": int},
        "temperature_u1_motor": {"type": int},
        "temperature_u2_motor": {"type": int},
        "temperature_u1_inverter": {"type": int},
        "temperature_u2_inverter": {"type": int}
    }
    
    for signal, config in signal_config.items():
        raw_value = new_data.get(signal, 0)
        try:
            if config["type"] == float:
                value = float(raw_value) * config.get("factor", 1.0)
            else:
                value = int(float(raw_value))  # Sicherere Konvertierung
            data[signal].append(value)
        except:
            data[signal].append(0)
    
    # Fehlersignale verarbeiten
    for error_signal in ERROR_SIGNALS:
        raw_value = new_data.get(error_signal, 0)
        try:
            data[error_signal].append(int(float(raw_value)))
        except:
            data[error_signal].append(0)
    
    # Daten begrenzen
    for key in data:
        data[key] = data[key][-100:]
    
    return data

@app.callback(
    [Output(f'led{i}', 'style') for i in range(1, 11)],
    Input('data-store', 'data')
)
def update_leds(data):
    styles = []
    for error_signal in ERROR_SIGNALS:
        error_value = data[error_signal][-1] if data[error_signal] else 0
        color = "red" if error_value == 1 else "#00ff00"
        styles.append({
            "backgroundColor": color,
            "width": "30px",
            "height": "30px",
            "borderRadius": "50%",
            "boxShadow": f"0 0 15px {color}"
        })
    return styles

@app.callback(
    [Output('speed-graph', 'figure'),
     Output('throttle-brake-graph', 'figure'),
     Output('inverter-graph', 'figure'),
     Output('temp-graph', 'figure'),
     Output('soc-graph', 'figure')],
    Input('data-store', 'data')
)
def update_graphs(data):
    try:
        time_window = data["time"][-20:]
        
        # Geschwindigkeitsgraph
        speed_fig = px.line(x=time_window, y=data["speed"][-20:], title="Geschwindigkeit (km/h)")
        speed_fig.update_traces(line_color='#00ff00')
        
        # Bremse/Gaspedal
        throttle_fig = go.Figure()
        throttle_fig.add_trace(go.Scatter(
            x=time_window, 
            y=data["driver_input_brake"][-20:], 
            name='Bremse', 
            line_color='red'))
        throttle_fig.add_trace(go.Scatter(
            x=time_window,
            y=data["driver_input_demanded_throttle"][-20:],
            name='Gaspedal',
            line_color='green'))
        
        # Inverter-Spannungen
        inverter_fig = go.Figure()
        inverter_fig.add_trace(go.Scatter(
            x=time_window,
            y=data["voltage_left_inverter"][-20:],
            name='Links',
            line_color='blue'))
        inverter_fig.add_trace(go.Scatter(
            x=time_window,
            y=data["voltage_right_inverter"][-20:],
            name='Rechts',
            line_color='orange'))
        
        # Temperaturen
        temp_fig = go.Figure()
        temp_fig.add_trace(go.Scatter(
            x=time_window,
            y=data["temperature_u1_motor"][-20:],
            name='Motor U1',
            line_color='#ff00ff'))
        temp_fig.add_trace(go.Scatter(
            x=time_window,
            y=data["temperature_u1_inverter"][-20:],
            name='Inverter U1',
            line_color='#00ffff'))
        
        # SOC
        soc_fig = px.line(x=time_window, y=data["info_soc"][-20:], title="Ladezustand (%)")
        soc_fig.update_traces(line_color='#00ff00')
        
        # Layout anwenden
        for fig in [speed_fig, throttle_fig, inverter_fig, temp_fig, soc_fig]:
            fig.update_layout(**DARK_LAYOUT)
        
        return speed_fig, throttle_fig, inverter_fig, temp_fig, soc_fig
    
    except Exception as e:
        print(f"Graph Error: {e}")
        return [go.Figure(layout=DARK_LAYOUT) for _ in range(5)]

@app.callback(
    [Output('speed-text', 'figure'),
     Output('motor-temp-text', 'figure'),
     Output('inverter-temp-text', 'figure'),
     Output('soc-text', 'figure')],
    Input('data-store', 'data')
)
def update_indicators(data):
    indicators = [
        ('speed', 'Geschwindigkeit', 'km/h', '#00ff00'),
        ('temperature_u1_motor', 'Motor Temp', '°C', '#ff6600'),
        ('temperature_u1_inverter', 'Inverter Temp', '°C', '#ff00ff'),
        ('info_soc', 'Ladezustand', '%', '#00ffff')
    ]
    
    figs = []
    for key, title, unit, color in indicators:
        try:
            value = data[key][-1] if data[key] else 0
            fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=value,
                number={"suffix": f" {unit}", "font": {"color": color, "size": 40}},
                title={"text": title, "font": {"color": "white", "size": 16}},
                delta={'reference': data[key][-2] if len(data[key]) > 1 else 0}
            ))
            fig.update_layout(**DARK_LAYOUT)
            figs.append(fig)
        except:
            figs.append(go.Figure(layout=DARK_LAYOUT))
    
    return tuple(figs)

if __name__ == "__main__":
    app.run(debug=True, port=8050)