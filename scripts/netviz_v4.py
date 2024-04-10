import argparse
from gooey import Gooey, GooeyParser
import pandas as pd
import colorsys
import subprocess
import os
import shlex

def sanitize_input(input_str):
    """Sanitizes inputs for Graphviz by replacing illegal characters, including those problematic in paths and identifiers."""
    replacements = {
        '"': "'",  # Replace double quotes with single quotes
        ':': '-',  # Replace colons with dashes
        ',': '',   # Remove commas
        '\n': ' ', # Replace newlines with spaces
        ' ': '_',  # Replace spaces with underscores for cluster names
        '/': '_',  # Replace forward slashes with underscores
        '\\': '_', # Replace backslashes with underscores
        '{': '',   # Remove curly braces
        '}': '',
        '[': '',   # Remove square brackets
        ']': '',
        '|': '_',  # Replace pipe characters with underscores
        '<': '_',  # Replace less than with underscore
        '>': '_',  # Replace greater than with underscore
    }
    for old, new in replacements.items():
        input_str = input_str.replace(old, new)
    return input_str



def read_csv_data(csv_file: str) -> pd.DataFrame:
    """Loads network data from CSV into DataFrame, including handling of new columns and empty values."""
    df = pd.read_csv(csv_file)
    for col in df.columns:
        df[col] = df[col].fillna('Unknown')  # Replace NaN values with 'Unknown'
        df[col] = df[col].apply(lambda x: sanitize_input(str(x)))  # Sanitize inputs
    return df

def generate_zones_from_dataframe(df: pd.DataFrame) -> dict:
    """Organizes devices by location and zone, considering new columns."""
    zones = {}
    for _, row in df.iterrows():
        zones.setdefault(row['Location'], {}).setdefault(row['Zone'], []).append(row['Domotz Name'])
    return zones

def generate_pastel_color(seed: str) -> str:
    """Generates pastel color for visualization."""
    hue = (hash(seed) % 255) / 255.0
    return "#{:02x}{:02x}{:02x}".format(*[int(c * 255) for c in colorsys.hls_to_rgb(hue, 0.8, 0.7)])



def generate_graphviz_code(df: pd.DataFrame, zones: dict) -> str:
    """Generates Graphviz DOT code with subgraphs, colored zones, additional device details, and ports."""
    dot_code = """
    digraph NetworkDiagram {
        //graph [splines=ortho, ratio=auto]; // Adjust 'ratio' for aspect ratio control
        graph [ratio=fill, size="46,33"]; // Adjust 'ratio' for aspect ratio control
        node [shape=box, style=filled, fillcolor=lightgrey, fontname=Helvetica];
        nodesep=0.75; // Adjust horizontal spacing
        ranksep=1.5;  // Adjust vertical spacing for more balanced expansion
        compound=true;
        // rankdir=LR; // Uncomment to layout the graph left-to-right
    """
    for location, zone_dict in zones.items():
        location_id = sanitize_input(location)
        dot_code += f'    subgraph "cluster_{location_id}" {{\n'
        dot_code += f'        label="{location}";\n        style="filled,rounded";\n'
        dot_code += f'        fillcolor="{generate_pastel_color(location)}";\n'
        for zone, devices in zone_dict.items():
            zone_id = sanitize_input(zone)
            dot_code += f'        subgraph "cluster_{location_id}_{zone_id}" {{\n'
            dot_code += f'            label="{zone}";\n            style="filled,rounded";\n'
            dot_code += f'            fillcolor="{generate_pastel_color(location + zone)}";\n'
            for device in devices:
                device_row = df[df['Domotz Name'] == device].iloc[0]
                label = (f"{device}\\n{device_row['Model']}\\nMAC: {device_row['MAC']}\\n"
                         f"IP: {device_row['IP Address']}")
                dot_code += f'            "{sanitize_input(device)}" [label="{label}"];\n'
            dot_code += '        }\n'
        dot_code += '    }\n'

    for _, row in df.iterrows():
        if row['Uplink'] not in ['Internet', 'Unknown'] and pd.notna(row['Uplink']):
            src_device = sanitize_input(row["Domotz Name"])
            dst_device = sanitize_input(row["Uplink"])
            src_port = sanitize_input(row["Source Port"]) if pd.notna(row["Source Port"]) and row["Source Port"] != 'Unknown' else None
            dst_port = sanitize_input(row["Destination Port"]) if pd.notna(row["Destination Port"]) and row["Destination Port"] != 'Unknown' else None
            label = f"{src_port} to {dst_port}" if src_port and dst_port else ""

            src = f'"{src_device}"' + (f":{src_port}" if src_port else "")
            dst = f'"{dst_device}"' + (f":{dst_port}" if dst_port else "")

            dot_code += f'    {src} -> {dst} [label="{label}"];\n'
    dot_code += '}\n'
    return dot_code




def generate_svg(dot_file: str):
    """Generates SVG from DOT using subprocess, ensuring file paths are properly handled."""
    svg_file = dot_file.replace('.dot', '.svg')
    try:
        subprocess.run(['dot', '-Tsvg', dot_file, '-o', svg_file], check=True, capture_output=True)
        print(f"SVG file '{svg_file}' generated.")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else 'Unknown error'
        print(f"Error generating SVG: {error_message}")

@Gooey(program_name="Network Diagram Generator", program_description="Generate network diagrams from CSV data. Now with enhanced details.")
def main():
    parser = GooeyParser(description="Generate network diagrams from CSV files.")
    parser.add_argument('csv_file', widget="FileChooser", help="Select a CSV file containing network data.")
    parser.add_argument('-d', '--dot', action='store_true', help="Save the network diagram as a DOT file.")
    parser.add_argument('-s', '--svg', action='store_true', help="Generate and save the network diagram as an SVG file.")

    args = parser.parse_args()

    if args.csv_file:
        df = read_csv_data(args.csv_file)
        zones = generate_zones_from_dataframe(df)
        base_filename = os.path.splitext(args.csv_file)[0]
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
