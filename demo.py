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

# Printed result:
# {
#   "matches": [
#     {"source_index": 0, "source": "baro_alt", "target_index": 8, "target": "Barometric Altitude", "score": 79, "method": "partial_token", "matched_terms": ("alt~altitude", "baro~barometric")},
#     {"source_index": 1, "source": "static_pressure_corr", "target_index": 4, "target": "Corrected Static Pressure", "score": 90, "method": "token_and_partial", "matched_terms": ("pressure", "static", "corr~corrected")},
#     {"source_index": 2, "source": "total_air_temp", "target_index": 21, "target": "Total Air Temperature", "score": 89, "method": "token_and_partial", "matched_terms": ("air", "total", "temp~temperature")},
#     {"source_index": 3, "source": "vert_accel", "target_index": 18, "target": "Acceleration Vertical", "score": 79, "method": "partial_token", "matched_terms": ("accel~acceleration", "vert~vertical")},
#     {"source_index": 4, "source": "indicated_airspeed", "target_index": 15, "target": "Airspeed Indicated", "score": 96, "method": "token_reorder", "matched_terms": ("airspeed", "indicated")},
#     {"source_index": 6, "source": "eng_1_rpm", "target_index": 10, "target": "Engine 1 RPM", "score": 89, "method": "token_and_partial", "matched_terms": ("1", "rpm", "eng~engine")},
#     {"source_index": 7, "source": "fuel_flow_left", "target_index": 7, "target": "Left Engine Fuel Flow", "score": 88, "method": "token_overlap", "matched_terms": ("flow", "fuel", "left")},
#     {"source_index": 8, "source": "oil_press_no_2", "target_index": 2, "target": "Engine 2 Oil Pressure", "score": 65, "method": "token_and_partial", "matched_terms": ("2", "oil", "press~pressure")},
#     {"source_index": 9, "source": "exhaust_gas_temp", "target_index": 13, "target": "Exhaust Gas Temperature", "score": 89, "method": "token_and_partial", "matched_terms": ("exhaust", "gas", "temp~temperature")},
#     {"source_index": 10, "source": "angle_attack", "target_index": 26, "target": "Aircraft Angle of Attack", "score": 82, "method": "token_overlap", "matched_terms": ("angle", "attack")},
#     {"source_index": 11, "source": "pitch_rate_deg_s", "target_index": 16, "target": "Pitch Angular Rate Degrees Second", "score": 63, "method": "token_and_partial", "matched_terms": ("pitch", "rate", "deg~degree")},
#     {"source_index": 12, "source": "roll_rate", "target_index": 0, "target": "Aircraft Roll Rate", "score": 85, "method": "token_overlap", "matched_terms": ("rate", "roll")},
#     {"source_index": 13, "source": "yaw_rate", "target_index": 9, "target": "Rate of Yaw", "score": 87, "method": "token_overlap", "matched_terms": ("rate", "yaw")},
#     {"source_index": 14, "source": "gps_lat", "target_index": 3, "target": "GPS Latitude Degrees", "score": 79, "method": "token_and_partial", "matched_terms": ("gps", "lat~latitude")},
#     {"source_index": 15, "source": "gps_lon", "target_index": 25, "target": "Longitude GPS Degrees", "score": 78, "method": "token_and_partial", "matched_terms": ("gps", "lon~longitude")},
#     {"source_index": 16, "source": "wind_spd", "target_index": 29, "target": "Wind Speed", "score": 48, "method": "token_overlap", "matched_terms": ("wind",)},
#     {"source_index": 17, "source": "wind_dir", "target_index": 11, "target": "Wind Direction", "score": 86, "method": "token_and_partial", "matched_terms": ("wind", "dir~direction")},
#     {"source_index": 18, "source": "outside_air_temp", "target_index": 1, "target": "Outside Air Temperature", "score": 89, "method": "token_and_partial", "matched_terms": ("air", "outside", "temp~temperature")},
#     {"source_index": 19, "source": "cabin_alt", "target_index": 19, "target": "Cabin Pressure Altitude", "score": 79, "method": "token_and_partial", "matched_terms": ("cabin", "alt~altitude")},
#     {"source_index": 20, "source": "radio_height", "target_index": 28, "target": "Height Radio Altimeter", "score": 85, "method": "token_overlap", "matched_terms": ("height", "radio")},
#     {"source_index": 21, "source": "mach_no", "target_index": 22, "target": "Mach Number", "score": 46, "method": "token_overlap", "matched_terms": ("mach",)},
#     {"source_index": 22, "source": "flap_pos", "target_index": 24, "target": "Flap Position Degrees", "score": 79, "method": "token_and_partial", "matched_terms": ("flap", "pos~position")},
#     {"source_index": 23, "source": "landing_gear_state", "target_index": 5, "target": "Landing Gear Position State", "score": 88, "method": "token_overlap", "matched_terms": ("gear", "landing", "state")},
#     {"source_index": 24, "source": "true_heading", "target_index": 27, "target": "Heading True Degrees", "score": 86, "method": "token_overlap", "matched_terms": ("heading", "true")},
#   ],
#   "unmatched_source": [
#     {"index": 5, "name": "ground_speed"}, {"index": 25, "name": "QNH"},
#     {"index": 26, "name": "SAT"}, {"index": 27, "name": "N1"},
#     {"index": 28, "name": "wow_switch"}, {"index": 29, "name": "hyd_qty_b"},
#   ],
#   "unmatched_target": [
#     {"index": 6, "name": "Ambient Air Temperature"},
#     {"index": 12, "name": "Fan Rotation Speed"},
#     {"index": 14, "name": "Right Hydraulic Reservoir Level"},
#     {"index": 17, "name": "Altitude Setting"},
#     {"index": 20, "name": "Weight On Wheels Indicator"},
#     {"index": 23, "name": "Aircraft Groundspeed"},
#   ],
# }


