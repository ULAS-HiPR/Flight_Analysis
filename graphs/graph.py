import pandas as pd
import plotly.graph_objects as go

class Graph:
    def __init__(self, name=None, type=None):
        self.fig = go.Figure()
        self.name = name
        self.type = type

    def show(self):
        self.fig.show()

    def save(self, output_dir="outputed_graphs"):
        output_path = f"{output_dir}/{self.name}_{self.type}"
        self.fig.write_html(f"{output_path}.html")
        self.fig.write_image(f"{output_dir}.png")

    velocity_columns = ['FVeloc', 'velocity']
    acceleration_columns = ['acceleration', 'filtered_acceleration']
    altitude_columns = ['height', 'filtered_altitude_AGL', 'Alt', 'FAlt']
    filtered_altitude_columns = ['height', 'FAlt']

    eggtimer_coloum_names = {
        'Alt' : 'Altitude',
        'FAlt' : 'Filtered Altitude', 
        'FVeloc' : 'Filtered Velocity', 
        'LDA' : 'Launch Detected',
        'Apogee' : 'Apogee Detected', 
        'N-O' : 'Nose-Over',
        'Main' : 'Main Triggered', 
        'AUX' : 'AUX Triggered'
    }

    vega_coloum_names = {
        'id_x' : 'IMU ID', 
        'Ax' : 'Acceleration X',
        'Ay' : 'Acceleration Y', 
        'Az' : 'Acceleration Z', 
        'Gx' : 'Gyro X',
        'Gy' : 'Gyro Y',
        'Gz' : 'Gyro Z',
        'id_y' : 'Baro ID',
        'T' : 'Temperature', 
        'P' : 'Pressure', 
        'height' : 'Height', 
        'velocity' : 'Velocity',
        'acceleration' : 'Acceleration', 
        'q0_estimated' : 'quaternion 0', 
        'q1_estimated' : 'quaternion 1',
        'q2_estimated' : 'quaternion 2', 
        'q3_estimated' : 'quaternion 3', 
        'filtered_altitude_AGL' : 'Filtered Altitude Above Ground Level', 
        'filtered_acceleration' : 'Filtered Acceleration',
        'event' : 'Event Detected', 
        'out_idx' : 'Output Index', 
        'error' : 'Error Detected',
        'state' : 'Flight State', 
        'latitude' : 'Latitude', 
        'longitude' : 'Longitude',
        'satellites' : 'Satellites Connected',
        'voltage' : 'Battery Voltage'
        }