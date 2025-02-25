import dash
from dash import html, dcc,callback,Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import random

app = dash.Dash(__name__)



graph_1_fig = go.Figure()         # speed 
graph_2_fig = go.Figure()       # current und Leistung
graph_3_fig = go.Figure()      # Apps, Accel., brake
big_graph_fig = go.Figure()
small_graph_1_fig = go.Figure()
small_graph_2_fig = go.Figure()
small_graph_3_fig = go.Figure()
small_graph_4_fig =go.Figure()
voltage_soc_fig = go.Figure()

app.layout = html.Div(

    children=[
   
            html.Div(
    children=[
        html.Div(
            f"{i}",
            style={
                "position": "absolute",                         # durch absolute lassen sich die dinger bewegen
                "top": "50px",
                "left": f"{100 + (i-1)*150}px",                 #   ok?
                "fontSize": "18px"
            }
        )
        for i in range(1, 10)
    ]
),           
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
                )
                for i in range(1, 10)  # Erstellt 9 LEDs
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(9, 1fr)",
                "gap": "20px",
                "margin": "20px 0",
                "padding": "10px",
                "background": "#2a2a2a",
                "borderRadius": "15px",
                "justifyContent": "center"
            }
        ),

        # Interval und Store für die LEDs
        dcc.Interval(id='interval-component_led', interval=5000, n_intervals=0),
        html.Div(
            children=[
                # (Links) 3 kleine Graphen
                html.Div(
                    children=[
                        dcc.Graph(id='graph-1', figure=graph_1_fig,
                                  style={'width': '100%', 'height': '330px','overflow': 'hidden','borderRadius': '15px'}),
                        dcc.Graph(id='graph-2', figure=graph_2_fig,
                                  style={'width': '100%', 'height': '330px','overflow': 'hidden','borderRadius': '15px'}),
                        dcc.Graph(id='graph-3', figure=graph_3_fig,
                                  style={'width': '100%', 'height': '330px','overflow': 'hidden','borderRadius': '15px'}),
                        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),

                        dcc.Store(id='speed-store', data={"time": [], "speed": [],"current":[],"power":[]}, storage_type='local'),
                        dcc.Store(id='voltage_store', data={"time": [], "voltage": []}, storage_type='local')
                    ],
                    style={
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '10px',
                        'width': '100%',
                        "width": "500px",
                         }

                ),
                # (Rechts) großer Graph oben, 4 kleine Graphen darunter
                html.Div(
                    children=[
                        dcc.Graph(id='big-graph', figure=big_graph_fig,
                                  style={'width': '100%', 'height': '500px',"width": "500px",'overflow': 'hidden','borderRadius': '15px'}), 
                        dcc.Interval(id='interval-component_big', interval=800, n_intervals=0),
                        dcc.Store(id='temp-store', data={"time": [], "temperature": []}, storage_type='local'),
        
                        html.Div(
                            children=[                                                                  
                                dcc.Graph(id='small-graph-1', figure=small_graph_1_fig,                         #die 4 kleinen Figs
                                          style={'width': '100%', 'height': '230px',"width": "240px",'borderRadius': '15px','overflow': 'hidden',}),
                                dcc.Graph(id='small-graph-2', figure=small_graph_2_fig,
                                          style={'width': '100%', 'height': '230px',"width": "240px",'borderRadius': '15px','overflow': 'hidden',}),
                                dcc.Graph(id='small-graph-3', figure=small_graph_3_fig,
                                         style={'width': '100%', 'height': '230px',"width": "240px",'borderRadius': '15px','overflow': 'hidden',}),
                                dcc.Graph(id='small-graph-4', figure=small_graph_4_fig,
                                          style={'width': '100%', 'height': '230px',"width": "240px",'borderRadius': '15px','overflow': 'hidden',}),
                            ],
                            style={
                                'display': 'grid',
                                'gridTemplateColumns': 'repeat(2, 1fr)',
                                'gap': '5px',
                                'marginTop': '20px',
                                
                            }
                        ),
                        dcc.Interval(id='interval-component_small', interval=2000, n_intervals=0),
                        dcc.Store(id='power-store', data={"time": [], "speed": [],"current":[],"power":[],}, storage_type='local')         #hier muessen noch die speicher geändert werden
                    ],
                    style={'paddingLeft': '20px'}
                )
            ],
            style={
                'display': 'grid',
                'gridTemplateColumns': '1fr 1.5fr',
                'width': '66%',
                'gap': '2px',
             
            }),
        # Gyro-Display, Batterie
       html.Div(
    children=[
        html.Div(
            children=[
                # Logo
                html.Img(
                    src="https://e-traxx.eu/wp-content/uploads/2024/02/E-Traxx_Logo_rot_schwarze_Schrift-e1707594241497.png",
                    style={'width': '200px', 'margin': '10px auto'}
                ),

                # Gyro
                dcc.Graph(
                    id='gyro-display',
                    figure=go.Figure(),
                    style={
                        'width': '300px',
                        'height': '300px',
                        'backgroundColor': '#2a2a2a',
                        'margin': '10px auto',
                        'borderRadius': '15px',
                        'overflow': 'hidden',   
                        'boxShadow': '0 4px 20px rgba(0,0,0,0.3)'
                    
                    }
                ),
                dcc.Store(id='gyro-store', data={"x_gyro": [], "y_gyro": []}, storage_type='local'),
                dcc.Interval(id='interval-component_gyro', interval=300, n_intervals=0),

                # Batterie
                dcc.Graph(
                    id='battery-charge',
                    figure=go.Layout(),
                    style={
                        'width': '200px',
                        'height': '150px',
                        'position': 'absolute',
                        'top': '400px',
                        'right':'140px'
                    }
                ),
                dcc.Interval(id='interval-component_battery', interval=4000, n_intervals=0),

                # Voltage Graph
                dcc.Graph(
                    id='voltage_soc_fig',
                    figure=voltage_soc_fig,
                    style={
                        'width': '330px',
                        'height': '400px',
                        'position': 'absolute',
                        'top': '590px',
                        'borderRadius': '15px',
                        'overflow': 'hidden',
                    }
                ),
                dcc.Interval(id='interval-component_soc', interval=1000, n_intervals=0)
                
            ],
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'position': 'absolute',
                'right': '20px',
                'top': '100px',
                'gap': '20px'  # Abstand zwischen Elementen
            }
        )
    ]
)
    ],
    style={
        "backgroundColor": "grey",
        "color": "white",
        "minHeight": "100vh",
        "padding": "20px",
        "position": "relative"
    }
)


