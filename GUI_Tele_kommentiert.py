import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import requests


# Übersicht:
# 1) dcc.Interval -> triggert update_store() -> holt Daten via fetch_data()
# 2) update_store() -> skaliert/konvertiert Signale & hängt sie als Zeitreihe an
# 3) update_graphs() -> baut die 7 Plots aus den letzten Punkten
# 4) update_leds() -> färbt die Fehler-LEDs (rot/grün)
# 5) update_indicators() -> zeigt 4 kompakte Kennzahlen (go.Indicator)


FONT_FAMILY = "Inter, Roboto, Arial, sans-serif"        # Schriftart für die gesamte GUI, kann man anpassen, wurde mir vorgeschlagen
GRID_COLOR  = "#555"   
SPACING_4   = "4px"
SPACING_8   = "8px"
SPACING_16  = "16px"
SPACING_32  = "32px"

# Backend API URL,  die aus der Telemetriedaten abgerufen werden

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
# Die REIHENFOLGE in ERROR_SIGNALS bestimmt 1:1 die Reihenfolge der LEDs in der oberen LED-Leiste
# UND die Reihenfolge der Outputs im LED-Callback. Wenn du hier eine neue Fehlervariable  einfügst,
# erscheint automatisch eine neue LED an der Stelle, an der du sie in dieser Liste platzierst



# Dark Theme Layout Einstellungen
DARK_LAYOUT = {
    'plot_bgcolor': '#2a2a2a',
    'paper_bgcolor': '#2a2a2a',
    'font': {'color': 'white', 'family': FONT_FAMILY},
    'xaxis': {'showgrid': True, 'gridcolor': GRID_COLOR, 'gridwidth': 0.5, 'tickformat': '%H:%M:%S'},
    'yaxis': {'showgrid': True, 'gridcolor': GRID_COLOR, 'gridwidth': 0.5},
    'margin': dict(l=20, r=20, t=60, b=20)
}

# Card Style für alle Graphen
GRAPH_STYLE = {'borderRadius': '15px', 'overflow': 'hidden'}


# Applies consistent styling to x and y axes
def apply_axis_style(fig):
    fig.update_xaxes(
        title_text='',
        tickangle=-30,
        ticks="outside",
        tickfont=dict(size=10),
        showgrid=True,
        gridcolor="#444",
        dtick=1 
    )
    fig.update_yaxes(
        tickfont=dict(size=10),
        ticks="outside",
        showgrid=True,
        gridcolor="#444"
    )

# puts legends above the plots
def place_legend_top(fig):
    fig.update_layout(
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=10),
            bgcolor='rgba(0,0,0,0)'
        )
    )

