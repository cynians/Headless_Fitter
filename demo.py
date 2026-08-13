from pathlib import Path

from headless_fitter import fit_loud, fit_quiet, fit_silent, load_name_list
from xls_to_list import xls_to_list


# Chapter 1: list definition

project_directory = Path(__file__).resolve().parent
reference_directory = project_directory / "reference"
list_a = load_name_list(reference_directory / "source_names.yaml")
list_b = load_name_list(reference_directory / "target_names.json")

# Both reference lists contain 30 flight time-series terms.


# Chapter 2: fit_loud

loud_result = fit_loud(list_a, list_b)

# Result: 24 one-to-one matches
#
# List A term                  List B term                         Score  Method
# ---------------------------  ----------------------------------  -----  -----------------
# baro_alt                     Barometric Altitude                    79  partial_token
# static_pressure_corr         Corrected Static Pressure              90  token_and_partial
# total_air_temp               Total Air Temperature                  89  token_and_partial
# vert_accel                   Acceleration Vertical                  79  partial_token
# indicated_airspeed           Airspeed Indicated                     96  token_reorder
# eng_1_rpm                    Engine 1 RPM                            89  token_and_partial
# fuel_flow_left               Left Engine Fuel Flow                  88  token_overlap
# oil_press_no_2               Engine 2 Oil Pressure                  65  token_and_partial
# exhaust_gas_temp             Exhaust Gas Temperature                89  token_and_partial
# angle_attack                 Aircraft Angle of Attack               82  token_overlap
# pitch_rate_deg_s             Pitch Angular Rate Degrees Second      63  token_and_partial
# roll_rate                    Aircraft Roll Rate                     85  token_overlap
# yaw_rate                     Rate of Yaw                            87  token_overlap
# gps_lat                      GPS Latitude Degrees                   79  token_and_partial
# gps_lon                      Longitude GPS Degrees                  78  token_and_partial
# wind_spd                     Wind Speed                             48  token_overlap
# wind_dir                     Wind Direction                         86  token_and_partial
# outside_air_temp             Outside Air Temperature                89  token_and_partial
# cabin_alt                    Cabin Pressure Altitude                 79  token_and_partial
# radio_height                 Height Radio Altimeter                  85  token_overlap
# mach_no                      Mach Number                            46  token_overlap
# flap_pos                     Flap Position Degrees                  79  token_and_partial
# landing_gear_state           Landing Gear Position State            88  token_overlap
# true_heading                 Heading True Degrees                   86  token_overlap
#
# Unmatched List A terms:
#   ground_speed, QNH, SAT, N1, wow_switch, hyd_qty_b
#
# Unmatched List B terms:
#   Ambient Air Temperature, Fan Rotation Speed,
#   Right Hydraulic Reservoir Level, Altitude Setting,
#   Weight On Wheels Indicator, Aircraft Groundspeed


# Chapter 3: fit_quiet

quiet_result = fit_quiet(list_a, list_b)

# Result: ranked candidates with scores
#
# List A term                  Ranked List B candidates
# ---------------------------  -------------------------------------------------------
# baro_alt                     Barometric Altitude (79)
# static_pressure_corr         Corrected Static Pressure (90)
# total_air_temp               Total Air Temperature (89)
#                              Ambient Air Temperature (55)
#                              Outside Air Temperature (55)
# vert_accel                   Acceleration Vertical (79)
# indicated_airspeed           Airspeed Indicated (96)
# ground_speed                 Wind Speed (46)
# eng_1_rpm                    Engine 1 RPM (89)
# fuel_flow_left               Left Engine Fuel Flow (88)
# oil_press_no_2               Engine 2 Oil Pressure (65)
# exhaust_gas_temp             Exhaust Gas Temperature (89)
# angle_attack                 Aircraft Angle of Attack (82)
# pitch_rate_deg_s             Pitch Angular Rate Degrees Second (63)
# roll_rate                    Aircraft Roll Rate (85)
# yaw_rate                     Rate of Yaw (87)
# gps_lat                      GPS Latitude Degrees (79)
# gps_lon                      Longitude GPS Degrees (78)
# wind_spd                     Wind Speed (48), Wind Direction (45)
# wind_dir                     Wind Direction (86), Wind Speed (46)
# outside_air_temp             Outside Air Temperature (89)
#                              Total Air Temperature (56)
#                              Ambient Air Temperature (55)
# cabin_alt                    Cabin Pressure Altitude (79)
# radio_height                 Height Radio Altimeter (85)
# mach_no                      Mach Number (46)
# flap_pos                     Flap Position Degrees (79)
# landing_gear_state           Landing Gear Position State (88)
# true_heading                 Heading True Degrees (86)
# QNH                          no candidates above cutoff
# SAT                          no candidates above cutoff
# N1                           no candidates above cutoff
# wow_switch                   no candidates above cutoff
# hyd_qty_b                    no candidates above cutoff


# Chapter 4: fit_silent

silent_result = fit_silent(list_a, list_b)

# Result: ranked candidate names without scores
#
# List A term                  Ranked List B candidates
# ---------------------------  -------------------------------------------------------
# baro_alt                     Barometric Altitude
# static_pressure_corr         Corrected Static Pressure
# total_air_temp               Total Air Temperature
#                              Ambient Air Temperature
#                              Outside Air Temperature
# vert_accel                   Acceleration Vertical
# indicated_airspeed           Airspeed Indicated
# ground_speed                 Wind Speed
# eng_1_rpm                    Engine 1 RPM
# fuel_flow_left               Left Engine Fuel Flow
# oil_press_no_2               Engine 2 Oil Pressure
# exhaust_gas_temp             Exhaust Gas Temperature
# angle_attack                 Aircraft Angle of Attack
# pitch_rate_deg_s             Pitch Angular Rate Degrees Second
# roll_rate                    Aircraft Roll Rate
# yaw_rate                     Rate of Yaw
# gps_lat                      GPS Latitude Degrees
# gps_lon                      Longitude GPS Degrees
# wind_spd                     Wind Speed, Wind Direction
# wind_dir                     Wind Direction, Wind Speed
# outside_air_temp             Outside Air Temperature
#                              Total Air Temperature
#                              Ambient Air Temperature
# cabin_alt                    Cabin Pressure Altitude
# radio_height                 Height Radio Altimeter
# mach_no                      Mach Number
# flap_pos                     Flap Position Degrees
# landing_gear_state           Landing Gear Position State
# true_heading                 Heading True Degrees
# QNH                          no candidates above cutoff
# SAT                          no candidates above cutoff
# N1                           no candidates above cutoff
# wow_switch                   no candidates above cutoff
# hyd_qty_b                    no candidates above cutoff


# Chapter 5: XLS extraction followed by fit_silent

workbook = project_directory / "flight_parameters.xlsx"
xls_list_a = xls_to_list(
    workbook,
    "Recorded Parameter",
    reference_directory / "demo_source_names.json",
)
xls_list_b = xls_to_list(
    workbook,
    "Reference Parameter",
    reference_directory / "demo_target_names.yaml",
)
xls_result = fit_silent(xls_list_a, xls_list_b)

# Result: extracted XLS terms and their candidates
#
# XLS List A term              Ranked XLS List B candidates
# ---------------------------  ----------------------------------
# BarometricAltitude           Altitude Barometric
# Static Pressure Corrected    StaticPressure_Corrected
# TotalAirTemperature          Air Temperature Total
# vertical_acceleration        Acceleration Vertical
# indicated_airspeed           Airspeed Indicated