@app.callback(

    Output('speed-store', 'data'),
    Output('temp-store', 'data'),
    Output('voltage_store', 'data'),
    Output('gyro-store', 'data'),
    Output('power-store','data'),
    Input('interval-component', 'n_intervals'),                     # trigger bei einem reicht aus beim callback 
    State('speed-store', 'data'),
    State('temp-store', 'data'),
    State('voltage_store', 'data'),
    State('gyro-store', 'data'),
    State('power-store', 'data'),                                   # muss noch anpassen 2 grapghen benutzen gleiche daten
)

def update_store(n, speed_data, temp_data, voltage_data, gyro_data, power_data):    

    new_time = pd.Timestamp.now().isoformat()
    speed_data = update_speed_store(speed_data, new_time)
    temp_data = update_temp_store(temp_data, new_time)
    voltage_data = update_voltage_store(voltage_data, new_time)
    gyro_data = update_gyro_store(gyro_data, new_time)
    power_data = update_power_store(power_data, new_time)
    
    return speed_data, temp_data, voltage_data, gyro_data, power_data

def update_speed_store(data, time):

    data['time'].append(time)
    data['speed'].append(random.uniform(0, 100))
    data['current'].append(random.uniform(-50, 50))
    data['power'].append(random.randint(0, 1000))

    return limit_data(data, 100)

def update_temp_store(data, time):

    data['time'].append(time)
    data['temperature'].append(random.uniform(30, 70))
    return limit_data(data, 100)

