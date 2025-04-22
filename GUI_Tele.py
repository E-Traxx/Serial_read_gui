import dash
from dash import html, dcc,callback,Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import random, requests




API_URL = "http://127.0.0.1:8024/incoming_data"




app = dash.Dash(__name__)

#LAYOUT beginnt hier

graph_1_fig = go.Figure()        
graph_2_fig = go.Figure()       
graph_3_fig = go.Figure()      
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
                "position": "absolute",                         
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

        # interval und Store für die LEDs
        dcc.Interval(id='interval-component_led', interval=1000, n_intervals=0),
        html.Div(
            children=[
            
                html.Div(
                    children=[
                        dcc.Graph(id='graph-1', figure=graph_1_fig,
                                  style={'width': '100%', 'height': '330px','overflow': 'hidden','borderRadius': '15px'}),
                        dcc.Graph(id='graph-2', figure=graph_2_fig,
                                  style={'width': '100%', 'height': '330px','overflow': 'hidden','borderRadius': '15px'}),
                        dcc.Graph(id='graph-3', figure=graph_3_fig,
                                  style={'width': '100%', 'height': '330px','overflow': 'hidden','borderRadius': '15px'}),
                        dcc.Interval(id='interval-component', interval=1000, n_intervals=0),

                        dcc.Store(id='speed_power-store', data={"time": [], "speed": [],"current":[],"power":[],"ACCEL":[],"BRAKE":[]}),
                    ],
                    style={
                        'display': 'flex',
                        'flexDirection': 'column',
                        'gap': '10px',
                        'width': '100%',
                        "width": "500px",
                         }

                ),
                # großer Graph oben, 4 kleine Graphen darunter
                html.Div(
                    children=[
                        dcc.Graph(id='big-graph', figure=big_graph_fig,
                                  style={'width': '100%', 'height': '500px',"width": "500px",'overflow': 'hidden','borderRadius': '15px'}), 
                        dcc.Interval(id='interval-component_big', interval=1000, n_intervals=0),
                        dcc.Store(id='temp-store', data={"time": [], "temperature_battery": [],"temperature_inverter": [],"temperature_motor": [],}),
        
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
                        dcc.Store(id='suspension-store', data={"time": [], "FL": [],"FR":[],"RR":[],"RL":[]})         #hier muessen noch die speicher geändert werden
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
                dcc.Store(id='gyro-store', data={"x_gyro": [], "y_gyro": []}),
                dcc.Interval(id='interval-component_gyro', interval=300, n_intervals=0),

                html.Img(
                    src="https://media.tenor.com/qgrHA6RFg4EAAAAM/electric-fan-wind.gif",
                    style={
                      'width': '250px',
                      'height': '150px',
                      'position': 'absolute',
                      'top': '430px',
                      'right':'50px'
                    }
                ),

              # # Batterie
              # dcc.Graph(
              #     id='battery-charge',
              #     figure=go.Layout(),
              #     style={
              #         'width': '200px',
              #         'height': '150px',
              #         'position': 'absolute',
              #         'top': '400px',
              #         'right':'140px'
              #     }
              # ),
               dcc.Interval(id='interval-component_battery', interval=4000, n_intervals=0),
               dcc.Store(id='battery-store', data={"battery_status":[]}),

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
                dcc.Interval(id='interval-component_soc', interval=1000, n_intervals=0),
                dcc.Store(id = 'soc-store', data = {"time":[],"soc_1":[], "soc_2":[]})
                
            ],
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'position': 'absolute',
                'right': '20px',
                'top': '100px',
                'gap': '20px'  
            }
        ),
    html.Div(
    children=[       
        dcc.Interval(id='speed_text_figure', interval=1000, n_intervals=0), 
        dcc.Store(id = 'little_windows_store',data = {"signal":[]}),                                                          
        dcc.Graph(
            id='speed_text',
            style={'width': '224px', 'height': '230px', 'borderRadius': '15px', 'overflow': 'hidden'}
        ),
        dcc.Graph(
            id='temp_motor',
            style={'width': '224px', 'height': '230px', 'borderRadius': '15px', 'overflow': 'hidden'}
        ),
        dcc.Graph(
            id='temp_inver',
            style={'width': '224px', 'height': '230px', 'borderRadius': '15px', 'overflow': 'hidden'}
        ),
        dcc.Graph(
            id='charge_of_battery',
            style={'width': '224px', 'height': '230px', 'borderRadius': '15px', 'overflow': 'hidden'}
        ),
        dcc.Graph(
            id='temp_batt',
            style={'width': '224px', 'height': '230px', 'borderRadius': '15px', 'overflow': 'hidden'}
        ),
        dcc.Graph(
            id='small-graph-47',
            style={'width': '224px', 'height': '230px', 'borderRadius': '15px', 'overflow': 'hidden'}
        )
    ],
    style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(6, 1fr)',
        'gap': '5px',
        'marginTop': '20px',
        'width': '500px'  # Container-Breite festlegen
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

def fetch_data():
    response = requests.get(API_URL)
    if response.ok:
        data = response.json()
        print("Empfangene Daten:", data)

    return data


#LAYOUT ENDET HIER


@app.callback(

    Output('speed_power-store', 'data'),
    Output('temp-store', 'data'),
    Output('soc-store', 'data'),       
    Output('gyro-store', 'data'),
    Output('suspension-store','data'),
    Output('battery-store','data'),
    Input('interval-component', 'n_intervals'),
    State('speed_power-store', 'data'),
    State('temp-store', 'data'),
    State('soc-store', 'data'),        
    State('gyro-store', 'data'),
    State('suspension-store', 'data'), 
    State('battery-store', 'data'),                                 
)

def update_store(n, speed_power_data, temp_data, soc_data, gyro_data, sus_data, battery_data):
    time = pd.Timestamp.now().isoformat()
    
    speed_power_data = update_speed_power_store(speed_power_data, time)
    temp_data = update_temp_store(temp_data, time)
    soc_data = update_soc_store(soc_data, time)
    gyro_data = update_gyro_store(gyro_data)
    sus_data = update_suspension_store(sus_data, time)
    battery_data = battery_store(battery_data,time)

    return speed_power_data, temp_data, soc_data, gyro_data, sus_data, battery_data



def update_speed_power_store(data, time):           
    data_read = fetch_data()     

    data['time'].append(time)
    data['speed'].append(data_read.get('apps_speed',0))
    data['power'].append(data_read.get('power',0))
    data['current'].append(data_read.get('current_sensor',0))
    data['ACCEL'].append(data_read.get('apps_accel',0))
    data['BRAKE'].append(data_read.get('brake',0))


    return limit_data(data, 100)

def update_temp_store(data, time):
    data_read = fetch_data() 

    data['time'].append(time)
    data['temperature_battery'].append(data_read.get('temperature_battery', 0))
    data['temperature_inverter'].append(data_read.get('temperature_inverter', 0))
    data['temperature_motor'].append(data_read.get('temperature_motor', 0))

    return limit_data(data, 100)

def update_soc_store(data, time):
    data_read = fetch_data() 

    data['time'].append(time)
    data['soc_1'].append(data_read.get('soc1', 0))
    data['soc_2'].append(data_read.get('soc2', 0))

    return limit_data(data, 100)

def update_gyro_store(data):
    data_read = fetch_data()

    data['x_gyro'].append(data_read.get('x_gyro',0))
    data['y_gyro'].append(data_read.get('y_gyro',0))

    return data

def update_suspension_store(data, time):         
    data_read = fetch_data() 

    data['time'].append(time)
    data['FL'].append(data_read.get('suspension_fl',0))
    data['RR'].append(data_read.get('suspension_rr',0))
    data['FR'].append(data_read.get('suspension_fr',0))
    data['RL'].append(data_read.get('suspension_rl',0))

    return limit_data(data, 100)

def battery_store(data,time):
    data_read = fetch_data()

    data['battery_status'].append(data_read.get('battery_status',0))


    return data
    

def limit_data(data, max_points):

    for key in data:
        data[key] = data[key][-max_points:]
    return data


@app.callback(
    Output('speed_text','figure'),
    Output('temp_motor','figure'),
    Output('temp_inver','figure'),
    Output('temp_batt','figure'),
    Output('charge_of_battery','figure'),
    Output('small-graph-47','figure'),
    Input('speed_text_figure','n_intervals'),
    State('speed_power-store', 'data'),
    State('temp-store', 'data'),
    State('battery-store','data')
)

def show_current_speed(n, speed_power_data, temp_data, battery_data):

    data = fetch_data()
    
    # Hole aktuelle Werte (keine Listen!)
    current_speed = data.get('apps_speed', 0)
    current_temp_battery = data.get('temperature_battery', 0)
    current_temp_motor = data.get('temperature_motor', 0)
    current_temp_inverter = data.get('temperature_inverter', 0)
    current_charge_battery = data.get('battery_status',0)
    signal = data.get('signal',0)
    signal_value = int(signal)

    speed_text = go.Figure(go.Indicator(
        mode="number",
        value=current_speed,
        number={"font": {"color": "cyan", "size": 50}},
        title={"text": "Speed (km/h)", "font": {"color": "white", "size": 20}}
    ))
    speed_text.update_layout(
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
    )
    
    # Motor Temperatur-Indikator
    temp_motor_text = go.Figure(go.Indicator(
        mode="number",
        value=current_temp_motor,
        number={"font": {"color": "orange", "size": 50}},
        title={"text": "Motor in °C", "font": {"color": "white", "size": 20}}
    ))
    temp_motor_text.update_layout(
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
    )
    
    # Inverter Temperatur-Indikator
    temp_inverter_text = go.Figure(go.Indicator(
        mode="number",
        value=current_temp_inverter,
        number={"font": {"color": "magenta", "size": 50}},
        title={"text": "Inverter in °C", "font": {"color": "white", "size": 20}}
    ))
    temp_inverter_text.update_layout(
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
    )


    #TEMP battery
    temp_battery_text = go.Figure(go.Indicator(
        mode="number",
        value=  current_charge_battery,
        number={"font": {"color": "red", "size": 50}},
        title={"text": "Charge %", "font": {"color": "white", "size": 20}}
    ))
    temp_battery_text.update_layout(
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
    )
    
    #battery
    battery_charge_text = go.Figure(go.Indicator(
        mode="number",
        value=current_temp_battery,
        number={"font": {"color": "green", "size": 50}},
        title={"text": "Battery in °C", "font": {"color": "white", "size": 20}}
    ))
    battery_charge_text.update_layout(
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
    )
    current_signal = go.Figure(go.Indicator(
        mode="number",
        value=signal_value,
        number={"font": {"color": "white", "size": 50}},
        title={"text": "signal: ", "font": {"color": "white", "size": 20}}
     ))
    current_signal.update_layout(
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
     )


    return speed_text, temp_motor_text, temp_inverter_text, temp_battery_text, battery_charge_text, current_signal

#app.callback(
#   Output('battery-charge','figure'),
#   Input('interval-component_battery','n_intervals'),
#   Input('battery-store','data')
#
#
#ef battery_charge_status(n,data): 
#
#   status = data['battery_status'][-1]
#   battery_layout = go.Layout(
#   shapes=[
#       dict(
#               type="rect",
#               xref="paper",
#               yref="paper",
#               x0=0.2,
#               y0=0.4,
#               x1=0.8,
#               y1=0.6,
#               line=dict(color="white", width=2),
#               fillcolor="rgba(0,0,0,0)"
#           ),
#       
#           dict(
#               type="rect",
#               xref="paper",
#               yref="paper",
#               x0=0.21,    
#               y0=0.41,
#               x1=status,                      #akku
#               y1=0.59,
#               fillcolor="limegreen"
#           )
#   ],
#   xaxis=dict(
#       showgrid=False,
#       range=[0, 1],
#       zeroline=False,
#       visible=False
#   ),
#   yaxis=dict(
#       showgrid=False,
#       range=[0, 1],
#       zeroline=False,
#       visible=False
#   ),
#   margin=dict(l=0, r=0, t=0, b=0),
#   height=300,
#   width=400,
#   plot_bgcolor="rgba(0,0,0,0)",
#   paper_bgcolor="rgba(0,0,0,0)"
#   )
#   return go.Figure(layout=battery_layout)

@app.callback(                                                                        
    Output('graph-1', 'figure'),
    Output('graph-2', 'figure'),
    Output('graph-3', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('speed_power-store', 'data')
)

def update_graph_1_2_3(n,data):  
                                              
    x = data["time"][-10:]
    speed = data["speed"][-10:]
    ACCEL = data["ACCEL"][-10:]
    BRAKE = data["BRAKE"][-10:]
    power = data["power"][-10:]
    current = data["current"][-10:]

    fig_1 = go.Figure()
    fig_1.add_trace(go.Scatter(x=x, y=speed, mode='lines+markers',name = 'Speed'))
    fig_1.update_layout(
        xaxis_title="Zeit",
        yaxis_title="Geschwindigkeit (km/h)",
        font=dict(size=10,color='white'),    
        margin=dict(l=20, r=20, t=30, b=20),  # Rand einstellen
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white')),
        
        legend=dict(
        orientation="h",     
        yanchor="bottom",
        y=1.02,              
        xanchor="right",
        x=1,
        font=dict(size=10,color='white')   # Schriftgröße ändern
    )
    )
    fig_1.update_xaxes(tickformat='%H:%M:%S')

   
    fig_2 = go.Figure()
    fig_2.add_trace(go.Scatter(x=x, y=current, mode='lines+markers',name = 'current [V]'))

    fig_2.add_trace(go.Scatter(x=x, y=power, mode='lines',name= 'Leistung [W]'))

    fig_2.update_layout(
        font=dict(size=10,color='white'), 
        xaxis_title="Zeit",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),),
        yaxis=dict(tickfont=dict(color='white'),),
        legend=dict(
        orientation="h",     
        yanchor="bottom",
        y=1.02,              
        xanchor="right",
        x=1,
        font=dict(size=13,color='white')  
    )
    )
    fig_2.update_xaxes(tickformat='%H:%M:%S')

    fig_3 = go.Figure()
    fig_3.add_traces(go.Scatter(x=x, y=BRAKE, mode='lines', name='BRAKE[]'))

    fig_3.add_traces(go.Scatter(x=x, y=ACCEL, mode='lines', name='ACCEL[]'))

    fig_3.update_layout(
        font=dict(size=10,color='white'), 
        xaxis_title="Zeit",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),),
        yaxis=dict(tickfont=dict(color='white'),),

        legend=dict(
        orientation="h",     
        yanchor="bottom",
        y=1.02,              #
        xanchor="right",
        x=1,
        font=dict(size=13,color='white')
           
    )
    )
    fig_3.update_xaxes(tickformat='%H:%M:%S')


    return fig_1,fig_2,fig_3

