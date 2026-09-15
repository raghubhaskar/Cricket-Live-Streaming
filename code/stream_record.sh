#!/bin/bash

# Ensure Bluetooth radio is unblocked
sudo rfkill unblock bluetooth

bluetoothctl -- agent off
bluetoothctl -- power on
bluetoothctl -- discoverable on
bluetoothctl -- pairable on
bluetoothctl -- agent NoInputNoOutput
bluetoothctl -- default-agent

echo "Bluetooth configured. Starting Python listener..."

python3 pc_obs_interface.py