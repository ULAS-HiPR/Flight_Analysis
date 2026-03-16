from catslogs import binary_parser
from catslogs.embedded_constants import FLIGHT_MAP
import os
import pandas as pd
from functools import reduce

def extract_data_from_vega(log_path, output_log_path=None):
    df_dict, plot_output_dir, base_name = binary_parser.extract_data(
        input_log_path=log_path,
        output_log_path=output_log_path,
        state_map=FLIGHT_MAP,
    )
    return df_dict, plot_output_dir, base_name
        
def check_file_exists(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
def check_directory_exists(dir_path):
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"Directory not found: {dir_path}")

def check_data_type(graph_type):
    valid_types = ["VEGA", "EGGTIMER"]
    if graph_type not in valid_types:
        raise ValueError(f"Invalid flight data type: {graph_type}. Valid types are: {valid_types}")
    
def process_flight_data(file_name, data_type, output_log_path):
    if data_type == "VEGA":
        df_dict, plot_output_dir, base_name = extract_data_from_vega(file_name, output_log_path)
        dfs = [
            df_dict['imu_df'],
            df_dict['baro_df'],
            df_dict['flight_info_df'],
            df_dict['orientation_info_df'],
            df_dict['filtered_data_info_df'],
            df_dict['event_info_df'],
            df_dict['error_info_df'],
            df_dict['flight_states_df'],
            df_dict['gnss_info_df'],
            df_dict['voltage_info_df'],
        ]
        
        df_merged = reduce(lambda left, right: pd.merge(left, right, on="ts", how="outer"), dfs)

        df_merged = df_merged.drop_duplicates(subset=["ts"])
        df_merged = df_merged.sort_values("ts", kind="mergesort").reset_index(drop=True)
        df_merged.sort_values(by='ts').reset_index(drop=True)
        df_merged.to_csv(f"{output_log_path}/merged_{base_name}.csv")
        print(df_merged["ts"].dtype)

        return df_merged
    
    elif data_type == "EGGTIMER":
        df = pd.read_csv(file_name)

        #eggtimer is in feet, convert to meters
        df['Alt'] = df['Alt'].apply(lambda x : x*0.3048)
        df['FAlt'] = df['FAlt'].apply(lambda x : x*0.3048)
        df['FVeloc'] = df['FVeloc'].apply(lambda x : x*0.3048)
        df["ts"] = pd.to_numeric(df["T"], errors="coerce")
        df = df.drop(columns=["T"])
        cols = ["ts"] + [c for c in df.columns if c != "ts"]
        df = df[cols]
        df.to_csv(f"{output_log_path}/metric_{file_name.split('/')[-1]}", index=True)
        
        return df
    else:
        raise ValueError(f"Unsupported data type: {data_type}")
    
def rename_columns_by_file(df, file_name, data_type, time_col="ts"):
    df = df.copy()
    base_name = file_name.split('/')[-1].split('.')[0]
    new_cols = {}
    for col in df.columns:
        if col != time_col:
            new_cols[col] = f"{base_name}_{data_type}_{col}"
    df.rename(columns=new_cols, inplace=True)
    return df
    
def align_dataframes(dfs):
    df_comb = reduce(lambda l, r: pd.merge(l, r, on="ts", how="outer"), dfs)
    df_comb = df_comb.drop_duplicates(subset=["ts"])
    df_comb = df_comb.sort_values("ts", kind="mergesort").reset_index()

    return df_comb

def make_dataframe(flight_data : list[str, str], output_log_path):
    dataframes = []
    output_log_path_folder = ''
    for data in flight_data:
        file_name, data_type = data
        print(f"Processing file: {file_name} with data type: {data_type}")
        base_name = file_name.split('/')[-1].split('.')[0]
        output_log_path_folder = f"{output_log_path}/{base_name}"
        print(f"Output log path: {output_log_path_folder}")
        if not os.path.exists(output_log_path_folder):
            os.mkdir(output_log_path_folder)

        df = process_flight_data(file_name, data_type, output_log_path_folder)
        df_renamed = rename_columns_by_file(df, file_name, data_type)
        dataframes.append(df_renamed)

    comb = align_dataframes(dataframes)
    comb.to_csv(f"{output_log_path}/aligned_flight_data.csv", index=False)

    return comb