app.layout = html.Div(
    children=[
        # Fehler‑LED‑Bar oben
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            id=f"led_{err}",  # dynamische ID: ergibt z.B. led_error_imd, led_bms_error etc.
                            style={
                                "backgroundColor": "#00ff00",
                                "width": "24px",
                                "height": "24px",
                                "borderRadius": "50%",
                                "boxShadow": "0 0 12px #00ff00",
                                "transition": "all 0.25s ease"
                            },
                        ), 

                        #html.Span(             #weiß gerade nich wofür das war lol 
                        #    err.replace("_", " "),
                        #    style={
                        #        "marginTop": "4px",
                        #        "fontSize": "11px",
                        #        "color": "white",
                        #        "whiteSpace": "nowrap",
                        #    },
                        #),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "minWidth": "80px",
                    },
                )
                
                #für jede LED eine html.Div mit dynamischer ID 
                for err in ERROR_SIGNALS  # <- erzeugt pro 'err' genau EIN LED-Element
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": SPACING_32,
                "margin": f"{SPACING_16} 0",
                "padding": "10px",
                "background": "#2a2a2a",
                "borderRadius": "15px",
            },
        ),

        dcc.Interval(id='interval-component', interval=500, n_intervals=0),     # alle 500 ms aktualisieren


        #die gruppierung der graphen sehen bisschen weird aus, aber klappt so   -> |°_°|

        # Hauptlayout
        html.Div(
            children=[
                # Linke Spalte
                html.Div(
                    children=[
                        html.Div(
                            children=[      # Obere Hauptcharts
                                dcc.Graph(id='speed-graph', style={'flex': 1, 'height': '300px', **GRAPH_STYLE}),
                                dcc.Graph(id='bms-graph',   style={'flex': 1, 'height': '300px', **GRAPH_STYLE}),
                            ],
                            style={'display': 'flex', 'gap': SPACING_32, 'marginBottom': '30px'}
                        ),
                        html.Div(
                            children=[  # Mittlere Hauptcharts
                                dcc.Graph(id='throttle-brake-graph', style={'flex': 1, **GRAPH_STYLE}),
                                dcc.Graph(id='inverter-graph', style={'flex': 1, **GRAPH_STYLE}),
                            ],
                            style={'display': 'flex', 'gap': SPACING_32, 'height': '300px'}
                        ),
                        # unten links – kleine graphen
                        html.Div(
                            children=[
                                dcc.Graph(id='speed-text', style={'height': '180px', **GRAPH_STYLE}),
                                dcc.Graph(id='motor-temp-text', style={'height': '180px', **GRAPH_STYLE}),
                                dcc.Graph(id='signal-text', style={'height': '180px', **GRAPH_STYLE}),
                                dcc.Graph(id='soc-text', style={'height': '180px', **GRAPH_STYLE}),
                            ],
                            style={
                                'display': 'grid',
                                'gridTemplateColumns': 'repeat(2, 1fr)',
                                'gridAutoRows': '1fr',
                                'gap': SPACING_16,
                                'marginTop': '20px'
                            }
                        ),
                        # dcc.Store zur Speicherung der Zeitreihendaten
                        #Das sind die Namen aus der API, wenn neue hinzugefügt werden,
                        #müssen die auch hier rein,  mit 1:1 den Namen
                        dcc.Store(id='data-store', data={
                            "time": [],
                            **{signal: [] for signal in [
                                "speed",
                                "driver_input_break",
                                "driver_input_demanded_throttle",
                                "voltage_left_inverter",
                                "voltage_right_inverter",
                                "temperature_highest_bms",
                                "temperature_u1_motor",
                                "temperature_u2_motor",
                                "temperature_u1_inverter",
                                "temperature_u2_inverter",
                                "info_soc",
                                "current_bms",
                                "charge_bms",
                                "signal_info",
                            ]},
                            **{error: [] for error in ERROR_SIGNALS}
                        }),
                    ],
                    style={'width': '70%', 'paddingRight': '20px'}
                ),

                # Rechte Spalte
                html.Div(
                    children=[
                        dcc.Graph(id='motor-temp-graph', style={'height': '300px', **GRAPH_STYLE}),
                        dcc.Graph(id='inv-temp-graph', style={'height': '300px', **GRAPH_STYLE, 'marginTop': '20px'}),
                        dcc.Graph(id='soc-graph', style={'height': '420px', **GRAPH_STYLE, 'marginTop': '20px'}),
                    ],
                    style={'width': '35%'}
                )
            ],
            style={'display': 'flex', 'gap': SPACING_16}
        ),

    ],
    style={
        "backgroundColor": "#1a1a1a",
        "color": "white",
        "padding": "20px",
        "minHeight": "100vh",
        "fontFamily": FONT_FAMILY
    }
)

# Funktion zum Abrufen der Telemetriedaten von der API
def fetch_data():
    try:
        response = requests.get(API_URL)
        return response.json() if response.ok else {}
    except:
        return {}

# Callback zum Aktualisieren der Graphen
# Callback wird getriggert wenn sich der Store ändert
@app.callback(
    [Output('speed-graph', 'figure'),
     Output('bms-graph',   'figure'),
     Output('throttle-brake-graph', 'figure'),
     Output('inverter-graph', 'figure'),
     Output('motor-temp-graph', 'figure'),
     Output('inv-temp-graph', 'figure'),
     Output('soc-graph', 'figure')],
    Input('data-store', 'data')
)

