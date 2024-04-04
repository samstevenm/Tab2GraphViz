# path/filename: generate_network_diagram.py

import argparse
import pandas as pd
import colorsys
from typing import Dict, List

def read_csv_data(csv_file: str) -> pd.DataFrame:
    """
    Reads network data from a CSV file into a pandas DataFrame.

    Parameters:
        csv_file (str): Path to the CSV file containing network data.

    Returns:
        pd.DataFrame: DataFrame containing the network data.
    """
    try:
        return pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file {csv_file} was not found.")
        exit(1)
    except pd.errors.EmptyDataError:
        print("Error: The file is empty.")
        exit(1)

def generate_zones_from_dataframe(df: pd.DataFrame) -> Dict[str, Dict[str, List[str]]]:
    """
    Organizes network devices into zones and locations from DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing network data.

    Returns:
        Dict: A dictionary organizing devices by location and zone.
    """
    zones = {}
    for _, row in df.iterrows():
        location, zone, device = row['Location'], row['Zone'], row['Domotz Name']
        zones.setdefault(location, {}).setdefault(zone, []).append(device)
    return zones

def generate_pastel_color(seed: str) -> str:
    """
    Generates a pastel color based on a hash of the input seed.

    Parameters:
        seed (str): Seed for color generation.

    Returns:
        str: Hexadecimal color code.
    """
    hue = (hash(seed) % 255) / 255.0
    saturation, lightness = 0.7, 0.8
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

def generate_device_nodes(df: pd.DataFrame, location: str, zone: str, zones: Dict[str, Dict[str, List[str]]]) -> str:
    """
    Generates Graphviz nodes for devices in a given location and zone.

    Parameters:
        df (pd.DataFrame): DataFrame containing network data.
        location (str): Network location.
        zone (str): Network zone.
        zones (Dict): A dictionary organizing devices by location and zone.

    Returns:
        str: Graphviz formatted device nodes.
    """
    node_statements = ""
    for device in zones[location][zone]:
        device_row = df.loc[df['Domotz Name'] == device]
        label = f"{device}\\n{device_row['Model'].values[0]}\\n{device_row['MAC'].values[0]}\\n{device_row['IP Address'].values[0]}"
        node_statements += f'"{device}" [label="{label}"];\n'
    return node_statements

def generate_graphviz_code(df: pd.DataFrame, zones: Dict[str, Dict[str, List[str]]]) -> str:
    """
    Generates the complete Graphviz DOT code from the DataFrame and zones dictionary.

    Parameters:
        df (pd.DataFrame): DataFrame containing network data.
        zones (Dict): A dictionary organizing devices by location and zone.

    Returns:
        str: Complete Graphviz DOT code for network diagram.
    """
    dot_code = "digraph NetworkDiagram {\n"
    dot_code += '    node [shape=box];\n\n'

    for location, zone_dict in zones.items():
        location_id = location.replace(" ", "_")
        dot_code += f'    subgraph cluster_{location_id} {{\n'
        dot_code += f'        label = "{location}";\n'
        dot_code += '        style = "filled,rounded";\n'
        dot_code += f'        fillcolor = "{generate_pastel_color(location)}";\n'
        for zone in zone_dict:
            zone_id = f'{location_id}_{zone.replace(" ", "_")}'
            dot_code += f'        subgraph cluster_{zone_id} {{\n'
            dot_code += f'            label = "{zone}";\n'
            dot_code += '            style = "filled,rounded";\n'
            dot_code += f'            fillcolor = "{generate_pastel_color(location+zone)}";\n'
            dot_code += generate_device_nodes(df, location, zone, zones)
            dot_code += '        }\n'
        dot_code += '    }\n\n'

    for _, row in df.iterrows():
        if row['Uplink'] != 'Internet':
            dot_code += f'    "{row["Domotz Name"]}" -> "{row["Uplink"]}" [label="{row["Label"]}"];\n'

    dot_code += '}\n'
    return dot_code

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for CSV file path.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Generate Graphviz DOT code for network diagram from CSV file")
    parser.add_argument("csv_file", help="Path to the CSV file containing network data")
    return parser.parse_args()

def main():
    args = parse_arguments()
    df = read_csv_data(args.csv_file)
    zones = generate_zones_from_dataframe(df)
    graphviz_code = generate_graphviz_code(df, zones)
    print(graphviz_code)

if __name__ == "__main__":
    main()
