import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


df = pd.read_json('logs/telemetry.log', lines=True)


df_error_bspd_software = df[df["name"] == "error_bspd_software"].copy()
df_error_can_bus = df[df["name"] == "error_can_bus"].copy()
df_error_general = df[df["name"] == "error_general"].copy()
df_error_imd = df[df["name"] == "error_imd"].copy()
df_error_u2_inverter = df[df["name"] == "error_u2_inverter"].copy()
df_error_latching = df[df["name"] == "error_latching"].copy()
df_error_temperature = df[df["name"] == "error_temperature"].copy()
df_error_undervoltage = df[df["name"] == "error_undervoltage"].copy()
df_bms_error = df[df["name"] == "bms_error"].copy()
df_error_u1_inverter = df[df["name"] == "error_u1_inverter"].copy()




fig,axs = plt.subplots(5, 2, figsize=(10, 8), sharex=True, sharey=True)
for ax in axs.flat:
    ax.set_ylim(-0.1, 1.1)


for dframe in [
    df_error_bspd_software, df_error_can_bus, df_error_imd,
    df_error_u2_inverter, df_error_latching, df_error_temperature, df_error_undervoltage,
    df_bms_error, df_error_u1_inverter
]:
    dframe["t"] = pd.to_datetime(dframe["timestamp"], unit='s',utc = True).dt.tz_convert("Europe/Berlin") .dt.tz_localize(None) 


ax_error_temp = plt.subplot2grid((5, 2), (0, 0), rowspan=1)
ax_error_temp.step(df_error_temperature["t"], df_error_temperature["value"], where="post")
ax_error_temp.set_ylim(-0.1, 1.1)
ax_error_temp.set_title("Error Temperature")

ax_error_can_bus = plt.subplot2grid((5, 2), (1, 0))
ax_error_can_bus.step(df_error_can_bus["t"], df_error_can_bus["value"], where="post")
ax_error_can_bus.set_ylim(-0.1, 1.1)
ax_error_can_bus.set_title("Error CAN Bus")

ax_error_bspd_software = plt.subplot2grid((5, 2), (2, 0))
ax_error_bspd_software.step(df_error_bspd_software["t"], df_error_bspd_software["value"], where="post")
ax_error_bspd_software.set_ylim(-0.1, 1.1)
ax_error_bspd_software.set_title("Error BSPD Software")

ax_error_latching = plt.subplot2grid((5, 2), (3, 0))
ax_error_latching.step(df_error_latching["t"], df_error_latching["value"], where="post")
ax_error_latching.set_ylim(-0.1, 1.1)
ax_error_latching.set_title("Error Latching")

ax_error_imd = plt.subplot2grid((5, 2), (4, 0), colspan=2)
ax_error_imd.step(df_error_imd["t"], df_error_imd["value"], where="post")
ax_error_imd.set_ylim(-0.1, 1.1)
ax_error_imd.set_title("Error IMD")

ax_bms_error = plt.subplot2grid((5, 2), (0, 1))
ax_bms_error.step(df_bms_error["t"], df_bms_error["value"], where="post")
ax_bms_error.set_ylim(-0.1, 1.1)
ax_bms_error.set_title("BMS Error")

ax_error_u2_inverter = plt.subplot2grid((5, 2), (1, 1))
ax_error_u2_inverter.step(df_error_u2_inverter["t"], df_error_u2_inverter["value"], where="post")
ax_error_u2_inverter.set_ylim(-0.1, 1.1)
ax_error_u2_inverter.set_title("Error U2 Inverter")

ax_error_undervoltage = plt.subplot2grid((5, 2), (2, 1))
ax_error_undervoltage.step(df_error_undervoltage["t"], df_error_undervoltage["value"], where="post")
ax_error_undervoltage.set_ylim(-0.1, 1.1)
ax_error_undervoltage.set_title("Error Undervoltage")

ax_error_u1_inverter = plt.subplot2grid((5, 2), (3, 1))
ax_error_u1_inverter.step(df_error_u1_inverter["t"], df_error_u1_inverter["value"], where="post")
ax_error_u1_inverter.set_ylim(-0.1, 1.1)
ax_error_u1_inverter.set_title("Error U1 Inverter")

plt.tight_layout()
plt.show()