@app.callback(
    Output('small-graph-1', 'figure'),
    Output('small-graph-2', 'figure'),
    Output('small-graph-3', 'figure'),
    Output('small-graph-4', 'figure'),
    Input('interval-component_small', 'n_intervals'),
    Input('suspension-store', 'data')
)

def update_sus_graphs(n,data):
    x = data["time"][-15:]
    RL = data["RL"][-15:]
    FR = data["FR"][-15:]
    RR = data["RR"][-15:]
    FL = data["FL"][-15:]


    fig_4 = go.Figure()
    fig_4.add_trace(go.Scatter(x=x, y=FL, mode='lines+markers',name = 'FL'))
   
    fig_4.update_layout(  
        font=dict(size=10,color='white'),   
        xaxis_title="time", 
        yaxis_title= "% of ...",
        margin=dict(l=20, r=20, t=30, b=20),  # Rand einstellen
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )
    fig_4.update_xaxes(tickformat='%H:%M:%S')

   
    fig_5 = go.Figure()
    fig_5.add_trace(go.Scatter(x=x, y=FR,  mode='lines', name='FR'))
    fig_5.update_layout(
        font=dict(size=10,color='white'), 
        xaxis_title="Zeit",
        yaxis_title= "in %",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )
    fig_5.update_xaxes(tickformat='%H:%M:%S')


    fig_6 = go.Figure()
    fig_6.add_traces(go.Scatter(x=x, y=RR, mode='lines', name='RR'))
    fig_6.update_layout(
        font=dict(size=10,color='white'), 
        xaxis_title="time",
        yaxis_title= "in %",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )
    fig_6.update_xaxes(tickformat='%H:%M:%S')


    fig_7 = go.Figure()
    fig_7.add_traces(go.Scatter(x=x, y=RL, mode='lines', name='RL'))
    fig_7.update_layout(
        font=dict(size=10,color='white'), 
        xaxis_title="time",
        yaxis_title= "in %",
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor="#2a2a2a",
        paper_bgcolor="#2a2a2a",
        xaxis=dict(tickfont=dict(color='white'),tickformat='%S'),
        yaxis=dict(tickfont=dict(color='white'),) 
    )
    fig_7.update_xaxes(tickformat='%H:%M:%S')

    return fig_4, fig_5, fig_6, fig_7


