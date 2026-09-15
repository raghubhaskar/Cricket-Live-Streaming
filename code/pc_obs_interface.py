import os
import json
import requests
import datetime
import threading
import sys
import tkinter as tk
from tkinter import messagebox

import dbus, dbus.mainloop.glib
from gi.repository import GLib

# BlueZ Constants
BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '5a0d6a15-b664-4304-8530-3a0ec53e5bc1'
UART_RX_CHARACTERISTIC_UUID =  'df531f62-fc0b-40ce-81b2-32a6262ea440'
LOCAL_NAME =                   'BT-Scoreboard'
SETTINGS_FILE =                "internal_settings.json"
STATE_FILE =                   "overlay_state.json"

# Import your existing BLE components
from example_advertisement import Advertisement, register_ad_cb, register_ad_error_cb
from example_gatt_server import Service, Characteristic, register_app_cb, register_app_error_cb

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {"site_id": "", "season": str(datetime.date.today().year), "api_key": "", "club_name": ""}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def clear_match_data():
    default_state = {
        "BTN": "TEAM", 
        "BTR": "0", 
        "BTW": "0", 
        "OVB": "0.0",
        "B1N": "BATTER 1", 
        "B1S": "0", 
        "B1B": "0", 
        "B1K": "0",
        "B2N": "BATTER 2", 
        "B2S": "0", 
        "B2B": "0", 
        "B2K": "0",
        "F1N": "BOWLER", 
        "F1S": "0-0 / 0.0",
        "CRR": "0.00", 
        "RRR": "0.00", 
        "BTT": "0", 
        "COV": ""
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(default_state, f)
    input("\n[✔] Match scorecard data cleared. Press Enter to return to menu...")

def fetch_fixtures(settings):
    if not settings.get('api_key') or not settings.get('site_id'):
        input("\n[!] Error: Site ID and API Key must be configured first. Press Enter...")
        return

    url = f"https://play-cricket.com/api/v2/matches.json?site_id={settings['site_id']}&season={settings['season']}&api_token={settings['api_key']}"
    try:
        response = requests.get(url)
        data = response.json()
        today = datetime.date.today().strftime("%d/%m/%Y")
        
        matches = [m for m in data.get('matches', []) if m.get('match_date') == today]
        
        if not matches:
            input(f"\n[-] No fixtures found for {today}. Press Enter to return...")
            return
            
        print(f"\n--- Fixtures for {today} ---")
        for idx, match in enumerate(matches):
            home_club = match.get('home_club_name', 'Unknown')
            home_team = match.get('home_team_name', 'Unknown')
            away_club = match.get('away_club_name', 'Unknown')
            away_team = match.get('away_team_name', 'Unknown')
            print(f"{idx + 1}. [{home_club} - {home_team} vs {away_club} - {away_team}]")
            
        sel = input("\nSelect a match to load (or 0 to cancel): ")
        if sel.isdigit() and 0 < int(sel) <= len(matches):
            selected = matches[int(sel)-1]
            match_data = {
                "home_team": f"{selected.get('home_club_name')} - {selected.get('home_team_name')}",
                "away_team": f"{selected.get('away_club_name')} - {selected.get('away_team_name')}",
                "match_id": selected.get('id')
            }
            with open(STATE_FILE, 'w') as f:
                json.dump(match_data, f)
            input(f"\n[✔] Loaded: {match_data['home_team']} vs {match_data['away_team']}\nPress Enter...")
            
    except Exception as e:
        input(f"\n[!] API Error: {e}\nPress Enter to return...")

def set_demo_match():
    print("\n--- Setup Demo/Friendly Match ---")
    
    # Prompt for input, defaulting to generic names if left blank
    home_team = input("Enter Home Team Name [Home Team]: ") or "Home Team"
    away_team = input("Enter Away Team Name [Away Team]: ") or "Away Team"
    
    match_data = {
        "home_team": home_team,
        "away_team": away_team,
        "match_id": "DEMO"
    }
    
    with open(STATE_FILE, 'w') as f:
        json.dump(match_data, f)
        
    input(f"\n[✔] Loaded Demo Game: {home_team} vs {away_team}\nPress Enter to return...")

def show_mismatch_popup(received_name, home_name, away_name):
    def popup_thread():
        root = tk.Tk()
        root.withdraw() 
        root.attributes('-topmost', True) 
        messagebox.showwarning(
            "Team Name Mismatch", 
            f"BLE received team name: '{received_name}'\n\n"
            f"This does not match your selected fixture:\n"
            f"Home: {home_name}\nAway: {away_name}\n\n"
            "Data recording will continue in the background.",
            parent=root
        )
        root.destroy()
    threading.Thread(target=popup_thread, daemon=True).start()

class RxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID, ['write'], service)

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
    def WriteValue(self, value, options):
        try:
            raw_data = bytearray(value).decode('utf-8').strip('\r\n')
            if len(raw_data) >= 3:
                slot_id = raw_data[:3]
                slot_value = raw_data[3:]
                if slot_value == " ": slot_value = ""
                
                state = {}
                if os.path.exists(STATE_FILE):
                    with open(STATE_FILE, 'r') as f:
                        state = json.load(f)
                
                # Validation Logic for Team Names
                if slot_id in ['BTN', 'FTN'] and slot_value:
                    home = state.get('home_team', '')
                    away = state.get('away_team', '')
                    
                    if home and away:
                        # Normalize strings by converting to lowercase and stripping spaces and hyphens
                        val_clean = slot_value.lower().replace(" ", "").replace("-", "")
                        home_clean = home.lower().replace(" ", "").replace("-", "")
                        away_clean = away.lower().replace(" ", "").replace("-", "")
                        
                        # Loose matching check on cleaned strings
                        if (val_clean not in home_clean and home_clean not in val_clean) and \
                           (val_clean not in away_clean and away_clean not in val_clean):
                            
                            # Only warn once per slot ID to avoid spamming popups
                            if not state.get(f'{slot_id}_warning_shown'):
                                show_mismatch_popup(slot_value, home, away)
                                state[f'{slot_id}_warning_shown'] = True

                state[slot_id] = slot_value
                
                with open("state_temp.json", "w") as f:
                    json.dump(state, f)
                os.replace("state_temp.json", STATE_FILE)
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {slot_id} -> {slot_value}")
        except Exception as e:
            pass

