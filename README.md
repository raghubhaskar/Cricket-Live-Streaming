Cricket Live Streaming (Play-Cricket to OBS Studio to Youtube)

Welcome! This project provides cricket clubs with a completely free, amatuer-grade live streaming graphics overlay (similar to premium services like FrogBox). By intercepting the Bluetooth (BLE) signal broadcasted by the official ECB Play-Cricket Scorer app, this software automatically updates an on-screen TV graphic in OBS Studio in real-time. No manual score entry is required by the broadcast team—if it is scored on the tablet, it appears on the live stream.

🌟 Features
    • Zero-Delay Automation: Captures live score data directly from the scorer's tablet via Bluetooth.
    • Professional Graphics: Clean, modern lower-third overlay featuring team scores, wickets, overs, current batters, bowler figures, required run rates, and a dynamic ball-by-ball timeline.
    • Play-Cricket API Integration: Automatically fetches today's fixtures and populates team names.
    • Corner Logos: Easily display your club crest and sponsor logos on the stream.
    • Terminal Interface: Simple menu-driven application to manage the match state.

🛠️ Hardware Requirements
To run this setup at your club, you will need:
    1. A Scoring Tablet: Any Android or iOS tablet running the official Play-Cricket Scorer App.
    2. A Broadcasting PC: A computer to run OBS Studio and this Python software.
        ◦ Tested on: HP Elite Slice G2.
        ◦ Compatible with: Almost any PC running a Linux distribution (like Zorin OS, Ubuntu, or Debian) or a Raspberry Pi 3/4. The device must have a working Bluetooth adapter.
    3. Camera Equipment: A camera (e.g., a camcorder, IP camera, or webcam) connected to your PC to capture the match footage.

💻 Software & System Setup
1. Operating System Configuration (Linux)
This project requires Linux to utilize the BlueZ Bluetooth stack to emulate a generic scoreboard.
    • Ensure your Bluetooth radio is active.
    • Install the required Python DBus libraries. On Debian/Ubuntu/Zorin OS, run:
      Bash
      sudo apt update
      sudo apt install python3-dbus python3-gi python3-tk
2. Project Files
Clone this repository to your broadcasting PC. The project consists of the following core files:
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

🏏 Match Day Operation
Operating the system on match day is designed to be simple for club volunteers.
Step 1: Start the Server
  Execute the shell script from your terminal to unblock Bluetooth and launch the menu: 
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

⚠️ Important Note for Scorers: Do not pair the PC to the tablet using the tablet's main Android/iOS Bluetooth settings menu. The Play-Cricket app handles the Bluetooth connection entirely internally.

🤝 Contributing & Support
This project was built to help grassroots cricket clubs professionalize their media output without breaking the bank. If you are a developer, feel free to fork this repository, submit pull requests, or open issues if you find bugs.
Let's make local cricket look spectacular!
