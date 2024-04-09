import argparse
from gooey import Gooey, GooeyParser
import pandas as pd
import colorsys
import subprocess
import os
import shlex

def read_csv_data(csv_file: str) -> pd.DataFrame:
    """Loads network data from CSV into DataFrame."""
    return pd.read_csv(csv_file)

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
    """Generates Graphviz DOT code with subgraphs and colored zones."""
    dot_code = """
    digraph NetworkDiagram {
        //graph [splines=ortho];  // Orthogonal (90deg) lines for edges
        node [shape=box, style="filled", fillcolor="lightgrey", fontname="Helvetica"]; // Stylish nodes
        
        // Increase the separation between nodes and clusters to reduce line crossings
        nodesep=1;  // Increase node separation
        ranksep=1;  // Increase rank separation between layers of nodes
        
        // Use a compound=true to allow edges to be clipped properly at cluster boundaries
        compound=true;
    """
    for location, zone_dict in zones.items():
        dot_code += f'    subgraph "cluster_{location.replace(" ", "_")}" {{\n'
        dot_code += f'        label = "{location}";\n        style = "filled,rounded";\n'
        dot_code += f'        fillcolor = "{generate_pastel_color(location)}";\n'
        for zone, devices in zone_dict.items():
            dot_code += f'        subgraph "cluster_{location.replace(" ", "_")}_{zone.replace(" ", "_")}" {{\n'
            dot_code += f'            label = "{zone}";\n            style = "filled,rounded";\n'
            dot_code += f'            fillcolor = "{generate_pastel_color(location+zone)}";\n'
            for device in devices:
                device_row = df[df['Domotz Name'] == device].iloc[0]
                label = f"{device}\\n{device_row['Model']}\\n{device_row['MAC']}\\n{device_row['IP Address']}"
                dot_code += f'            "{device}" [label="{label}"];\n'
            dot_code += '        }\n'
        dot_code += '    }\n\n'
    for _, row in df.iterrows():
        if row['Uplink'] != 'Internet' and pd.notna(row['Uplink']):
            dot_code += f'    "{row["Domotz Name"]}" -> "{row["Uplink"]}" [label="{row["Label"].replace("->", " to ")}"];\n'
    dot_code += '}\n'
    return dot_code

def generate_svg(dot_file: str):
    """Generates SVG from DOT using subprocess, ensuring file paths are properly handled."""
    svg_file = dot_file.replace('.dot', '.svg')
    try:
        # Using list format for subprocess.run to avoid shell=True and ensure correct handling of paths
        subprocess.run(['dot', '-Tsvg', dot_file, '-o', svg_file], check=True, capture_output=True)
        print(f"SVG file '{svg_file}' generated.")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else 'Unknown error'
        print(f"Error generating SVG: {error_message}")
        if "syntax error" in error_message:
            print("This may be due to an unquoted identifier or special characters in your DOT file.")
            print("Ensure all node names or labels containing special characters or hyphens are enclosed in double quotes.")

@Gooey(program_name="Network Diagram Generator", program_description="Generate network diagrams from CSV data. Ask Sam for help.")
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
