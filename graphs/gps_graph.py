from .graph import Graph
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
from io import BytesIO
import requests
from dotenv import load_dotenv
import os
import matplotlib.colors as mcolors

load_dotenv()  

class GPSGraph(Graph):
    def __init__(self, combined_df,
                 name="GPS 3D", type="3D",
                 x_axis_title="Longitude", y_axis_title="Latitude",
                 z_axis_title="Altitude", title="3D GPS Path Colored by Flight State"):
        """
        combined_df: single merged DataFrame containing ts, latitude, longitude, Alt/height, state, etc.
        satellite_image_path: path to satellite image for ground texture
        """
        super().__init__(name, type=type)
        self.df = combined_df.copy()

        # Initialize figure layout
        self.fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title=x_axis_title,
                yaxis_title=y_axis_title,
                zaxis_title=z_axis_title,
                aspectmode="data"
            )
        )

        self.prepare_data()

    def prepare_data(self):
        rename_map = {}
        keep_cols = []
        for col in self.df.columns:
            if 'latitude' in col.lower():
                rename_map[col] = 'latitude'
                keep_cols.append(col)
            elif 'longitude' in col.lower():
                rename_map[col] = 'longitude'
                keep_cols.append(col)
            elif 'height' in col.lower():
                rename_map[col] = 'height'
                keep_cols.append(col)
            elif 'state' in col.lower():
                rename_map[col] = 'state'
                keep_cols.append(col)
            elif 'ts' in col.lower():
                rename_map[col] = 'ts'
                keep_cols.append(col)

        self.df = self.df[keep_cols].rename(columns=rename_map)
        df_events = self.df[['ts', 'state']].copy()
        self.df = self.df.dropna(subset=['latitude', 'longitude'])

        self.origin_lat = self.df["latitude"].iloc[0]
        self.origin_lon = self.df["longitude"].iloc[0]
        R = 6371000

        self.df["x"] = (self.df["longitude"] - self.origin_lon) * np.cos(np.radians(self.origin_lat)) * (np.pi/180) * R
        self.df["y"] = (self.df["latitude"] - self.origin_lat) * (np.pi/180) * R
        self.df["z"] = self.df["height"]

       
        df_events = df_events.dropna(subset=['state'])
        print(df_events)

        self.df['state'] = None
        for i in range(len(df_events) - 1):
            mask = (self.df['ts'] >= df_events.iloc[i]['ts']) & (self.df['ts'] < df_events.iloc[i + 1]['ts'])
            self.df.loc[mask, 'state'] = df_events.iloc[i]['state']

        if not df_events.empty:
            self.df.loc[self.df['ts'] >= df_events.iloc[-1]['ts'], 'state'] = df_events.iloc[-1]['state']

        self.df = self.df.sort_values(by='ts').reset_index(drop=True)

        print(self.df)

    def get_satellite_image(self, zoom=18, size="1280x1280", margin=0):
        key = os.getenv("GOOGLE_MAPS_API")

        if key is None:
            raise ValueError("Google API key required for satellite imagery")

        lat_min = self.df['latitude'].min() - margin
        lat_max = self.df['latitude'].max() + margin
        lon_min = self.df['longitude'].min() - margin
        lon_max = self.df['longitude'].max() + margin

        print(f"Bounding box: lat [{lat_min}, {lat_max}], lon [{lon_min}, {lon_max}]")

        print(f"Map Height: {lat_max - lat_min}, Map Width: {lon_max - lon_min}")
        image_height = int((lat_max - lat_min) / (lon_max - lon_min) * int(size.split('x')[0]))
        size = f"{size.split('x')[0]}x{image_height}"
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2

        url = (
            "https://maps.googleapis.com/maps/api/staticmap?"
            f"size={size}"
            f"&scale=2"
            f"&maptype=satellite"
            f"&path=weight:3|color:0xff0000|"
            f"{lat_min},{lon_min}|{lat_min},{lon_max}|{lat_max},{lon_max}|"
            f"{lat_max},{lon_min}|{lat_min},{lon_min}"
            f"&key={key}"
        )

        response = requests.get(url)
        print(f"url: {url}")    

        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            self.satellite_image = np.array(img) / 255.0
        else:
            raise RuntimeError(f"Failed to fetch Google satellite image: {response.status_code}")

        origin_lat = self.df['latitude'].iloc[0]
        origin_lon = self.df['longitude'].iloc[0]

        def lon_to_meters(lon):
            return (lon - origin_lon) * np.cos(np.radians(origin_lat)) * (np.pi / 180) * 6371000

        def lat_to_meters(lat):
            return (lat - origin_lat) * (np.pi / 180) * 6371000

        self.x_range = [lon_to_meters(lon) for lon in [lon_min, lon_max]]
        self.y_range = [lat_to_meters(lat) for lat in [lat_min, lat_max]]

    def make_graph(self):


        if hasattr(self, 'satellite_image') and self.satellite_image is not None:
            self.satellite_image = np.flipud(self.satellite_image)
            img = self.satellite_image 
    
            if img.ndim == 2:
                surface_color = img
            else:
                surface_color = img[:, :, 0]
            # Add as surface
            self.fig.add_trace(
                go.Surface(
                    z=np.zeros((img.shape[0], img.shape[1])),  # flat at ground level
                    x=np.linspace(self.x_range[0], self.x_range[1], img.shape[1]),
                    y=np.linspace(self.y_range[0], self.y_range[1], img.shape[0]),
                    surfacecolor=surface_color,  # or average if RGB
                    colorscale="gray",
                    showscale=False,
                    opacity=1.0
                )
            )
        state_colors = {
            "THRUSTING": "red",
            "COASTING": "#24d7f2",
            "DROGUE": "pink",
            "MAIN": "purple",
            "TOUCHDOWN": "blue"
        }

        for state, color in state_colors.items():
            state_df = self.df[self.df["state"] == state]
            if not state_df.empty:
                self.fig.add_trace(
                    go.Scatter3d(
                        x=state_df["longitude"],
                        y=state_df["latitude"],
                        z=state_df["z"],
                        mode='markers+lines',
                        marker=dict(size=5, color=color),
                        line=dict(color="grey", width=2),
                        name=state
                    )
                )

        self.show()