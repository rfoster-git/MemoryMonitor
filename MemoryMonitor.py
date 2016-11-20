import subprocess, wmi, re, wmi, sys, datetime, time, os

processName = ""
processID = 0
interval_minutes = 5

def main():

    setupSaveDir()

    #continue until valid process is entered
    global processName
    result = 0

    #first argument is process name
    if len(sys.argv) > 1:
        processName = sys.argv[1]
        result = getProcessID()
    while(result == 0):
        processName = input("Enter process name: ")
        
        result = getProcessID()

    #second argument is custom interval (in minutes)
    global interval_minutes

    if len(sys.argv) > 2:   
        interval = sys.argv[2]
        if isinstance(interval, int):
            if interval >= 1 and interval <= 60:
                interval_minutes = interval
            #else default interval_minutes will be used
                
    monitorMemoryLoop()

def setupSaveDir():
    #get the path of the directory containing this script then change directory
    scriptPath = sys.path[0]
    dirName = os.path.dirname(scriptPath)
    os.chdir(dirName)

    #construct pathname and create directory for save files
    savePath = os.path.join(scriptPath, "MemoryMonitor")
    if not os.path.exists(savePath):
        os.makedirs(savePath)

    #change directory to save file directory
    os.chdir(savePath)

def getProcessID():
    
    cmd = 'WMIC PROCESS WHERE Name=\"' + processName + '\" get Caption, ProcessID, WorkingSetSize'

    try:
        processList = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        for listItem in processList.stdout:
            line = listItem.decode("utf-8")

            if "WorkingSetSize" in line:
                continue

            splitLine = re.split("\s{2,}", line)

            global processID
            processID = int(splitLine[1])

            break
    except:
        print("Error - could not identify processID, please ensure specified process is running")
        return 0
    else:
        print("Monitoring memory for process: " + processName + "; using interval of " + str(interval_minutes) + " minute(s)")
        return 1
        
def monitorMemoryLoop():

    filename = datetime.datetime.now().strftime("%Y.%m.%d_%H%M%S" + "_" + processName + "_memory.txt")

    savefile = open(str(filename),'w')

    running = True
    currentMinute = None
    
    while(running):
        memory = getMemory()
        now = datetime.datetime.now()
        nowFormatted = now.strftime("%Y-%m-%d %H:%M")
        
        if(memory != None):
            if (now.minute % interval_minutes == 0) and (now.minute != currentMinute):
                currentMinute = now.minute
                
                line = nowFormatted + ": " + formatMemory(memory)
            
                print(line)
                
                savefile.write( line + "\n" )
                savefile.flush()

            time.sleep(1)
        else:
            savefile.write( nowFormatted + ": " + " unable to determine process memory; process may have terminated" )
            savefile.flush()
            running = False

def getMemory():
    try:
        w = wmi.WMI('.')
        result = w.query("SELECT WorkingSetPrivate FROM Win32_PerfRawData_PerfProc_Process WHERE IDProcess=" + str(processID))
        subset = result[0]
        return round( float(int(subset.WorkingSetPrivate) / 1024 / 1024), 1 )
    except:
        return

def formatMemory(memoryInMB):
    if memoryInMB < 1024:
        return str(memoryInMB) + "MB"
    else:
        return str(memoryInMB / 1024) + "GB"
    
#======================================================================
main()


