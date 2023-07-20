#reads processor-device data from a tab delimited file and generates a graphviz file

#allow the file path the be entered as a command line argument
import sys  #for command line arguments
import argparse #for command line arguments

import pandas as pd
sheet_id = "1O96t52IudOEeXs3DyJCMo1sYNqlL9GTBOjKDURbcHbY"
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
print(df)