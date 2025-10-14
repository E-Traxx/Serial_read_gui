import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation
import itertools
from collections import deque

window_size = 100

df = pd.read_json('logs/telemetry.log', lines=True)

# Daten vorbereiten
df_speed = df[df["name"] == "speed"].copy()
df_info_soc = df[df["name"] == "info_soc"].copy()
df_info_ing = df[df["name"] == "info_ing"].copy()
df_driver_input_break = df[df["name"] == "driver_input_break"].copy()
df_driver_input_demanded_throttle = df[df["name"] == "driver_input_demanded_throttle"].copy()
df_driver_input_steering_angle = df[df["name"] == "driver_input_steering_angle"].copy()
df_voltage_left_inverter = df[df["name"] == "voltage_left_inverter"].copy()
df_voltage_right_inverter = df[df["name"] == "voltage_right_inverter"].copy()
df_charge_bms = df[df["name"] == "charge_bms"].copy()
df_current_bms = df[df["name"] == "current_bms"].copy()

# Zeitkonvertierung
dfs = [
    df_speed, df_info_soc, df_info_ing, df_voltage_left_inverter,
    df_voltage_right_inverter, df_charge_bms, df_current_bms,
    df_driver_input_break, df_driver_input_demanded_throttle,
    df_driver_input_steering_angle
]

for dframe in dfs:
    if not dframe.empty:
        dframe["t"] = pd.to_datetime(dframe["timestamp"], unit='s', utc=True).dt.tz_convert("Europe/Berlin").dt.tz_localize(None)


def gen_from_df(dframe):
    if dframe is None or dframe.empty:
        # empty generator
        if False:
            yield None  # never reached
        return
    ts = dframe["t"].to_numpy()
    vs = dframe["value"].to_numpy()
    for i in range(len(ts)):
        yield ts[i], vs[i]

fig, axes = plt.subplots(6, 1, figsize=(10, 12),sharex=True)
plt.subplots_adjust(hspace=0.5)

# Konfiguration für jeden Plot
plots = [
    {
        'ax': axes[0],
        'title': 'Speed (km/h)',
        'generator': gen_from_df(df_speed),
        'xdata': deque(),
        'ydata': deque(),
        'line': None,
        'color': 'blue'
    },
    {
        'ax': axes[1],
        'title': 'Battery SOC',
        'generator': gen_from_df(df_info_soc),
        'xdata': deque(),
        'ydata': deque(),
        'line': None,
        'color': 'green'
    },
    {
        'ax': axes[2],
        'title': 'Current (A)',
        'generator': gen_from_df(df_current_bms),
        'xdata': deque(),
        'ydata': deque(),
        'line': None,
        'color': 'purple'
    },
    {
        'ax': axes[3],
        'title': 'Voltage (V)',
        'generator': gen_from_df(df_voltage_left_inverter),
        'xdata': deque(),
        'ydata': deque(),
        'line': None,
        'color': 'orange'
    },
    {
        'ax': axes[4],
        'title': 'Driver Input',
        'generator': gen_from_df(df_driver_input_break),
        'xdata': deque(),
        'ydata': deque(),
        'line': None,
        'color': 'red'
    },
    {
        'ax': axes[5],
        'title': 'Steering Angle',
        'generator': gen_from_df(df_driver_input_steering_angle),
        'xdata': deque(),
        'ydata': deque(),
        'line': None,
        'color': 'olive'
    }
]

# Initialisiere jeden Plot
for plot in plots:
    plot['ax'].set_title(plot['title'])
    plot['ax'].grid(True)
    plot['line'], = plot['ax'].plot([], [], lw=2, color=plot['color'])

# Startzeit für die X-Achse
t0 = df_speed["t"].iloc[0] if not df_speed.empty else pd.Timestamp.now()

def init():
    for plot in plots:
        plot['xdata'].clear()
        plot['ydata'].clear()
        plot['line'].set_data([], [])
        plot['ax'].set_xlim(t0, t0 + pd.Timedelta(seconds=window_size))
        plot['ax'].set_ylim(-1, 1)  # Standard-Y-Limits, werden später angepasst
    return [plot['line'] for plot in plots]

def run(frame):
    lines = []

    # 1) Pull one sample from each generator; track the newest timestamp globally
    current_time = None
    for plot in plots:
        try:
            t, y = next(plot['generator'])
        except StopIteration:
            # this series is finished; skip adding new samples
            continue
        plot['xdata'].append(t)
        plot['ydata'].append(y)
        if (current_time is None) or (t > current_time):
            current_time = t

    if current_time is None:
        # no new data this frame
        return [plot['line'] for plot in plots]

    # 2) Shared cutoff for all plots so time windows stay aligned
    cutoff = current_time - pd.Timedelta(seconds=window_size)

    # prune, update data & y-limits
    for plot in plots:
        # remove points older than the shared cutoff
        while plot['xdata'] and plot['xdata'][0] < cutoff:
            plot['xdata'].popleft()
            plot['ydata'].popleft()

        # update line
        plot['line'].set_data(list(plot['xdata']), list(plot['ydata']))
        lines.append(plot['line'])

        # adapt y-limits softly if we have data
        if plot['ydata']:
            ymin = min(plot['ydata'])
            ymax = max(plot['ydata'])
            pad = (ymax - ymin) * 0.1 if ymax != ymin else 1.0
            plot['ax'].set_ylim(ymin - pad, ymax + pad)

    # 3) Set the same x-limits for all plots (shared time window)
    left = cutoff
    right = current_time
    for p in plots:
        p['ax'].set_xlim(left, right)

    return lines

# Animation starten
ani = animation.FuncAnimation(
    fig, 
    run, 
    init_func=init,
    interval=700, 
    blit=False,
    cache_frame_data=False
)

plt.show()