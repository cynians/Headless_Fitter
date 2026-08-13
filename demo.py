from headless_fitter import fit_loudly, fit_silently


source_names = [
    "BarometricAltitude",
    "Static Pressure Corrected",
    "TotalAirTemperature",
    "vertical_acceleration",
    "indicated_airspeed",
]

target_names = [
    "Acceleration Vertical",
    "StaticPressure_Corrected",
    "Air Temperature Total",
    "Altitude Barometric",
    "Airspeed Indicated",
]

loud_result = fit_loudly(source_names, target_names)
silent_result = fit_silently(source_names, target_names)

# loud_result contains five matches and no unmatched terms:
# BarometricAltitude -> Altitude Barometric (96)
# Static Pressure Corrected -> StaticPressure_Corrected (100)
# TotalAirTemperature -> Air Temperature Total (96)
# vertical_acceleration -> Acceleration Vertical (96)
# indicated_airspeed -> Airspeed Indicated (96)
#
# silent_result:
# {
#     "BarometricAltitude": [
#         {"candidate": "Altitude Barometric", "score": 96}
#     ],
#     "Static Pressure Corrected": [
#         {"candidate": "StaticPressure_Corrected", "score": 100}
#     ],
#     "TotalAirTemperature": [
#         {"candidate": "Air Temperature Total", "score": 96}
#     ],
#     "vertical_acceleration": [
#         {"candidate": "Acceleration Vertical", "score": 96}
#     ],
#     "indicated_airspeed": [
#         {"candidate": "Airspeed Indicated", "score": 96}
#     ]
# }