def update_voltage_store(data, time):

    data['time'].append(time)
    data['voltage'].append(random.uniform(0, 50))
    return limit_data(data, 100)

def update_gyro_store(data, time):

    data['x_gyro'].append(random.uniform(-1, 1))
    data['y_gyro'].append(random.uniform(-1, 1))
    return limit_data(data, 100)

def update_power_store(data, time):

    data['time'].append(time)
    data['power'].append(random.randint(0, 10))   

    return limit_data(data, 100)
    
def limit_data(data, max_points):

    for key in data:
        data[key] = data[key][-max_points:]
    return data


@app.callback(
    Output('battery-charge','figure'),
    Input('interval-component_battery','n_intervals')

)
def battery_charge_status(n):       
    x1 = random.uniform(0, 1)
    battery_layout = go.Layout(
    shapes=[
        dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0.2,
                y0=0.4,
                x1=0.8,
                y1=0.6,
                line=dict(color="white", width=2),
                fillcolor="rgba(0,0,0,0)"
            ),
            # Inneres Rechteck 
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0.21,    
                y0=0.41,
                x1=x1,
                y1=0.59,
                fillcolor="limegreen"
            )
    ],
    xaxis=dict(
        showgrid=False,
        range=[0, 1],
        zeroline=False,
        visible=False
    ),
    yaxis=dict(
        showgrid=False,
        range=[0, 1],
        zeroline=False,
        visible=False
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=300,
    width=400,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
    )
    return go.Figure(layout=battery_layout)

@app.callback(                                                                        
    Output('graph-1', 'figure'),
    Output('graph-2', 'figure'),
    Output('graph-3', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('speed-store', 'data'),
)

def update_graph_1_2_3(n,data):  
                                              
    x_last = data["time"][-10:]
    y_last = data["speed"][-10:]
    y1_last = data["current"][-10:]

    fig_1 = go.Figure()
    fig_1.add_trace(go.Scatter(x=x_last, y=y_last, mode='lines+markers',name = 'Speed'))
    fig_1.update_layout(
        xaxis_title="Zeit",
        yaxis_title="Geschwindigkeit (km/h)",      
        margin=dict(l=20, r=20, t=30, b=20),  # Rand einstellen
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),),
        yaxis=dict(tickfont=dict(color='white'),)
    )

   
    fig_2 = go.Figure()
    fig_2.add_trace(go.Scatter(x=x_last, y=y1_last, mode='lines+markers',name = 'current [V]'))

    fig_2.add_trace(go.Scatter(x=x_last, y=y_last, mode='lines',name= 'Leistung [W]'))
                            
    fig_2.update_layout(
        xaxis_title="Zeit",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),),
        yaxis=dict(tickfont=dict(color='white'),)
    )

    fig_3 = go.Figure()
    fig_3.add_traces(go.Scatter(x=x_last, y=y_last, 
                               mode='lines', name='Double random_y1'))
    fig_3.update_layout(
        xaxis_title="Zeit",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),),
        yaxis=dict(tickfont=dict(color='white'),)
    )
    return fig_1,fig_2,fig_3

@app.callback(
    Output('small-graph-1', 'figure'),
    Output('small-graph-2', 'figure'),
    Output('small-graph-3', 'figure'),
    Output('small-graph-4', 'figure'),
    Input('interval-component_small', 'n_intervals'),
    State('power-store', 'data')
)

def update_small_graphs(n,data):
    x_vals = data["time"][-25:]
    y_last = data["power"][-25:]
    y1_last = data["power"][-25:]

    fig_4 = go.Figure()
    fig_4.add_trace(go.Scatter(x=x_vals, y=y_last, mode='lines+markers'))
   
    fig_4.update_layout(    
        xaxis_title="Zeit",  
        margin=dict(l=20, r=20, t=30, b=20),  # Rand einstellen
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )

   
    fig_5 = go.Figure()
    fig_5.add_trace(go.Scatter(x=x_vals, y=y_last,  mode='lines', name='Double random_y1'))
    fig_5.update_layout(
        xaxis_title="Zeit",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )

    fig_6 = go.Figure()
    fig_6.add_traces(go.Scatter(x=x_vals, y=y_last, mode='lines', name='Double random_y1'))
    fig_6.update_layout(
        xaxis_title="Zeit",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )

    fig_7 = go.Figure()
    fig_7.add_traces(go.Scatter(x=x_vals, y=y_last, mode='lines', name='Double random_y1'))
    fig_7.update_layout(
        xaxis_title="Zeit",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )

    return fig_4, fig_5, fig_6, fig_7


