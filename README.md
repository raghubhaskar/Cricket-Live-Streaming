Cricket Live Streaming (Play-Cricket to OBS Studio to Youtube)
----------------------------------------------------------------------------------------

Welcome! This project provides cricket clubs with a completely free, amatuer-grade live streaming graphics overlay (similar to premium services like FrogBox). By intercepting the Bluetooth (BLE) signal broadcasted by the official ECB Play-Cricket Scorer app, this software automatically updates an on-screen TV graphic in OBS Studio in real-time. No manual score entry is required by the broadcast team—if it is scored on the tablet, it appears on the live stream.

🌟 **Features**
    • Zero-Delay Automation: Captures live score data directly from the scorer's tablet via Bluetooth.
    
    • Professional Graphics: Clean, modern lower-third overlay featuring team scores, wickets, overs, current batters, bowler figures, required run rates, and a dynamic ball-by-ball timeline.
    
    • Play-Cricket API Integration: Automatically fetches today's fixtures and populates team names.
    
    • Corner Logos: Easily display your club crest and sponsor logos on the stream.
    
    • Terminal Interface: Simple menu-driven application to manage the match state.


🛠️ **Hardware Requirements**
To run this setup at your club, you will need:
    1. A Scoring Tablet: Any Android or iOS tablet running the official Play-Cricket Scorer App.
    2. A Broadcasting PC: A computer to run OBS Studio and this Python software.
        ◦ Tested on: HP Elite Slice G2.
        ◦ Compatible with: Almost any PC running a Linux distribution (like Zorin OS, Ubuntu, or Debian) or a Raspberry Pi 3/4. The device must have a working Bluetooth adapter.
    3. Camera Equipment: A camera (e.g., a camcorder, IP camera, or webcam) connected to your PC to capture the match footage. I am using an IP camera which would be connected to the clubs wifi, so will the PC running OBS Studio and the python code.


💻 **Software & System Setup**
1. Operating System Configuration (Linux)
This project requires Linux to utilize the BlueZ Bluetooth stack to emulate a generic scoreboard.
    • Ensure your Bluetooth radio is active.
    • Install the required Python DBus libraries. On Debian/Ubuntu/Zorin OS, run:
      Bash
      sudo apt update
      sudo apt install python3-dbus python3-gi python3-tk
2. Project Files - Clone this repository to your broadcasting PC. The project consists of the following core files:
    • pc_obs_interface.py: The main backend application that creates the BLE server and provides the user menu. 
    • overlay.html: The professional lower-third graphics engine. 
    • overlay_state.json: The local data file bridging Python and HTML. 
    • logos_overlay.html: A static full-screen canvas for club and sponsor logos. 
    • stream_record.sh: The startup script to initialize Bluetooth and launch the application. 
3. OBS Studio Configuration
    1. Open OBS Studio and set up your video capture device (your camera).
    2. Add a new Browser Source and name it "Cricket Scoreboard".
    3. Check Local file, click Browse, and select overlay.html. 
    4. Set the Width to 1920 and Height to 1080 (or match your stream resolution).
    5. Check Refresh browser when scene becomes active and click OK.
    6. Repeat steps 2-5 to add logos_overlay.html as a second Browser Source, ensuring it sits at the top of your Sources list. 


🏏 **Match Day Operation**
Operating the system on match day is designed to be simple for club volunteers.
Step 1: Start the Server - Execute the shell script from your terminal to unblock Bluetooth and launch the menu: 
  Bash ./stream_record.sh
  
Step 2: Configure the Match
  Using the on-screen terminal menu:
    • Press 4 to enter your club's Play-Cricket Site ID and API Key (you only need to do this once).
    • Press 2 to fetch the day's fixtures from Play-Cricket and select your match. This will auto-populate the team names on the stream.
    • (Alternatively, press 3 to manually type in team names for a friendly match).
    • Press 1 to clear any old data from overlay_state.json. 
