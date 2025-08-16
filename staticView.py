import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation
import itertools

df = pd.read_json('logs/telemetry.log', lines=True)

df_speed = df[df["name"] == "speed"].copy()
df_info_soc = df[df["name"] == "info_soc"].copy()
df_info_ing = df[df["name"] == "info_ing"].copy()

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

df_driver_input_break = df[df["name"] == "driver_input_break"].copy()
df_driver_input_demanded_throttle = df[df["name"] == "driver_input_demanded_throttle"].copy()
df_driver_input_steering_angle = df[df["name"] == "driver_input_steering_angle"].copy()

df_voltage_left_inverter = df[df["name"] == "voltage_left_inverter"].copy()
df_voltage_right_inverter = df[df["name"] == "voltage_right_inverter"].copy()

df_charge_bms = df[df["name"] == "charge_bms"].copy()
df_current_bms = df[df["name"] == "current_bms"].copy()


dfig = plt.figure(figsize=(12, 8))


for dframe in [
    df_speed, df_info_soc, df_error_temperature, df_voltage_left_inverter, df_voltage_right_inverter,df_charge_bms, df_current_bms, df_driver_input_break,
    df_driver_input_demanded_throttle, df_driver_input_steering_angle, df_error_bspd_software, df_error_can_bus, df_error_general, df_error_imd,
    df_error_u2_inverter, df_error_latching, df_error_undervoltage, df_bms_error, df_error_u1_inverter
]:
    dframe["t"] = pd.to_datetime(dframe["timestamp"], unit='s',utc = True).dt.tz_convert("Europe/Berlin") .dt.tz_localize(None)



ax_speed = plt.subplot2grid((4, 4), (0, 0), colspan=2)
ax_speed.plot(df_speed["t"], df_speed["value"])
ax_speed.set_title("Speed [km/h]")


ax_soc = plt.subplot2grid((4, 4), (1, 0), colspan=2)
ax_soc.plot(df_info_soc["t"], df_info_soc["value"])
ax_soc.set_title("SOC [%]")


ax_err_temp = plt.subplot2grid((4, 4), (2,2), rowspan=1)
ax_err_temp.step(df_error_temperature["t"], df_error_temperature["value"], where="post")
ax_err_temp.set_ylim(-0.1, 1.1)
ax_err_temp.set_title("Error Temperature [0/1]")


ax_volt_l = plt.subplot2grid((4, 4), (2, 0))
ax_volt_l.plot(df_voltage_left_inverter["t"], df_voltage_left_inverter["value"])
ax_volt_l.set_title("Voltage Left Inverter [V]")


ax_volt_r = plt.subplot2grid((4, 4), (2, 1))
ax_volt_r.plot(df_voltage_right_inverter["t"], df_voltage_right_inverter["value"])
ax_volt_r.set_title("Voltage Right Inverter [V]")

ax_charge_bms = plt.subplot2grid((4, 4), (3, 2), colspan=2)
ax_charge_bms.plot(df_charge_bms["t"], df_charge_bms["value"])
ax_charge_bms.set_title("Charge BMS [V]")

ax_current_bms = plt.subplot2grid((4, 4), (3, 0), colspan=2)
ax_current_bms.plot(df_current_bms["t"], df_current_bms["value"])
ax_current_bms.set_title("Current BMS [A]")


ax_breakthrottle = plt.subplot2grid((4, 4), (1, 2), colspan=2)
ax_breakthrottle.plot(df_driver_input_break["t"], df_driver_input_break["value"])
ax_breakthrottle.set_title("Driver Input Break ") #Einheit?

ax_steering = plt.subplot2grid((4, 4), (2, 3), rowspan=1)
ax_steering.plot(df_driver_input_steering_angle["t"], df_driver_input_steering_angle["value"])
ax_steering.set_title("Driver Input Steering Angle [rad]")

ax_demanded_throttle = plt.subplot2grid((4, 4), (0,2), colspan=2)
ax_demanded_throttle.plot(df_driver_input_demanded_throttle["t"], df_driver_input_demanded_throttle["value"])
ax_demanded_throttle.set_title("Driver Input Demanded Throttle [%]")

plt.tight_layout()
plt.show()