#reads processor-device data from a tab delimited file and generates a graphviz file

#allow the file path the be entered as a command line argument
import sys  #for command line arguments
import argparse #for command line arguments
import os   #for file path
import csv  #for reading the file
import time

#set up the graphviz front matter

frontMatter = """
digraph structs {
    node [shape=record];
    splines=true;
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
                #print(row)
                
                #create an array of arrays
                graphvizInput.append(row)
    else:
        print (f"""File "{fileName}" not found. Make sure you entered the correct path and filename.""")
        sys.exit(1)

    #print (graphvizInput)
    lengthgraphvizInput = len(graphvizInput)
    print (f"""##Rows Consumed: {lengthgraphvizInput}""")
    #print the number of columns
    deviceTableWidth = len(graphvizInput[0])
    print (f"""##Columns Consumed: {deviceTableWidth}""")
    return graphvizInput

def generateGraphviz(fileName, deviceID, deviceModel, devicehwAddress, devicePortCapacity):
    #call getTAB to get the data
    graphvizInput = readTAB(fileName)
    #get the length of the array, later we'll subtract one for the header and this will be the number of ports (we hope)
    deviceTableLength = len(graphvizInput)
    #get the width of the array, later we'll subtract one and this will be the number of ports (we hope)
    deviceTableWidth = len(graphvizInput[0])


    #print(graphvizInput)
    devicePortCapacity = int(deviceTableLength - 1)

    #last port of first section
    if devicePortCapacity < 4:
        deviceLastPortOfFirstSection = devicePortCapacity
    else:
        deviceLastPortOfFirstSection = 4
    #[2][1] is the model, 3rd row, 2nd column, etc

    deviceID = str(graphvizInput[1][0]).strip().replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("#", "")
    deviceModel = str(graphvizInput[0][0]).strip()
    deviceLocation = str(graphvizInput[3][1]).strip()
    deviceSerial = str(graphvizInput[4][1]).strip()
    deviceIP = str(graphvizInput[5][1]).strip()
    devicehwAddress = str(graphvizInput[6][1]).strip()

    #print the front matter
    print (frontMatter)

    #this only works because we strip returns and newlines later
    label = f"""
    "{deviceID}" [label="{deviceModel} | ID: {deviceID} | LOC: {deviceLocation} | 
    SN: {deviceSerial} | IP: {deviceIP} | HW: {devicehwAddress} |
    """

    #saving: {{ COM &#92;n | {{

    #repeat this with every column
    for col in range(2,deviceTableWidth):
        #print (f"""{graphvizInput[0][col]}""")
        #if the column is PORT, then we're in the port section, and we want the next column as the port type
        if f"""{graphvizInput[0][col]}""" == "PORT":
            #the column to the right (col+1) is the port type, i.e. COM, IR, etc
            portSectionType = f"""{graphvizInput[0][col+1]}"""

            #strip the returns and newlines
            portSectionType = portSectionType.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("#", "")
            
            #portSectionType label. note opening curly brace (must be escaped with second curly brace)
            
            #if this isn't first section, close the previous section and open the next one
            if col > 2:
                #need double curly to escape the curly braces in the graphviz label
                #if this isn't first section, close the previous section
                label += f"""}}}} | {{"""

                        #if this isn't first section, close the previous section
            if col == 2:
                #need double curly to escape the curly brace in the graphviz label
                #if this is the first section, just open the next section
                label += f"""{{"""


            #open the port section type
            label += f"""{portSectionType} | {{"""            

            continue
        else:   

            next

        #for i in range(1,numPorts+1):
        #add 1 to the range because the array starts at 0
        for i in range(1,devicePortCapacity+1):
            #if devicePortConnectedDevice is empty, make will be an empty string
            if len(str(graphvizInput[i][col-1]).strip()) < 1:
                continue
            else:
                #if we're at the end of the first section, close the label
                if i > 1:
                    label += f"""|"""
               
                next
                
                #append to the label
                #two curly braces are needed to escape the curly braces in the graphviz label
                label += f"<{deviceID}{portSectionType}{i}> &#92;n {portSectionType}{i} &#92;n&#92;n"



            #get the port info (type, number, vlan, connected device) assume:
            #  user copied the data from the switch in the correct order, and with headers
            # expect array of arrays 0,1,2,3,4,5, 0-length of array
            
            #old way
            #devicePortType = str(graphvizInput[0][3]).strip()

            #clean this
            devicePortType = portSectionType.replace(" ", "").replace(")", "").replace("(", "").replace("-", "").replace("#", "")

            devicePortNum = str(graphvizInput[i][col-1]).strip()
            
            #if devicePortConnectedDevice is empty, make will be an empty string
            if len(str(graphvizInput[i][col]).strip()) < 1:
                devicePortConnectedDevice = ""
            else:
                devicePortConnectedDevice = str(graphvizInput[i][col]).strip()

            graphvizLineLabel = f"""{devicePortType}{devicePortNum}"""
            
            #print all the ports

            #the extra spaces are to make the graphviz output look nice, there's probably a better way to do this
            print(f"""{deviceID}:{deviceID}{portSectionType}{str(i)} -> "{devicePortConnectedDevice} ({devicePortType}{str(i)})" [label="         {str(graphvizLineLabel)}         "];""")
            #put a break every 12 ports


            

            print 
    #remove line breaks and add closing bracket
    #add trailing end quote and escape it with a backslash
    newLabel = str(label + "}} | SAM MYERS| AHT GLOBAL WEST\"];").replace('\n', '').replace('\r', '')
    #newLabel = str(label + "}} | SAM\"];")
    print (newLabel)
    print("}")


#generateGraphviz("asdf12340000", "MX75", "DE:AD:FA:CE:69:69", 24)

#readTab()


def main():
    #started time
    print (time.time())
    #check if the user entered a file path
    if len(sys.argv) > 1:
        #if the user entered a file path, use it
        fileName = sys.argv[1]      #get the file path from the command line
        print (f"""##Input File Name: {fileName}""")
        generateGraphviz(fileName, "asdf12340000", "MX75", "DE:AD:FA:CE:69:69", 24)
    else:
        fileName = input("Enter the file name: ")
        generateGraphviz(fileName, "asdf12340000", "MX75", "DE:AD:FA:CE:69:69", 24)
    
if __name__ == "__main__":
    #make a switch with 24 ports if they don't specify a number of ports
    main()


#python3 read_whole_section.py 53673_23_SW03.txt > 53673_23_SW03-viz.dot
#use the above command to consume a TAB delimited file and generate a dot file

# dot -Tsvg *.dot > /Users/sm/politis/53673_23_SW03-viz.svg
# use the above command to convert the dot file to svg

#chaining the commands together and doing a little loop:
# `for i in *.txt; do python3 read_whole_section.py $i >> $i.dot; dot -Tsvg $i.dot >> $i.svg; done`