# path/filename: generate_network_diagram.py

import argparse
import pandas as pd
import colorsys
import subprocess
import os
from typing import Dict, List

def read_csv_data(csv_file: str) -> pd.DataFrame:
    """Loads network data from CSV into DataFrame."""
    return pd.read_csv(csv_file)

def generate_zones_from_dataframe(df: pd.DataFrame) -> Dict[str, Dict[str, List[str]]]:
    """Organizes devices by location and zone."""
    zones = {}
    for _, row in df.iterrows():
        zones.setdefault(row['Location'], {}).setdefault(row['Zone'], []).append(row['Domotz Name'])
    return zones

def generate_pastel_color(seed: str) -> str:
    """Generates pastel color for visualization."""
    hue = (hash(seed) % 255) / 255.0
    return "#{:02x}{:02x}{:02x}".format(*[int(c * 255) for c in colorsys.hls_to_rgb(hue, 0.8, 0.7)])

def generate_graphviz_code(df: pd.DataFrame, zones: Dict) -> str:
    """Generates Graphviz DOT code with subgraphs and colored zones."""
    dot_code = "digraph NetworkDiagram {\n    node [shape=box];\n\n"
    for location, zone_dict in zones.items():
        dot_code += f'    subgraph cluster_{location.replace(" ", "_")} {{\n'
        dot_code += f'        label = "{location}";\n        style = "filled,rounded";\n'
        dot_code += f'        fillcolor = "{generate_pastel_color(location)}";\n'
        for zone, devices in zone_dict.items():
            dot_code += f'        subgraph cluster_{location.replace(" ", "_")}_{zone.replace(" ", "_")} {{\n'
            dot_code += f'            label = "{zone}";\n            style = "filled,rounded";\n'
            dot_code += f'            fillcolor = "{generate_pastel_color(location+zone)}";\n'
            for device in devices:
                device_row = df[df['Domotz Name'] == device].iloc[0]
                label = f"{device}\\n{device_row['Model']}\\n{device_row['MAC']}\\n{device_row['IP Address']}"
                dot_code += f'            "{device}" [label="{label}"];\n'
            dot_code += '        }\n'
        dot_code += '    }\n\n'
    for _, row in df.iterrows():
        if row['Uplink'] != 'Internet':
            dot_code += f'    "{row["Domotz Name"]}" -> "{row["Uplink"]}" [label="{row["Label"]}"];\n'
    dot_code += '}\n'
    return dot_code

def generate_svg(dot_file: str):
    """Generates SVG from DOT using subprocess, handling file paths correctly and improving error handling."""
    svg_file = dot_file.replace('.dot', '.svg')
    dot_file_quoted = shlex.quote(dot_file)
    svg_file_quoted = shlex.quote(svg_file)
    try:
        subprocess.run(f'dot -Tsvg {dot_file_quoted} -o {svg_file_quoted}', shell=True, check=True, stderr=subprocess.PIPE)
        print(f"SVG file '{svg_file}' generated.")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else 'Unknown error'
        print(f"Error generating SVG: {error_message}")
        if "syntax error" in error_message:
            print("This may be due to an unquoted identifier or special characters in your DOT file.")
            print("Ensure all node names or labels containing special characters or hyphens are enclosed in double quotes.")

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Network diagram from CSV.")
    parser.add_argument("-c", "--csv", help="CSV file path.")
    parser.add_argument("-e", "--example", action="store_true", help="Generate example CSV.")
    parser.add_argument("-d", "--dot", action="store_true", help="Save DOT file.")
    parser.add_argument("-s", "--svg", action="store_true", help="Output SVG file.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if args.example:
        generate_example_csv()
        return

    if args.csv:
        df = read_csv_data(args.csv)
        zones = generate_zones_from_dataframe(df)
        base_filename = os.path.splitext(args.csv)[0]
        dot_filename = f"{base_filename}.dot"
        graphviz_code = generate_graphviz_code(df, zones)
        
        if args.dot or args.svg:
            with open(dot_filename, "w") as dot_file:
                dot_file.write(graphviz_code)
            print(f"DOT file '{dot_filename}' saved.")

        if args.svg:
            generate_svg(dot_filename)

if __name__ == "__main__":
    main()
