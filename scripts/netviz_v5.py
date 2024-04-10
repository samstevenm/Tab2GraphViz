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

def generate_graphviz_code(df: pd.DataFrame, zones: dict, paper_size: str, ratio: str, splines: str, ranksep: str) -> str:
    """Generates Graphviz DOT code with selected paper size, ratio, spline options, and rank separation."""
    paper_sizes = {
        '11x17': '11,17',
        'ARCH A': '9,12',
        'ARCH B': '12,18',
        'ARCH C': '18,24',
        'ARCH D': '24,36',
        'ARCH E1': '30,42',
        'ARCH E': '36,48'
    }
    size_attr = paper_sizes.get(paper_size, '24,36')  # Default to ARCH D if not found

    # Start the DOT code for the graph with selected graph attributes
    dot_code = f"""
    digraph NetworkDiagram {{
        graph [splines={splines}, ratio={ratio}, size="{size_attr}", ranksep={ranksep}];
        node [shape=box, style=filled, fillcolor=lightgrey, fontname=Helvetica];
        nodesep=1;
        compound=true;
    """

    # Loop through each location, creating subgraphs for better organization and visualization
    for location, zone_dict in zones.items():
        location_id = sanitize_input(location)
        dot_code += f'    subgraph "cluster_{location_id}" {{\n'
        dot_code += f'        label="{location}";\n        style="filled,rounded";\n'
        dot_code += f'        fillcolor="{generate_pastel_color(location)}";\n'
        
        # Loop through each zone within the location, creating nested subgraphs
        for zone, devices in zone_dict.items():
            zone_id = sanitize_input(zone)
            dot_code += f'        subgraph "cluster_{location_id}_{zone_id}" {{\n'
            dot_code += f'            label="{zone}";\n            style="filled,rounded";\n'
            dot_code += f'            fillcolor="{generate_pastel_color(location + zone)}";\n'
            
            # Add each device within the zone as a node
            for device in devices:
                device_row = df[df['Domotz Name'] == device].iloc[0]
                label = (f"{device}\\n{device_row['Model']}\\nMAC: {device_row['MAC']}\\n"
                         f"IP: {device_row['IP Address']}")
                dot_code += f'            "{sanitize_input(device)}" [label="{label}"];\n'
            dot_code += '        }\n'
        dot_code += '    }\n'

    # Loop through the DataFrame rows to create edges between devices with optional port and label information
    for _, row in df.iterrows():
        if row['Uplink'] not in ['Internet', 'Unknown'] and pd.notna(row['Uplink']):
            src_device = sanitize_input(row["Domotz Name"])
            dst_device = sanitize_input(row["Uplink"])
            src_port = sanitize_input(row["Source Port"]) if pd.notna(row["Source Port"]) and row["Source Port"] != 'Unknown' else ""
            dst_port = sanitize_input(row["Destination Port"]) if pd.notna(row["Destination Port"]) and row["Destination Port"] != 'Unknown' else ""
            label = f"{src_port} to {dst_port}" if src_port and dst_port else ""

            src = f'"{src_device}"' + (f":{src_port}" if src_port else "")
            dst = f'"{dst_device}"' + (f":{dst_port}" if dst_port else "")

            # Use label for edges; consider using xlabel if external labels are preferred
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

@Gooey(optional_cols=2, 
      program_name="Network Diagram Generator",
      program_description="Generate network diagrams from CSV data.",
      default_size=(610, 610))

def main():
    parser = GooeyParser(description="Generate network diagrams from CSV files.")
    parser.add_argument('csv_file', widget="FileChooser", help="Select a CSV file containing network data.")
    parser.add_argument('-d', '--dot', action='store_true', help="Save the network diagram as a DOT file.")
    parser.add_argument('-s', '--svg', action='store_true', help="Generate and save the network diagram as an SVG file.")
    parser.add_argument('-p', '--paper_size', default='ARCH D', choices=['11x17', 'ARCH A', 'ARCH B', 'ARCH C', 'ARCH D', 'ARCH E1', 'ARCH E'],
                        help="Select the paper size for the diagram", widget='Dropdown')
    parser.add_argument('-r', '--ratio', default='auto', choices=['fill', 'auto'],
                        help="Select the aspect ratio for the diagram", widget='Dropdown')
    parser.add_argument('--splines', default='ortho', choices=['ortho', 'curved'],
                        help="Select whether to use orthogonal splines or not", widget='Dropdown')
    parser.add_argument('--ranksep', default=1, help="Set the rank separation for the diagram", widget='Slider', gooey_options={'min': 0, 'max': 10})



    args = parser.parse_args()

    if args.csv_file:
        df = read_csv_data(args.csv_file)
        zones = generate_zones_from_dataframe(df)
        base_filename = os.path.splitext(args.csv_file)[0]
        dot_filename = f"{base_filename}.dot"
        graphviz_code = generate_graphviz_code(df, zones, args.paper_size, args.ratio, args.splines, args.ranksep)

        if args.dot or args.svg:
            with open(dot_filename, "w") as dot_file:
                dot_file.write(graphviz_code)
            print(f"DOT file '{dot_filename}' saved.")

        if args.svg:
            generate_svg(dot_filename)

if __name__ == "__main__":
    main()
