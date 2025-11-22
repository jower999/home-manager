# Home Manager

A Python application to control Apple HomeKit devices from the command line.

## Features

- Discover HomeKit devices on the network
- Pair with HomeKit accessories
- List paired devices and their accessories
- Control device characteristics (turn lights on/off, adjust thermostats, etc.)
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
- Discover unpaired devices
- Pair with devices using their setup codes
- View and control paired devices

## Requirements

- Python 3.7+
- Access to HomeKit devices on the local network
- HomeKit setup codes for pairing

## License

See LICENSE file.