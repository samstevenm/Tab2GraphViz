import argparse
from gooey import Gooey, GooeyParser
import pandas as pd
import colorsys
import subprocess
import os
import shlex
import sys

# Determine if Gooey is being bypassed
def is_gooey_available():
    # Check if '--ignore-gooey' is in the arguments to determine the mode
    return '--ignore-gooey' not in sys.argv

@Gooey(optional_cols=2, 
      program_name="Network Diagram Generator",
      program_description="Generate network diagrams from CSV data.",
      default_size=(610, 530))
def main():
    # Use GooeyParser if Gooey is active, else use argparse.ArgumentParser
    parser = GooeyParser(description="Generate network diagrams from CSV files.") if is_gooey_available() else argparse.ArgumentParser(description="Generate network diagrams from CSV files.")
    
    if is_gooey_available():
        parser.add_argument('csv_file', widget="FileChooser", help="Select a CSV file containing network data.", type=str)
    else:
        parser.add_argument('csv_file', help="Select a CSV file containing network data.", type=argparse.FileType('r'), default=sys.stdin)
    
    parser.add_argument('-d', '--dot', action='store_true', help="Save the network diagram as a DOT file.")
    parser.add_argument('-s', '--svg', action='store_true', help="Generate and save the network diagram as an SVG file.")

    args = parser.parse_args()

    if args.csv_file:
        # For CLI mode, 'csv_file' is a file object; for GUI mode, it's a filename string
        csv_file_path = args.csv_file.name if not is_gooey_available() else args.csv_file
        df = read_csv_data(csv_file_path)
        zones = generate_zones_from_dataframe(df)
        base_filename = os.path.splitext(csv_file_path)[0]
        dot_filename = f"{base_filename}.dot"
        graphviz_code = generate_graphviz_code(df, zones)
        
        if args.dot or args.svg:
            with open(dot_filename, "w") as dot_file:
                dot_file.write(graphviz_code)
            print(f"DOT file '{dot_filename}' saved.")

        if args.svg:
            generate_svg(dot_filename)

def read_csv_data(csv_file: str) -> pd.DataFrame:
    """Loads network data from CSV into DataFrame."""
    return pd.read_csv(csv_file, dtype=str, na_filter=False)

def generate_zones_from_dataframe(df: pd.DataFrame) -> dict:
    """Organizes devices by location and zone."""
    zones = {}
    for _, row in df.iterrows():
        zones.setdefault(row['Location'], {}).setdefault(row['Zone'], []).append(row['Domotz Name'])
    return zones

def generate_pastel_color(seed: str) -> str:
    """Generates pastel color for visualization."""
    hue = (hash(seed) % 255) / 255.0
    return "#{:02x}{:02x}{:02x}".format(*[int(c * 255) for c in colorsys.hls_to_rgb(hue, 0.8, 0.7)])

def generate_graphviz_code(df: pd.DataFrame, zones: dict) -> str:
    dot_code = "digraph NetworkDiagram {\n    node [shape=box];\n\n"
    for location, zone_dict in zones.items():
        location_str = format_identifier(location)
        dot_code += f'    subgraph cluster_{location_str} {{\n'
        dot_code += f'        label = "{format_label(location)}";\n        style = "filled,rounded";\n'
        dot_code += f'        fillcolor = "{generate_pastel_color(location)}";\n'
        for zone, devices in zone_dict.items():
            zone_str = format_identifier(zone)
            dot_code += f'        subgraph cluster_{location_str}_{zone_str} {{\n'
            dot_code += f'            label = "{format_label(zone)}";\n            style = "filled,rounded";\n'
            dot_code += f'            fillcolor = "{generate_pastel_color(location+zone)}";\n'
            for device in devices:
                device_row = df[df['Domotz Name'] == device].iloc[0]
                device_str = format_identifier(device)
                label = f"{format_label(device)}\\n{device_row['Model']}\\n{device_row['MAC']}\\n{device_row['IP Address']}"
                dot_code += f'            "{device_str}" [label="{label}"];\n'
            dot_code += '        }\n'
        dot_code += '    }\n\n'
    # Ensure edge definitions use quoted identifiers as well
    return dot_code

def format_identifier(identifier):
    """Enclose the identifier in quotes if it contains special characters or starts with a digit."""
    if not identifier.isalnum() or identifier[0].isdigit():
        return f'"{identifier}"'
    return identifier

def format_label(label):
    """Prepare label for DOT by enclosing in quotes and escaping internal quotes."""
    return label.replace('"', '\\"')



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

if __name__ == "__main__":
    main()