# Aktualisiert die Graphen basierend auf den Daten im dcc.Store
def update_graphs(data):
    try:
        index_window = list(range(len(data["time"])))[-10:]
        
        # Geschwindigkeitsgraph
        speed_fig = px.line(x=index_window, y=data["speed"][-10:], title="Geschwindigkeit (km/h)")
        speed_fig.update_traces(line_color='#00ff00')
        
        # BMS Charge & Current
        bms_fig = go.Figure()
        bms_fig.add_trace(go.Scatter(
            x=index_window,
            y=data["charge_bms"][-10:],
            name='Charge (Ah)',
            line_color='#00ffff'))
        bms_fig.add_trace(go.Scatter(
            x=index_window,
            y=data["current_bms"][-10:],
            name='Current (A)',
            line_color='#ffffff'))
        bms_fig.update_yaxes(title_text="Ah / A")
        
        # Bremse/Gaspedal
        throttle_fig = go.Figure()
        throttle_fig.add_trace(go.Scatter(
            x=index_window, 
            y=data["driver_input_break"][-10:], 
            name='Bremse', 
            line_color='red'))
        throttle_fig.add_trace(go.Scatter(
            x=index_window,
            y=data["driver_input_demanded_throttle"][-10:],
            name='Gaspedal',
            line_color='green'))
        throttle_fig.update_yaxes(range=[0, 100])
        
        # Inverter-Spannungen
        inverter_fig = go.Figure()
        inverter_fig.add_trace(go.Scatter(
            x=index_window,
            y=data["voltage_left_inverter"][-10:],
            name='Inv L (V)',
            line_color='blue'))
        inverter_fig.add_trace(go.Scatter(
            x=index_window,
            y=data["voltage_right_inverter"][-10:],
            name='Inv R (V)',
            line_color='orange'))
        
        # Motor‐ und BMS‐Temperaturen
        motor_temp_fig = go.Figure()
        motor_temp_fig.add_trace(go.Scatter(x=index_window, y=data["temperature_u1_motor"][-10:], name='Motor U1 (°C)', line_color='#ff6600'))
        motor_temp_fig.add_trace(go.Scatter(x=index_window, y=data["temperature_u2_motor"][-10:], name='Motor U2 (°C)', line_color='#ffff00'))
        motor_temp_fig.add_trace(go.Scatter(x=index_window, y=data["temperature_highest_bms"][-10:], name='BMS max (°C)', line_color='#ff2b2b'))

        # Inverter‐Temperaturen
        inv_temp_fig = go.Figure()
        inv_temp_fig.add_trace(go.Scatter(x=index_window, y=data["temperature_u1_inverter"][-10:], name='Inv U1 (°C)', line_color='#ff00ff'))
        inv_temp_fig.add_trace(go.Scatter(x=index_window, y=data["temperature_u2_inverter"][-10:], name='Inv U2 (°C)', line_color='#ffa500'))
        
        # SOC
        soc_fig = px.line(x=index_window, y=data["info_soc"][-10:], title="State of Charge (%)")
        soc_fig.update_traces(line_color='#00ff00')
        
        # Layout anwenden
        for fig in [speed_fig, bms_fig, throttle_fig, inverter_fig, motor_temp_fig, inv_temp_fig, soc_fig]:
            fig.update_layout(**DARK_LAYOUT)
        for fig in [speed_fig, bms_fig, throttle_fig, inverter_fig, motor_temp_fig, inv_temp_fig, soc_fig]:
            apply_axis_style(fig)
        for fig in [speed_fig, bms_fig, throttle_fig, inverter_fig, motor_temp_fig, inv_temp_fig, soc_fig]:
            place_legend_top(fig)
        
        # Einheitliche Achsenbeschriftungen
        speed_fig.update_yaxes(title_text="km/h")
        throttle_fig.update_yaxes(title_text="%")
        inverter_fig.update_yaxes(title_text="V / A")
        motor_temp_fig.update_yaxes(title_text="°C")
        inv_temp_fig.update_yaxes(title_text="°C")
        soc_fig.update_yaxes(title_text="%")
        
        return speed_fig, bms_fig, throttle_fig, inverter_fig, motor_temp_fig, inv_temp_fig, soc_fig
    
    except Exception as e:
        print(f"Graph Error: {e}")
        return [go.Figure(layout=DARK_LAYOUT) for _ in range(7)]

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
        # Werte kommen bereits skaliert vom Backend
        "speed": {"type": float, "factor": 1.0},
        "info_soc": {"type": float, "factor": 1.0},
        "voltage_left_inverter": {"type": float, "factor": 1.0},
        "voltage_right_inverter": {"type": float, "factor": 1.0},
        "current_bms": {"type": float, "factor": 1.0},
        "charge_bms": {"type": float, "factor": 1.0},

        # Scale raw 0–127 to 0–100%
        "driver_input_break": {"type": float, "factor": 100.0/127.0},
        "driver_input_demanded_throttle": {"type": float, "factor": 100.0/127.0},
        "temperature_highest_bms": {"type": int},
        "temperature_u1_motor": {"type": int},
        "temperature_u2_motor": {"type": int},
        "temperature_u1_inverter": {"type": int},
        "temperature_u2_inverter": {"type": int},
                
        "signal_info": {"type": int},
    }
    
    for signal, config in signal_config.items():
        source_key = config.get("source", signal)
        raw_value = new_data.get(source_key, 0)
        try:
            if config["type"] == float:
                value = float(raw_value) * config.get("factor", 1.0)
            else:
                value = int(float(raw_value))  
            data[signal].append(value)
        except:
            data[signal].append(0)
    # Fehlersignale verarbeiten

    # Für JEDES definierte Fehlersignal holen wir den aktuellen Wert aus der API-Antwort
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
    [Output(f'led_{err}', 'style') for err in ERROR_SIGNALS],
    Input('data-store', 'data')
)