Step 3: Connect the Scorer
    1. On the PC terminal, press 5 to start the BLE listener. The terminal will state it is waiting for a connection. 
    2. On the scorer's tablet, open the Play-Cricket Scorer App.
    3. Start the match, open the menu, and go to Match Settings > External Scoreboard.
    4. Select Manufacturer: Generic.
    5. Select BT-Scoreboard from the device list.
    6. The app will say "Connected". As the scorer logs deliveries, the OBS graphics will update instantly!

<img width="1920" height="1200" alt="51" src="https://github.com/user-attachments/assets/0bff38cb-e712-4404-b800-adcc53cac4be" />
<img width="1920" height="1200" alt="52" src="https://github.com/user-attachments/assets/083a5f47-702d-4942-a26c-c516dc46e517" />
Sample output from play-cricket app which is displayed by the python script
<img width="731" height="596" alt="image" src="https://github.com/user-attachments/assets/537d4f02-36aa-405b-b398-b035e253720b" />


🤝 Thank you very much to the team of https://buildyourownscoreboard.wordpress.com/ for the inspiration and the BLE scripts to help better understand what the play-cricket app is really doing.

⚠️ Important Note for Scorers: Do not pair the PC to the tablet using the tablet's main Android/iOS Bluetooth settings menu. The Play-Cricket app handles the Bluetooth connection entirely internally.

🤝 Contributing & Support
This project was built to help grassroots cricket clubs professionalize their media output without breaking the bank. If you are a developer, feel free to fork this repository, submit pull requests, or open issues if you find bugs.
Let's make local cricket look spectacular!


HOW IT WORKS BEHIND THE SCENES
-------------------------------------------------------------------------------------------------
The live graphics system you have built operates on a highly efficient, one-way data pipeline. It acts as a bridge between the physical Bluetooth radio on your PC and the visual rendering engine inside OBS Studio. Here is the step-by-step breakdown of exactly how that data flows from the scorer's fingertips to the live stream.

1. The BLE Transmission (Tablet → Python) - When the scorer records a delivery on the Play-Cricket app, the tablet immediately broadcasts that new information over Bluetooth Low Energy (BLE).
    • The pc_obs_interface.py script acts as a BLE GATT server, keeping a specific "receive" slot open (defined by the UART_RX_CHARACTERISTIC_UUID). 
    • The app sends data to this slot in the form of raw bytes, formatted as a 3-letter code followed by the value (for example, BTR150 to indicate the Batting Team Runs are 150). 

2. Data Processing (Python → JSON) = As soon as those bytes hit your PC's Bluetooth adapter, the Python script intercepts them.
    • The WriteValue function in the script decodes the raw bytes into standard text. 
    • It splits the string, separating the 3-letter identifier (BTR) from the actual value (150). 
    • To safely store this, the script opens the overlay_state.json file. 
    • It updates the specific dictionary key (e.g., changing "BTR": "0" to "BTR": "150") and saves the file. To prevent OBS from trying to read the file at the exact millisecond Python is writing to it, the script safely writes to a temporary file (state_temp.json) before instantly replacing the main file. 

3. The Web Polling (JSON → HTML) - The HTML file does not passively wait to be told there is new data; it actively checks for it.
    • The overlay.html file contains a JavaScript setInterval loop that runs twice every second (every 500 milliseconds). 
    • During each loop, it executes a fetch('overlay_state.json') command, explicitly telling the browser engine not to cache the result (cache: "no-store") so it always grabs the freshest data. 
    • The script reads the JSON dictionary and maps the keys directly to the HTML elements on the screen, updating the text values instantly. 

4. The Broadcast (HTML → OBS) - OBS Studio has a built-in Chromium browser engine (the same technology that powers Google Chrome).
    • When you add overlay.html as a Browser Source, OBS is simply running a transparent, full-screen webpage over your video feed. 
    • As the JavaScript updates the HTML text on that page, the OBS Chromium engine instantly re-renders those pixels, showing the new score to your viewers.
By keeping the Bluetooth receiving logic (Python) entirely separate from the graphics rendering logic (HTML/OBS) and using a simple text file (JSON) as the middleman, the system remains incredibly lightweight and crash-resistant.



