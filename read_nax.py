#reads NAX data from a tab delimited file and generates a graphviz file
#allow the file path the be entered as a command line argument
import sys  #for command line arguments
import argparse #for command line arguments
import os   #for file path
import csv  #for reading the file

#set up the graphviz front matter

frontMatter = """
digraph structs {
    node [shape=record];
    splines=false;
    overlap=false;
    rankdir="LR";
    """
#def generateGraphvizRow(graphvizInput):


def readTAB(fileName):
    #check if the file exists
    if os.path.isfile(fileName):
        #open the file and read it
        with open(fileName, 'r') as f:
        #with open('data.txt', 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            graphvizInput = []
            for row in reader:
   
                #create an array of arrays
                graphvizInput.append(row)
    else:
        print (f"""File "{fileName}" not found. Make sure you entered the correct path and filename.""")
        sys.exit(1)
    #print (graphvizInput)
    lengthgraphvizInput = len(graphvizInput)
    print (f"""##Rows Consumed: {lengthgraphvizInput}""")
    return graphvizInput

def generateGraphviz(fileName, deviceID, deviceModel, devicehwAddress, devicePortCapacity):
    #call getTAB to get the data
    graphvizInput = readTAB(fileName)
    #get the length of the array, later we'll subtract one for the header and this will be the number of ports (we hope)
    deviceTableLength = len(graphvizInput)

    #print(graphvizInput)
    devicePortCapacity = int(deviceTableLength - 1)
    #[2][1] is the model, 3rd row, 2nd column, etc
    #deviceID = str(graphvizInput[1][0]).strip().replace(" ", "").replace(")", "").replace("(", "")
    deviceModel = str(graphvizInput[0][0]).strip()
    deviceLocation = str(graphvizInput[2][1]).strip()
    deviceSerial = str(graphvizInput[3][1]).strip()
    deviceIP = str(graphvizInput[4][1]).strip()
    devicehwAddress = str(graphvizInput[5][1]).strip()
    print (frontMatter)

    #this only works because we strip returns and newlines later
    label = f"""
    "{deviceID}" [label="{deviceModel} | ID: {deviceID} | LOC: {deviceLocation} | 
    SN: {deviceSerial} | IP: {deviceIP} | HW: {devicehwAddress} |
    {{ PORTS &#92;n 1-8| {{
    """
    
    #for i in range(1,numPorts+1):
    #add 1 to the range because the array starts at 0
    for i in range(1,devicePortCapacity+1):
        #append an output the label
        label += f"<{deviceID}o{i}> {i} | |"
        #append an input the label
        label += f"<{deviceID}i{i}> {i} "

        #add a pipe if it's not the last port of a section
        if i % 8 != 0:
            #add a pipe if it's not the last port of the switch
            if i != devicePortCapacity:
                label += " | "
        
        #get the port info (type, number, vlan, connected device) assume:
        #  user copied the data from the switch in the correct order, and with headers
        # expect array of arrays 0,1,2,3,4,5, 0-length of array
        
        #inputs
        devicePortType = str(graphvizInput[i][2]).strip()
        devicePortNum = str(graphvizInput[i][3]).strip()
        devicePortConnectedDevice = str(graphvizInput[i][4]).strip()
        graphvizLineLabel = f"""{devicePortType} {devicePortNum}"""

        #outputs
        devicePortTypeOutput = str(graphvizInput[i][5]).strip()
        devicePortNumOutput = str(graphvizInput[i][6]).strip()
        devicePortConnectedDeviceOutput = str(graphvizInput[i][7]).strip()
        devicePortConnectedDeviceSpeakers = str(graphvizInput[i][8]).strip()
        graphvizLineLabelOutput = f"""{devicePortTypeOutput} {devicePortNumOutput}"""
        
        #print all the ports

        #the extra spaces are to make the graphviz output look nice, there's probably a better way to do this
        #print(f"""{deviceID}:{deviceID}f{str(i)} -> "{devicePortConnectedDevice} ({devicePortType}{str(devicePortNum)})" [label="              {str(graphvizLineLabel)}              "];""")
        print(f"""{deviceID}:{deviceID}o{str(i)} -> " {devicePortConnectedDeviceSpeakers}{devicePortConnectedDeviceOutput} ({devicePortTypeOutput}{str(devicePortNumOutput)})" [label="              {str(graphvizLineLabelOutput)}              "];""")
        #print(f""" "{devicePortConnectedDevice} ({devicePortType}{str(devicePortNum)})" -> {deviceID}:{deviceID}i{str(i)} [label="{str(graphvizLineLabel)}"];""")
        print(f""" "{devicePortConnectedDevice} ({devicePortType}{str(devicePortNum)})" -> {deviceID}:{deviceID}i{str(i)} ;""")


        #put a break every 8 ports
        if i % 8 == 0 and i != 0:
            if i != devicePortCapacity:
                startNextPortSection = i + 1
                if devicePortCapacity - i > 8:
                    endNextPortSection = i + 8
                else:
                    endNextPortSection = devicePortCapacity
                label += f"""}}}} |-&#92;n-| {{ PORTS &#92;n {startNextPortSection}-{endNextPortSection} | {{"""
        print
        
    #remove line breaks and add closing bracket
    #add trailing end quote and escape it with a backslash
    newLabel = str(label + "}} | SAM MYERS | AHT GLOBAL WEST\"];").replace('\n', '').replace('\r', '')
    #newLabel = str(label + "}} | SAM\"];")
    print (newLabel)
    print("}")



def main():
    #check if the user entered a file path
    if len(sys.argv) > 1:
        #if the user entered a file path, use it
        fileName = sys.argv[1]      #get the file path from the command line
        print (f"""##Input File Name: {fileName}""")
        generateGraphviz(fileName, "asdf12340000", "PowerWand3000", "DE:AD:FA:CE:69:69", 24)
    else:
        fileName = input("Enter the file name: ")
        generateGraphviz(fileName, "asdf12340000", "PowerWand3000", "DE:AD:FA:CE:69:69", 24)
    
if __name__ == "__main__":
    #make a switch with 24 ports if they don't specify a number of ports
    main()


#python3 read_whole_section.py 53673_23_SW03.txt > 53673_23_SW03-viz.dot
#use the above command to consume a TAB delimited file and generate a dot file

# dot -Tsvg *.dot > /Users/sm/politis/53673_23_SW03-viz.svg
# use the above command to convert the dot file to svg

#chaining the commands together and doing a little loop:
# `for i in *.txt; do python3 read_whole_section.py $i >> $i.dot; dot -Tsvg $i.dot >> $i.svg; done`