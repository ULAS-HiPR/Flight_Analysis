from .graph import Graph
import plotly.graph_objects as go
import pandas as pd

class LineGraph(Graph): 
    def __init__(self, dataframe, name, type, x_axis_title, y_axis_title, title):
        super().__init__(name, type=type)
        self.df = dataframe
        self.fig.update_layout(
            title=title,
            xaxis_title=x_axis_title,
            yaxis_title=y_axis_title,
            legend_title="Legend",
        )

    def look_for_colums(self):
        if self.type == "speed":
            columns = self.velocity_columns
        elif self.type == "acceleration":
            columns = self.acceleration_columns
        elif self.type == "altitude":
            columns = self.altitude_columns
        elif self.type == "filtered_altitude":
            columns = self.filtered_altitude_columns
        else:
            raise ValueError(f"Invalid graph type: {self.type}")

        speed_df = self.df[['ts']].copy()
        
         
        matching_cols = []
        for col in columns:
            matching_cols.extend([c for c in self.df.columns if col in c])
    

        for col in matching_cols:
            speed_df[col] = self.df[col]
    
        if matching_cols:
            speed_df = speed_df.dropna(subset=matching_cols, how='all')
            
        return speed_df

    def make_graph(self):
        for col in self.look_for_colums().columns:
            if col != 'ts':
                if 'EGGTIMER' in col:
                    self.fig.add_trace(go.Scatter(x=self.look_for_colums()['ts'], y=self.look_for_colums()[col], mode='lines', connectgaps=True, name=col))
                else:
                    self.fig.add_trace(go.Scatter(x=self.look_for_colums()['ts'], y=self.look_for_colums()[col], mode='lines', name=col))
        
        self.show()