@app.callback(
        Output('big-graph','figure'),
        Input('interval-component_big', 'n_intervals'),
        Input('temp-store', 'data')
    )

def update_temp_graph(n,data):

    x = data["time"][-15:]
    temp_battery = data["temperature_battery"][-15:]
    temp_inverter = data["temperature_inverter"][-15:]
    temp_motor = data["temperature_motor"][-15:]


    big_fig = go.Figure()
    big_fig.add_traces(go.Scatter(x=x, y=temp_battery, mode='lines+markers',name = 'battery[°C]'))
    big_fig.add_traces(go.Scatter(x=x, y=temp_inverter, mode='lines+markers', name = 'inverter[°C]'))
    big_fig.add_traces(go.Scatter(x=x, y=temp_motor, mode='lines+markers', name = 'motor[°C]'))
    big_fig.update_xaxes(tickformat='%H:%M:%S')
    big_fig.update_layout(
    font=dict(size=10,color='white'), 
    xaxis_title="Zeit",
    margin=dict(l=20, r=20, t=30, b=20),
    plot_bgcolor="#2a2a2a",
    paper_bgcolor="#2a2a2a",
    xaxis=dict(tickfont=dict(color='white'),),
    yaxis=dict(tickfont=dict(color='white'),),
     legend=dict(
        orientation="h",     
        yanchor="bottom",
        y=1.02,              
        xanchor="right",
        x=1,
        font=dict(size=15,color='white')
    )
    )

    return big_fig

