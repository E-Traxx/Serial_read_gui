import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import requests

API_URL = "http://127.0.0.1:8024/incoming_data"

app = dash.Dash(__name__)

# Initialisiere Figuren
speed_fig = go.Figure()        
throttle_brake_fig = go.Figure()       
inverter_fig = go.Figure()      
temp_graph_fig = go.Figure()
voltage_soc_fig = go.Figure()

app.layout = html.Div(
    children=[
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
                ) for i in range(1, 7)  # 6 LEDs für Fehlerzustände
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(6, 1fr)",
                "gap": "20px",
                "margin": "20px 0",
                "padding": "10px",
                "background": "#2a2a2a",
                "borderRadius": "15px",
                "justifyContent": "center"
            }
        ),

        dcc.Interval(id='interval-component_led', interval=500, n_intervals=0),
        
        html.Div(
            children=[
                html.Div(
                    children=[
                        # Speed Graph (ganze Breite)
                        dcc.Graph(id='speed-graph', figure=speed_fig,
                                 style={'height': '300px', 'borderRadius': '15px', 'marginBottom': '20px'}),
                        
                        # Untere Graph-Reihe
                        html.Div(
                            children=[
                                dcc.Graph(id='throttle-brake-graph', figure=throttle_brake_fig,
                                         style={'height': '300px', 'flex': 1, 'borderRadius': '15px'}),
                                dcc.Graph(id='inverter-graph', figure=inverter_fig,
                                         style={'height': '300px', 'flex': 1, 'borderRadius': '15px'}),
                            ],
                            style={'display': 'flex', 'gap': '20px'}
                        ),
                        
                        dcc.Interval(id='interval-component', interval=500, n_intervals=0),
                        dcc.Store(id='data-store', data={
                            "time": [],
                            "speed": [],
                            "driver_input_brake": [],
                            "driver_input_demanded_throttle": [],
                            "voltage_left_inverter": [],
                            "voltage_right_inverter": [],
                            "temperature_highest_bms": [],
                            "temperature_u1_motor": [],
                            "temperature_u2_motor": [],
                            "temperature_u1_inverter": [],
                            "temperature_u2_inverter": [],
                            "info_soc": [],
                            "current_bms": []
                        }),
                    ],
                    style={'width': '65%', 'paddingRight': '20px'}
                ),

                # Rechte Spalte für Temperatur und Zusatzinfo
                html.Div(
                    children=[
                        dcc.Graph(id='temp-graph', figure=temp_graph_fig,
                                 style={'height': '400px', 'borderRadius': '15px'}),
                        dcc.Graph(id='soc-graph', figure=voltage_soc_fig,
                                 style={'height': '300px', 'borderRadius': '15px', 'marginTop': '20px'}),
                    ],
                    style={'width': '35%'}
                )
            ],
            style={'display': 'flex', 'gap': '20px'}
        ),

        # Status-Anzeigen
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
    
    for key in data.keys():
        if key == "time":
            data[key].append(time_stamp)
        else:
            # Wende Faktor und Offset aus CSV-Definitionen an
            raw_value = new_data.get(key, 0)
            processed_value = raw_value * 0.1 if key == "speed" else raw_value  # Beispiel für Speed-Konversion
            data[key].append(processed_value)
    
    for key in data:
        data[key] = data[key][-100:]
    
    return data

# Speed Graph Update
@app.callback(
    Output('speed-graph', 'figure'),
    Input('data-store', 'data')
)
def update_speed_graph(data):
    fig = px.line(
        x=data["time"][-20:],
        y=data["speed"][-20:],
        title="Geschwindigkeit",
        labels={"x": "Zeit", "y": "km/h"},
        color_discrete_sequence=['#00ff00']
    )
    fig.update_layout(
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        font_color="white",
        xaxis_tickformat='%H:%M:%S',
        showlegend=False
    )
    return fig

# Andere Graphen
@app.callback(
    Output('throttle-brake-graph', 'figure'),
    Output('inverter-graph', 'figure'),
    Output('temp-graph', 'figure'),
    Output('soc-graph', 'figure'),
    Input('data-store', 'data')
)
def update_secondary_graphs(data):
    time = data["time"][-20:]
    
    # Throttle/Brake Graph
    throttle_fig = px.line(
        x=time,
        y=[data["driver_input_brake"][-20:], data["driver_input_demanded_throttle"][-20:]],
        title="Bremsen/Gaspedal",
        labels={"x": "Zeit", "y": "%"},
        color_discrete_sequence=['red', 'green']
    )
    
    # Inverter Graph
    inverter_fig = px.line(
        x=time,
        y=[data["voltage_left_inverter"][-20:], data["voltage_right_inverter"][-20:]],
        title="Inverter-Spannungen",
        labels={"x": "Zeit", "y": "V"},
        color_discrete_sequence=['blue', 'orange']
    )
    
    # Temperatur Graph
    temp_fig = px.line(
        x=time,
        y=[data["temperature_u1_motor"][-20:], 
         data["temperature_u1_inverter"][-20:],
         data["temperature_highest_bms"][-20:]],
        title="Temperaturen",
        labels={"x": "Zeit", "y": "°C"},
        color_discrete_sequence=['#ff00ff', '#00ffff', '#ffff00']
    )
    
    # SOC Graph
    soc_fig = px.line(
        x=time,
        y=data["info_soc"][-20:],
        title="Ladezustand (SOC)",
        labels={"x": "Zeit", "y": "%"},
        color_discrete_sequence=['#00ff00']
    )
    
    for fig in [throttle_fig, inverter_fig, temp_fig, soc_fig]:
        fig.update_layout(
            plot_bgcolor="#2a2a2a",
            paper_bgcolor="#2a2a2a",
            font_color="white",
            xaxis_tickformat='%H:%M:%S'
        )
    
    return throttle_fig, inverter_fig, temp_fig, soc_fig

# Status-Indikatoren
@app.callback(
    [Output(f'speed-text', 'figure'),
     Output(f'motor-temp-text', 'figure'),
     Output(f'inverter-temp-text', 'figure'),
     Output(f'soc-text', 'figure')],
    Input('data-store', 'data')
)
def update_indicators(data):
    indicators = [
        ('speed', 'Geschwindigkeit', 'km/h', '#00ff00'),
        ('temperature_u1_motor', 'Motor Temperatur', '°C', '#ff6600'),
        ('temperature_u1_inverter', 'Inverter Temperatur', '°C', '#ff00ff'),
        ('info_soc', 'Ladezustand', '%', '#00ffff')
    ]
    
    figs = []
    for key, title, unit, color in indicators:
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=data[key][-1] if data[key] else 0,
            number={"suffix": f" {unit}", "font": {"color": color, "size": 40}},
            title={"text": title, "font": {"color": "white", "size": 16}},
            delta={'reference': data[key][-2] if len(data[key]) > 1 else 0}
        ))
        fig.update_layout(plot_bgcolor="#2a2a2a", paper_bgcolor="#2a2a2a")
        figs.append(fig)
    
    return tuple(figs)

# LEDs bleiben gleich wie vorher

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
