# Home Manager

A Python application to control Apple HomeKit devices and Philips Hue lights from the command line.

## Features

- Discover HomeKit devices on the network
- Pair with HomeKit accessories (including those already paired to other controllers like Apple Home)
- List paired devices and their accessories
- Control device characteristics (turn lights on/off, adjust thermostats, etc.)
- Discover and authenticate Philips Hue Bridges
- Control Philips Hue lights directly (without interfering with HomeKit pairings)
- Interactive menu-driven interface

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jower999/home-manager.git
   cd home-manager
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment file:
   ```bash
   cp .env.example .env
   ```

## Usage

Run the application:
```bash
python home-manager.py
```

Use the interactive menu to:
- Discover devices on the network
- Pair with devices using their setup codes
- View and control paired devices
- Set up Philips Hue Bridges
- Control Hue lights directly

**Note:** HomeKit allows devices to be paired to multiple controllers. To manage devices already in your Apple Home setup, pair them with this application by putting the device in pairing mode and using its setup code.

### Putting a Device in Pairing Mode

Devices that are already paired won't appear in discovery unless they're in pairing mode. To add this controller:

1. Check your device's manual for pairing instructions.
2. Common methods:
   - Press and hold the pairing/setup button for 5-10 seconds.
   - Reset the device (may require removing/reinserting batteries or power cycling).
3. The device will start advertising and appear in the discovery list.
4. Use the setup code (usually found on the device or packaging) to pair it.

### Philips Hue Support

For Philips Hue lights, you can control them directly via the Hue Bridge API without affecting your HomeKit setup:

1. Use "Setup Hue Bridge" to discover and authenticate your bridge.
2. Press the link button on the bridge when prompted.
3. Use "Manage Hue Lights" to control your lights.

This allows you to manage Hue lights from the script while keeping them in Apple Home.

## Requirements

- Python 3.7+
- Access to HomeKit devices on the local network
- HomeKit setup codes for pairing
- Philips Hue Bridge for Hue light control

## License

See LICENSE file.