def update_leds(data):

    styles = []  
    for error_signal in ERROR_SIGNALS: 
       
        error_value = data[error_signal][-1] if data[error_signal] else 0
 
        color = "red" if error_value == 1 else "#00ff00"
       
        styles.append({
            "backgroundColor": color,
            "width": "24px",
            "height": "24px",
            "borderRadius": "50%",
            "boxShadow": f"0 0 12px {color}",
            "transition": "all 0.25s ease"
        })
    return styles

@app.callback(
    [Output('speed-text', 'figure'),
     Output('motor-temp-text', 'figure'),
     Output('signal-text', 'figure'),
     Output('soc-text', 'figure')],
    Input('data-store', 'data')
)
def update_indicators(data):
    indicators = [
        ('speed', 'Geschwindigkeit', 'km/h', '#00ff00'),
        ('temperature_u1_motor', 'Motor Temp', '°C', '#ff6600'),
        ('signal_info', 'signal', 'dBm', '#ff00ff'),             
        ('info_soc', 'Ladezustand', '%', '#00ffff')
    ]
      
                 
#   farben für signal_info
#   < -50 dBm:    Grün (#00ff00)
#   -60 bis -50 dBm: Hellgrün (#66ff66)
#   -70 bis -60 dBm: Gelb (#ffff00)
#   -80 bis -70 dBm: Orange (#ff9900)
#   < -80 dBm:    Rot (#ff0000)
    figs = []
    for key, title, unit, color in indicators:
        try:
            if key == 'signal_info':           
                 if value < -50:
                     color = "#00ff00"  
                 elif value >= -60:
                     color = "#66ff66"  
                 elif value >= -70:
                     color = "#ffff00"  
                 elif value >= -80:
                     color = "#ff9900"  
                 else:
                     color = "#ff0000" 


            value = data[key][-1] if data[key] else 0

            number_size = 50 if key == 'info_soc' else 40
            fig = go.Figure(go.Indicator(
                mode="number+delta",
                value=value,
                number={"suffix": f" {unit}", "font": {"color": color, "size": number_size}},
                title={"text": title, "font": {"color": "white", "size": 16}},
                delta={'reference': data[key][-2] if len(data[key]) > 1 else 0}
            ))

           
            fig.update_layout(**DARK_LAYOUT)
            fig.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                paper_bgcolor='#2a2a2a',
            )
            figs.append(fig)
        except:
            figs.append(go.Figure(layout=DARK_LAYOUT))
    return tuple(figs)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)