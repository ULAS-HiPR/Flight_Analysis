from .graph import Graph
import plotly.graph_objects as go
import pandas as pd

class LineGraph(Graph): 
    def __init__(self, dataframe, name, type, x_axis_title, y_axis_title, title, state):
        super().__init__(name, type=type, state=state)
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
    
    def eggtimer_vline(self):
        for col in self.df.columns:
            if 'LDA' in col:
                lda_col = col
            elif 'Apogee' in col:
                apogee_col = col
            elif 'N-O' in col:
                no_col = col
            elif 'Drogue' in col:
                drogue_col = col
            elif 'Main' in col:
                main_col = col

        self.fig.add_vline(
            x = self.df['ts'][lda_col.idxmax()],
            line_width = 2,
            line_dash = 'dot',
            line_color = 'blue',
            annotation = {
                'font' : {
                    'size' : 12,
                    'color': 'blue',
                }
            },
            annotation_text = "Launch Detected",
            annotation_position = 'top right'
        )
        self.fig.add_vline(
            x = self.df['ts'][apogee_col.idxmax()],
            line_width = 2,
            line_dash = 'dot',
            line_color = 'green',
            annotation = {
                'font' : {
                    'size' : 12,
                    'color': 'green',
                }
            },
            annotation_text = "Apogee Detected",
            annotation_position = 'left'
        )
        self.fig.add_vline(
            x = self.df['ts'][no_col.idxmax()],
            line_width = 2,
            line_dash = 'dash',
            line_color = 'red',
            annotation = {
                'font' : {
                    'size' : 12,
                    'color': 'red',
                }
            },
            annotation_text = "Nose Over Detected",
            annotation_position = 'bottom right'
        )
        self.fig.add_vline(
            x = self.df['ts'][drogue_col.idxmax()],
            line_width = 2,
            line_dash = 'dot',
            line_color = 'blue',
            annotation = {
                'font' : {
                    'size' : 12,
                    'color': 'blue',
                }
            },
            annotation_text = "Drogue Deployed",
            annotation_position = 'top right'
        )
        self.fig.add_vline(
            x = self.df['ts'][main_col.idxmax()],
            line_width = 2,
            line_dash = 'dot',
            line_color = 'blue',
            annotation = {
                'font' : {
                    'size' : 12,
                    'color': 'blue',
                }
            },
            annotation_text = "Main Deployed",
            annotation_position = 'top right'
        )

    def vega_vline(self):
        event_cols = [col for col in self.df.columns if 'event' in col]
        for col in event_cols:
            event_df = self.df.dropna(subset=[col])
            for idx, row in event_df.iterrows():
                self.fig.add_vline(
                    x=row['ts'],
                    line_width=2,
                    line_dash='dot',
                    line_color='blue',
                    annotation={
                        'font': {
                            'size': 12,
                            'color': 'blue',
                        }
                    },
                    annotation_text=row[col],
                    annotation_position='top right'
                )

    def make_graph(self):
        for col in self.look_for_colums().columns:
            if col != 'ts':
                if 'EGGTIMER' in col:
                    self.fig.add_trace(go.Scatter(x=self.look_for_colums()['ts'], y=self.look_for_colums()[col], mode='lines', connectgaps=True, name=col))
                else:
                    self.fig.add_trace(go.Scatter(x=self.look_for_colums()['ts'], y=self.look_for_colums()[col], mode='lines', name=col))
        
        if self.state:
            for col in self.look_for_colums().columns:
                if col != 'ts' and 'EGGTIMER' in col:
                    self.eggtimer_vline()
                    break
            for col in self.look_for_colums().columns:
                if col != 'ts' and 'VEGA' in col:
                    self.vega_vline()
                    break


        self.show()