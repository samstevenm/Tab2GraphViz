import argparse
import pandas as pd
import colorsys

def generate_graphviz_code_from_csv(csv_file):
    # Read CSV data into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Create a dictionary to store devices in each zone
    zones = {}
    for _, row in df.iterrows():
        location = row['Location']
        zone = row['Zone']
        device = row['Domotz Name']

        if location not in zones:
            zones[location] = {}
        if zone not in zones[location]:
            zones[location][zone] = []
        zones[location][zone].append(device)

    # Function to generate pastel colors
    def generate_pastel_color(seed):
        hue = (hash(seed) % 255) / 255.0
        saturation = 0.7
        lightness = 0.8
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

    # Function to generate the device nodes in Graphviz format
    def generate_device_nodes(location, zone):
        devices = zones[location][zone]
        node_statements = ""
        for device in devices:
            device_row = df.loc[df['Domotz Name'] == device]
            label = f"{device}\n{device_row['Model'].values[0]}\n{device_row['MAC'].values[0]}\n{device_row['IP Address'].values[0]}"
            node_statements += f'"{device}" [label="{label}"];\n'
        return node_statements

    # Generate the Graphviz DOT code
    dot_code = "digraph NetworkDiagram {\n"
    dot_code += '    node [shape=box];\n\n'

    # Iterate through locations and zones
    for location, zone_dict in zones.items():
        dot_code += f'    subgraph cluster_{location.replace(" ", "_")} {{\n'
        dot_code += f'        label = "{location}";\n'
        dot_code += '        style = "filled,rounded";\n'
        dot_code += f'        fillcolor = "{generate_pastel_color(location)}";\n'  # Generate a pastel color for location
        for zone, devices in zone_dict.items():
            dot_code += f'        subgraph cluster_{location.replace(" ", "_")}_{zone.replace(" ", "_")} {{\n'
            dot_code += f'            label = "{zone}";\n'
            dot_code += '            style = "filled,rounded";\n'
            dot_code += f'            fillcolor = "{generate_pastel_color(location+zone)}";\n'  # Generate a pastel color for zone
            dot_code += generate_device_nodes(location, zone)
            dot_code += '        }\n'
        dot_code += '    }\n\n'

    # Generate the uplink edges
    for _, row in df.iterrows():
        device = row['Domotz Name']
        uplink = row['Uplink']
        if uplink != 'Internet':
            dot_code += f'    "{device}" -> "{uplink}" [label="{row["Label"]}"];\n'

    dot_code += '}\n'
    return dot_code

def main():
    parser = argparse.ArgumentParser(description="Generate Graphviz DOT code for network diagram from CSV file")
    parser.add_argument("csv_file", help="Path to the CSV file containing network data")
    args = parser.parse_args()

    graphviz_code = generate_graphviz_code_from_csv(args.csv_file)
    print(graphviz_code)

if __name__ == "__main__":
    main()