class UartService(Service):
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(RxCharacteristic(bus, 1, self))

class UartApplication(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
        self.services.append(UartService(bus, 0))
        
    def get_path(self): 
        return dbus.ObjectPath(self.path)
        
    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response

class UartAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True

def run_ble():
    clear_screen()
    print("\n[📡] BLE Started. Waiting for Play-Cricket Scorer to connect... (Press Ctrl+C to stop)")
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'), DBUS_OM_IFACE)
    adapter = next((o for o, props in remote_om.GetManagedObjects().items() 
                   if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props), None)

    if not adapter:
        input("[!] BLE adapter not found. Press Enter...")
        return

    app = UartApplication(bus)
    adv = UartAdvertisement(bus, 0)
    
    dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), GATT_MANAGER_IFACE).RegisterApplication(
        app.get_path(), {}, reply_handler=register_app_cb, error_handler=register_app_error_cb)
    dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter), LE_ADVERTISING_MANAGER_IFACE).RegisterAdvertisement(
        adv.get_path(), {}, reply_handler=register_ad_cb, error_handler=register_ad_error_cb)

    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        print("\n[⏹] BLE Stopped.")

def main_menu():
    while True:
        clear_screen()
        settings = load_settings()
        print(f"=============================================")
        print(f" 🏏 Date: {datetime.date.today().strftime('%d %B %Y')}")
        print(f" 🏏 Club: {settings.get('club_name', 'Not Set')} | Season: {settings.get('season')}")
        print(f"=============================================")
        print("1. Record New Match (Clear Scorecard)")
        print("2. Select Fixture (Play-Cricket API)")
        print("3. Select Demo/Friendly Match")
        print("4. Enter Club Site ID, Season & API Key")
        print("5. Start Scoring (Enable Bluetooth Listener)")
        print("6. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == '1':
            clear_match_data()
        elif choice == '2':
            clear_screen()
            fetch_fixtures(settings)
        elif choice == '3':
            clear_screen()
            set_demo_match()
        elif choice == '4':
            clear_screen()
            settings['site_id'] = input(f"Enter Site ID [{settings['site_id']}]: ") or settings['site_id']
            settings['season'] = input(f"Enter Season [{settings['season']}]: ") or settings['season']
            settings['api_key'] = input(f"Enter API Key [{settings['api_key']}]: ") or settings['api_key']
            settings['club_name'] = input(f"Enter Club Name [{settings['club_name']}]: ") or settings['club_name']
            save_settings(settings)
            input("\n[✔] Settings saved. Press Enter...")
        elif choice == '5':
            run_ble()
        elif choice == '6':
            clear_screen()
            sys.exit()

if __name__ == '__main__':
    main_menu()