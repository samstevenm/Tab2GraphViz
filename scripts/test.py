import csv

def readTAB():
    #ask use to specificy the file name
    fileName = input("Enter the file name: ")
    #open the file and read it

    with open(fileName, 'r') as f:
    #with open('data.txt', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        graphvizInput = []
        for row in reader:
            #print(row)
            
            #create an array of arrays
            graphvizInput.append(row)

    print (graphvizInput)
    lengthgraphvizInput = len(graphvizInput)
    print (lengthgraphvizInput)
    return graphvizInput

frontMatter = """
    digraph structs {
        node [shape=record];
        splines=true;
        overlap=false;
        rankdir="LR";
    """
#def generateGraphvizRow(graphvizInput):
    

def generateGraphviz(deviceID, deviceModel, hwAddress, devicePortCapacity):
    #call getTAB to get the data
    graphvizInput = readTAB()
    #get the length of the array, this is the number of ports (we hope)
    devicePortCapacity = len(graphvizInput)
    #print(graphvizInput)
    print (frontMatter)

    label = f"""
    "{deviceID}" [label="{deviceModel} | {deviceID} | {hwAddress} | {{ PORTS &#92;n 1-12| {{
    """
    
    #for i in range(1,numPorts+1):
    for i in range(1,devicePortCapacity+1):
        #append to the label
        label += f"<{deviceID}f{i}> {i}"
        #add a pipe if it's not the last port of a section
        if i % 12 != 0:
            #add a pipe if it's not the last port of the switch
            if i != devicePortCapacity:
                label += " | "
        
        #get the port info (type, number, vlan, connected device) substract 1 from i because the array starts at 0
        
        devicePortType = str(graphvizInput[i-1][0]).strip()
        devicePortNum = str(graphvizInput[i-1][1]).strip()
        devicePortVLAN = str(graphvizInput[i-1][2]).strip()
        devicePortConnectedDevice = str(graphvizInput[i-1][3]).strip()
        graphvizLineLabel = f"""{devicePortType} {devicePortNum} VLAN{devicePortVLAN}"""
        
        #print all the ports

        #the extra spaces are to make the graphviz output look nice, there's probably a better way to do this
        print(f"""{deviceID}:{deviceID}f{str(i)} -> "{devicePortConnectedDevice} ({str(i)})" [label="              {str(graphvizLineLabel)}              "];""")
        #put a break every 12 ports
        if i % 12 == 0 and i != 0:
            if i != devicePortCapacity:
                startNextPortSection = i + 1
                if devicePortCapacity - i > 12:
                    endNextPortSection = i + 12
                else:
                    endNextPortSection = devicePortCapacity
                label += f"""}}}} |-&#92;n-| {{ PORTS &#92;n {startNextPortSection}-{endNextPortSection} | {{"""
        print 
    #remove line breaks and add closing bracket
    newLabel = str(label + "}} | SAM MYERS\"];").replace('\n', '').replace('\r', '')
    #newLabel = str(label + "}} | SAM\"];")
    print (newLabel)
    print("}")


#make a switch with 24 ports if they don't specify a number of ports
generateGraphviz("asdf12340000", "MX75", "DE:AD:FA:CE:69:69", 24)

#readTAB()