# Chapter 3: fit_quiet

quiet_result = fit_quiet(list_a, list_b)

# Printed result:
# {
#   "baro_alt": [{"candidate": "Barometric Altitude", "score": 79}],
#   "static_pressure_corr": [{"candidate": "Corrected Static Pressure", "score": 90}],
#   "total_air_temp": [{"candidate": "Total Air Temperature", "score": 89}, {"candidate": "Ambient Air Temperature", "score": 55}, {"candidate": "Outside Air Temperature", "score": 55}],
#   "vert_accel": [{"candidate": "Acceleration Vertical", "score": 79}],
#   "indicated_airspeed": [{"candidate": "Airspeed Indicated", "score": 96}],
#   "ground_speed": [{"candidate": "Wind Speed", "score": 46}],
#   "eng_1_rpm": [{"candidate": "Engine 1 RPM", "score": 89}],
#   "fuel_flow_left": [{"candidate": "Left Engine Fuel Flow", "score": 88}],
#   "oil_press_no_2": [{"candidate": "Engine 2 Oil Pressure", "score": 65}],
#   "exhaust_gas_temp": [{"candidate": "Exhaust Gas Temperature", "score": 89}],
#   "angle_attack": [{"candidate": "Aircraft Angle of Attack", "score": 82}],
#   "pitch_rate_deg_s": [{"candidate": "Pitch Angular Rate Degrees Second", "score": 63}],
#   "roll_rate": [{"candidate": "Aircraft Roll Rate", "score": 85}],
#   "yaw_rate": [{"candidate": "Rate of Yaw", "score": 87}],
#   "gps_lat": [{"candidate": "GPS Latitude Degrees", "score": 79}],
#   "gps_lon": [{"candidate": "Longitude GPS Degrees", "score": 78}],
#   "wind_spd": [{"candidate": "Wind Speed", "score": 48}, {"candidate": "Wind Direction", "score": 45}],
#   "wind_dir": [{"candidate": "Wind Direction", "score": 86}, {"candidate": "Wind Speed", "score": 46}],
#   "outside_air_temp": [{"candidate": "Outside Air Temperature", "score": 89}, {"candidate": "Total Air Temperature", "score": 56}, {"candidate": "Ambient Air Temperature", "score": 55}],
#   "cabin_alt": [{"candidate": "Cabin Pressure Altitude", "score": 79}],
#   "radio_height": [{"candidate": "Height Radio Altimeter", "score": 85}],
#   "mach_no": [{"candidate": "Mach Number", "score": 46}],
#   "flap_pos": [{"candidate": "Flap Position Degrees", "score": 79}],
#   "landing_gear_state": [{"candidate": "Landing Gear Position State", "score": 88}],
#   "true_heading": [{"candidate": "Heading True Degrees", "score": 86}],
#   "QNH": [], "SAT": [], "N1": [], "wow_switch": [], "hyd_qty_b": [],
# }


# Chapter 4: fit_silent

silent_result = fit_silent(list_a, list_b)

# Printed result:
# {
#   "baro_alt": ["Barometric Altitude"],
#   "static_pressure_corr": ["Corrected Static Pressure"],
#   "total_air_temp": ["Total Air Temperature", "Ambient Air Temperature", "Outside Air Temperature"],
#   "vert_accel": ["Acceleration Vertical"],
#   "indicated_airspeed": ["Airspeed Indicated"],
#   "ground_speed": ["Wind Speed"],
#   "eng_1_rpm": ["Engine 1 RPM"],
#   "fuel_flow_left": ["Left Engine Fuel Flow"],
#   "oil_press_no_2": ["Engine 2 Oil Pressure"],
#   "exhaust_gas_temp": ["Exhaust Gas Temperature"],
#   "angle_attack": ["Aircraft Angle of Attack"],
#   "pitch_rate_deg_s": ["Pitch Angular Rate Degrees Second"],
#   "roll_rate": ["Aircraft Roll Rate"],
#   "yaw_rate": ["Rate of Yaw"],
#   "gps_lat": ["GPS Latitude Degrees"],
#   "gps_lon": ["Longitude GPS Degrees"],
#   "wind_spd": ["Wind Speed", "Wind Direction"],
#   "wind_dir": ["Wind Direction", "Wind Speed"],
#   "outside_air_temp": ["Outside Air Temperature", "Total Air Temperature", "Ambient Air Temperature"],
#   "cabin_alt": ["Cabin Pressure Altitude"],
#   "radio_height": ["Height Radio Altimeter"],
#   "mach_no": ["Mach Number"],
#   "flap_pos": ["Flap Position Degrees"],
#   "landing_gear_state": ["Landing Gear Position State"],
#   "true_heading": ["Heading True Degrees"],
#   "QNH": [], "SAT": [], "N1": [], "wow_switch": [], "hyd_qty_b": [],
# }


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

# Printed result:
# {
#   "BarometricAltitude": ["Altitude Barometric"],
#   "Static Pressure Corrected": ["StaticPressure_Corrected"],
#   "TotalAirTemperature": ["Air Temperature Total"],
#   "vertical_acceleration": ["Acceleration Vertical"],
#   "indicated_airspeed": ["Airspeed Indicated"],
# }