@app.callback(
        Output('big-graph','figure'),
        Input('interval-component_big', 'n_intervals'),
        Input('temp-store', 'data')
    )

def update_big_graph(n,data):

    x_time = data["time"][-25:]
    y_temp= data["temperature"][-25:]


    big_fig = go.Figure()
    big_fig.add_traces(go.Scatter(x=x_time, y=y_temp, mode='lines+markers'))
    big_fig.update_layout(
    xaxis_title="Zeit",
    margin=dict(l=20, r=20, t=30, b=20),
    plot_bgcolor="#2a2a2a",
    paper_bgcolor="#2a2a2a",
    xaxis=dict(tickfont=dict(color='white'),),
    yaxis=dict(tickfont=dict(color='white'),)
    )

    return big_fig

@app.callback(
        Output('voltage_soc_fig','figure'),
        Input('interval-component_soc', 'n_intervals'),
        Input('voltage_store', 'data')
    )    

def update_soc(n,data):

    x_time = data["time"][-25:]
    y_vol = data["voltage"][-25:]

    fig_soc = go.Figure() 

    fig_soc.add_traces(go.Scatter(x=x_time, y=y_vol, mode='lines+markers'))
    fig_soc.update_layout(
    xaxis_title="Zeit",
    margin=dict(l=20, r=20, t=30, b=20),
    plot_bgcolor="#2a2a2a",
    paper_bgcolor="#2a2a2a",
    xaxis=dict(tickfont=dict(color='white'),),
    yaxis=dict(tickfont=dict(color='white'),)
    )

    return fig_soc

@app.callback(
        Output('gyro-display','figure'),
        Input('interval-component_gyro', 'n_intervals'),
        State('gyro-store', 'data')
    )    


def update_gyro(n,data):

    x = data['x_gyro'][-1] if data['x_gyro'] else 0
    y = data['y_gyro'][-1] if data['y_gyro'] else 0
    
    return go.Figure(
        data=[go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(color='red', size=15)
        )],
        layout=go.Layout(

    xaxis=dict(
        title='Accel X',              
        tickfont=dict(color='white'), 
        showgrid=True,
        gridcolor="gray",
        range=[-1.2, 1.2],  
        zeroline=False,
        
        
    ),
    yaxis=dict(
        title='Accel Y',              
        tickfont=dict(color='white'),
        showgrid=True,
        gridcolor="gray",
        range=[-1.2, 1.2], 
        zeroline=False,
       
    ),
    plot_bgcolor="#2a2a2a",
    paper_bgcolor="#2a2a2a",
    margin=dict(l=20, r=20, t=20, b=20),
    height=300
        )
    )
    return fig_gyro

@app.callback(
    [Output(f'led{i}', 'style') for i in range(1, 10)],
    Input('interval-component_led', 'n_intervals')
)

def update_led_and_store(n_intervals):
    errors = [random.randint(0,1) for _ in range(9)]
  
    base_style = {
        "width": "30px",
        "height": "30px",
        "borderRadius": "50%",
        "boxShadow": "0 0 15px rgb(255, 255, 0)",
        "transition": "all 0.3s ease"
    }
    styles = []
    for i in range(9):
        led_style = base_style.copy()
        if errors[i] == 0:
            led_style["backgroundColor"] = "red"
            led_style["boxShadow"] = "0 0 20px rgba(255, 0, 0, 0.8)"
        else:
            led_style["backgroundColor"] = "#00ff00"
            led_style["boxShadow"] = "0 0 15px rgba(0, 255, 0, 0.5)"
        styles.append(led_style)

    return styles
    
if __name__ == "__main__":
    app.run_server(debug=True)