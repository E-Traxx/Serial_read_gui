import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation
import itertools

df = pd.read_json('logs/telemetry.log', lines=True)


df_Temp_bms = df[df["name"] == "temperature_highest_bms"].copy()
df_Temp_u1_motor = df[df["name"] == "temperature_u1_motor"].copy()

df_Temp_u2_motor = df[df["name"] == "temperature_u2_motor"].copy()
df_Temp_u1_inverter = df[df["name"] == "temperature_u1_inverter"].copy()
df_Temp_u2_inverter = df[df["name"] == "temperature_u2_inverter"].copy()


dfig = plt.figure(figsize=(12, 8))


for dframe in [
    df_Temp_bms,
    df_Temp_u1_motor,
    df_Temp_u2_motor,
    df_Temp_u1_inverter,
    df_Temp_u2_inverter,
]:
    dframe["t"] = pd.to_datetime(dframe["timestamp"], unit='s', utc=True).dt.tz_convert("Europe/Berlin").dt.tz_localize(None)



ax_Temp_bms = plt.subplot2grid((3, 2), (0, 0), colspan=2)
ax_Temp_bms.plot(df_Temp_bms["t"], df_Temp_bms["value"])
ax_Temp_bms.set_title("Temperature BMS [°C]")

ax_Temp_u1_motor = plt.subplot2grid((3, 2), (1, 0))
ax_Temp_u1_motor.plot(df_Temp_u1_motor["t"], df_Temp_u1_motor["value"])
ax_Temp_u1_motor.set_title("Temperature U1 Motor [°C]")

ax_Temp_u2_motor = plt.subplot2grid((3, 2), (1, 1))
ax_Temp_u2_motor.plot(df_Temp_u2_motor["t"], df_Temp_u2_motor["value"])
ax_Temp_u2_motor.set_title("Temperature U2 Motor [°C]")

ax_Temp_u1_inverter = plt.subplot2grid((3, 2), (2, 0))
ax_Temp_u1_inverter.plot(df_Temp_u1_inverter["t"], df_Temp_u1_inverter["value"])
ax_Temp_u1_inverter.set_title("Temperature U1 Inverter [°C]")

ax_Temp_u2_inverter = plt.subplot2grid((3, 2), (2, 1))
ax_Temp_u2_inverter.plot(df_Temp_u2_inverter["t"], df_Temp_u2_inverter["value"])
ax_Temp_u2_inverter.set_title("Temperature U2 Inverter [°C]")


plt.tight_layout()
plt.show()