@app.callback(
        Output('voltage_soc_fig','figure'),
        Input('interval-component_soc', 'n_intervals'),
        Input('soc-store', 'data')
    )    

def update_soc(n,data):

    x= data["time"][-25:]
    soc_1 = data["soc_1"][-25:]
    soc_2 = data["soc_2"][-25:]

    fig_soc = go.Figure() 

    fig_soc.add_traces(go.Scatter(x=x, y=soc_1, mode='lines+markers', name = 'soce_1[V]'))

    fig_soc.add_traces(go.Scatter(x=x, y=soc_2, mode='lines+markers',name = 'soc_2[V]'))

    fig_soc.update_layout(
    font=dict(size=10,color='white'), 
    xaxis_title="Zeit",
    margin=dict(l=20, r=20, t=30, b=20),
    plot_bgcolor="#2a2a2a",
    paper_bgcolor="#2a2a2a",
    xaxis=dict(tickfont=dict(color='white'),),
    yaxis=dict(tickfont=dict(color='white'),),

    legend=dict(
        orientation="h",     
        yanchor="bottom",
        y=1.02,              
        xanchor="right",
        x=1,
        font=dict(size=15,color='white')
    )
    )
    fig_soc.update_xaxes(tickformat='%H:%M:%S')

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
        font=dict(size=10,color='white'), 

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
    Input('interval-component_led', 'n_intervals'), 
)
def update_led(n):
    data = fetch_data()  # Direkt Daten abrufen
    
    # Hole die Fehlerwerte direkt aus den Daten
    error_list = [
        data.get("error_temperature_battery", 0),  # Battery-Temperaturfehler
        data.get("error_temperature_inverter", 0), # Inverter-Temperaturfehler
        data.get("error_temperature_motor", 0),    # Motor-Temperaturfehler
        data.get("error_soc", 0),                  # SOC-Fehler
        data.get("error_current", 0),              # Stromfehler
        data.get("bspd", 0),                       # BSPD-Fehler (Schreibweise beachten!)
        data.get("error_voltage", 0),              # Spannungsfehler
        data.get("error_undervoltage", 0),         # Unterspannungsfehler
        data.get("error_undervoltage", 0)          # Platzhalter oder zusätzlicher Fehler
    ]

    styles = []
    for error in error_list:
        led_style = {
            "backgroundColor": "red" if error == 0 else "#00ff00",
            "width": "30px",
            "height": "30px",
            "borderRadius": "50%",
            "boxShadow": "0 0 20px rgba(255, 0, 0, 0.8)" if error == 0 else "0 0 15px rgba(0, 255, 0, 0.5)"
        }
        styles.append(led_style)
    
    return styles
    
if __name__ == "__main__":
    app.run_server(debug=True)