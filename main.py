import argparse
from tools import extract_data_from_vega, check_file_exists, check_directory_exists, check_data_type, make_dataframe
from graphs.speed_graph import LineGraph
#from graphs.altitude_graph import AltitudeGraph

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        nargs=2,
        action="append",
        metavar=("FILE", "TYPE"),
        help="Input flight data files and its type (VEGA, EGGTIMER)",
    )

    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory to save the generated graphs & parsed data",
    )

    parser.add_argument(
        "--graph-types",
        nargs="+",
        default=["speed", "altitude"],
        help="Types of graphs to generate (e.g., speed, altitude, acceleration)",
    )

    parser.add_argument(
        "--graph-title",
        help="Prefix for graph titles and output file names",
    )

    args = parser.parse_args()
    inputs = args.input or []
    output_dir = args.output_dir

    check_directory_exists(output_dir)
    for file, filetype in inputs:
        check_file_exists(file)
        check_data_type(filetype)
        print(file, filetype)
    
    flight_data = make_dataframe(inputs, output_dir)
    graph_title_prefix = args.graph_title or "Flight Data"

    for graph_type in args.graph_types:
        if graph_type == "speed":
            graph = LineGraph(flight_data, name="speed_graph", type="speed",
                               x_axis_title="Time (s)", y_axis_title="Speed (m/s)", title=f"{graph_title_prefix} Speed vs Time")
            graph.make_graph()
            graph.save(output_dir)
        elif graph_type == "altitude":
            graph = LineGraph(flight_data, name="altitude_graph", type="altitude",
                               x_axis_title="Time (s)", y_axis_title="Altitude (m)", title=f"{graph_title_prefix} Altitude vs Time")
            graph.make_graph()
            graph.save(output_dir)
        elif graph_type == "acceleration":
            graph = LineGraph(flight_data, name="acceleration_graph", type="acceleration",
                               x_axis_title="Time (s)", y_axis_title="Acceleration (m/s^2)", title=f"{graph_title_prefix} Acceleration vs Time")
            graph.make_graph()
            graph.save(output_dir)
        elif graph_type == "filtered_altitude":
            graph = LineGraph(flight_data, name="filtered_altitude_graph", type="filtered_altitude",
                               x_axis_title="Time (s)", y_axis_title="Filtered Altitude (m)", title=f"{graph_title_prefix} Filtered Altitude vs Time")
            graph.make_graph()
            graph.save(output_dir)
        
        else:
            print(f"Unsupported graph type: {graph_type}")


if __name__ == "__main__":
    main()