HELP ON RUNNING THE IP CAM FEED ON OBS STUDIO
-------------------------------------------------------------------------------------------------
🎥 Adding an IP Camera via RTSP to OBS Studio
Using an IP (Internet Protocol) camera is one of the most robust and cost-effective ways to broadcast cricket. Because they transmit video over standard network cables (Ethernet), you can mount the camera high up on a clubhouse roof or sight screen, far away from the broadcasting PC, without losing video quality.

The standard method for pulling an IP camera feed into broadcasting software is through RTSP (Real-Time Streaming Protocol).

**Phase 1: Physical Installation & Networking**
Choose your Vantage Point: For cricket, the best angles are elevated. Mount the camera either straight down the wicket (from behind the bowler's arm) or high up square of the wicket. Ensure the camera is weatherproof (look for an IP66 or IP67 rating).

Use Power over Ethernet (PoE): While you can use Wi-Fi, a wired connection is strongly recommended for live streaming. A PoE switch or injector allows you to send both power and a stable data connection to the camera over a single Cat5e or Cat6 Ethernet cable, eliminating the need for a separate power outlet on the roof.

Connect to the Network: Run the Ethernet cable from the camera into your PoE switch, and connect that switch to the same local network (router) as your broadcasting PC.

**Phase 2: Camera Configuration**
To get the video feed, you need to find the camera's unique network address and format its RTSP link.

Find the IP Address: Use your router's admin panel or the camera manufacturer’s discovery tool (e.g., SADP for Hikvision, ConfigTool for Dahua) to find the IP address assigned to the camera.

Set a Static IP: Log into the camera’s web interface by typing its IP address into a web browser. Navigate to the network settings and change the IP configuration from DHCP to Static. This ensures the IP address never changes when the system restarts.

Format the RTSP URL: Every camera brand has a specific RTSP URL structure. You will need the camera's IP address, your admin username, and your password. A typical RTSP URL looks like this:
rtsp://username:password@192.168.1.100:554/stream1
(Check your camera manual or an online RTSP database like iSpyConnect for your specific brand's format).

**Phase 3: Capturing the Stream in OBS Studio**
Once your camera is powered on and you have your RTSP URL, adding it to OBS Studio is straightforward.

1. Open OBS Studio.
2. In the Sources panel, click the + button and select Media Source (Do not choose Video Capture Device).
3. Name the source (e.g., "Main Roof Camera") and click OK.
4. In the properties window, uncheck the box that says Local File.

Two new fields will appear:
Input: Paste your complete RTSP URL here.
Input Format: Leave this blank.
Adjust Network Buffering: By default, OBS sets this to 2 MB. If your video stutters or drops frames, you can increase this value. If you want lower latency (less delay between real life and the stream), lower it to 1 MB.

5. Click OK.

After a few seconds of buffering, your IP camera feed will appear on the OBS canvas. You can now resize it, place it beneath your logos_overlay.html, and place your overlay.html scoreboard graphic on top of it.

My OBS Studio looks like this (Do not mind the feed as I was testing with my home IP camera)
<img width="1284" height="933" alt="image" src="https://github.com/user-attachments/assets/f2b2d459-e02d-4973-adde-15bcc6f5f451" />
Recomendation: Reolink rlc-811a - cheap and can be zoomed in and panned.


🔑 Acquiring a Play-Cricket API Key (Optional)
----------------------------------------------------------------------------------------
To utilize Option 2 in the application menu (which automatically fetches today's fixtures and populates the team names), your club will need a Play-Cricket API Key.

Please note that this step is not mandatory. If you do not have an API key, you can simply use Option 3 in the menu to manually enter the Home and Away team names for your broadcast.

If your club wishes to automate fixture retrieval:

Raise a Support Ticket: A senior administrative member of your club (e.g., the Chairman, Secretary, or Play-Cricket Main Administrator) must raise a support ticket directly with the Play-Cricket Helpdesk.

Request Access: In the ticket, request a "Club API Token" for the purpose of integrating live broadcast graphics.

Configuration: Once provided, enter this token along with your Club Site ID using Option 4 in the Python script's main menu. The system will save these details securely for future use.
