#!/usr/bin/env python3
"""Home Manager: Control Apple HomeKit devices from Python."""

import os
import sys
import json
import tempfile
from textwrap import dedent
import questionary
from dotenv import load_dotenv
from rich.console import Console
from prompt_toolkit.styles import Style

try:
    from homekit import Controller
    HOMEKIT_ENABLED = True
except ImportError:
    HOMEKIT_ENABLED = False

# Load environment variables
load_dotenv()

# Initialize rich console
console = Console()

# Define menu style for questionary
menu_style = Style.from_dict({
    'selected': 'bold fg:cyan bg:#333333',
})

# HomeKit storage
HOMEKIT_STORAGE_DIR = '.homekit'
os.makedirs(HOMEKIT_STORAGE_DIR, exist_ok=True)

def discover_devices():
    """Discover unpaired HomeKit devices on the network."""
    if not HOMEKIT_ENABLED:
        console.print("[red]❌ HomeKit library not available. Install with: pip install homekit[IP][/red]")
        return []
    
    try:
        controller = Controller()
        devices = controller.discover(timeout=10)
        unpaired = [d for d in devices if d.get('sf') == '1']  # status flag 1 means unpaired
        return unpaired
    except Exception as e:
        console.print(f"[red]❌ Error discovering devices: {e}[/red]")
        return []

def pair_device(device_id, setup_code, alias):
    """Pair with a HomeKit device."""
    if not HOMEKIT_ENABLED:
        return False
    
    try:
        controller = Controller()
        pairing_file = os.path.join(HOMEKIT_STORAGE_DIR, f"{alias}.json")
        controller.init_pairing_data_file(pairing_file)
        
        # Discover the device
        devices = controller.discover(timeout=10)
        device = next((d for d in devices if d['id'] == device_id), None)
        
        if not device:
            console.print("[red]❌ Device not found.[/red]")
            return False
        
        controller.perform_pairing(device, setup_code, alias)
        console.print(f"[green]✅ Paired with {alias}.[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Pairing failed: {e}[/red]")
        return False

def list_paired_devices():
    """List paired HomeKit devices."""
    if not HOMEKIT_ENABLED:
        return []
    
    devices = []
    for file in os.listdir(HOMEKIT_STORAGE_DIR):
        if file.endswith('.json'):
            alias = file[:-5]  # remove .json
            devices.append(alias)
    return devices

def get_accessories(alias):
    """Get accessories for a paired device."""
    if not HOMEKIT_ENABLED:
        return {}
    
    try:
        controller = Controller()
        pairing = controller.get_pairing(alias)
        accessories = pairing.list_accessories_and_characteristics()
        return accessories
    except Exception as e:
        console.print(f"[red]❌ Error getting accessories: {e}[/red]")
        return {}

def control_characteristic(alias, aid, cid, value):
    """Control a characteristic of a device."""
    if not HOMEKIT_ENABLED:
        return False
    
    try:
        controller = Controller()
        pairing = controller.get_pairing(alias)
        pairing.put_characteristics([(aid, cid, value)])
        console.print(f"[green]✅ Set characteristic {aid}.{cid} to {value}.[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Error controlling characteristic: {e}[/red]")
        return False

def manage_devices():
    """Manage paired devices."""
    while True:
        devices = list_paired_devices()
        if not devices:
            console.print("[yellow]⚠️  No paired devices found.[/yellow]")
            return
        
        choices = devices + ["⬅️  Back"]
        selected = questionary.select("Select device to manage:", choices, style=menu_style).ask()
        
        if selected == "⬅️  Back" or selected is None:
            return
        
        alias = selected
        
        while True:
            console.print(f"\n[bold yellow]Managing device:[/bold yellow] [green]'{alias}'[/green]")
            
            accessories = get_accessories(alias)
            if not accessories:
                console.print("[red]❌ No accessories found.[/red]")
                break
            
            # Display accessories
            console.print("\n[bold cyan]Accessories:[/bold cyan]")
            for aid, accessory in accessories.items():
                console.print(f"  Accessory {aid}: {accessory.get('name', 'Unknown')}")
                services = accessory.get('services', [])
                for service in services:
                    service_type = service.get('type', 'Unknown')
                    characteristics = service.get('characteristics', [])
                    for char in characteristics:
                        cid = char.get('iid')
                        char_type = char.get('type', 'Unknown')
                        value = char.get('value', 'N/A')
                        perms = char.get('permissions', [])
                        if 'pw' in perms:  # writable
                            console.print(f"    {aid}.{cid}: {char_type} = {value} (writable)")
                        else:
                            console.print(f"    {aid}.{cid}: {char_type} = {value}")
            
            choices = [
                "🔄 Refresh Accessories",
                "🎛️  Control Characteristic",
                "🗑️  Unpair Device",
                "⬅️  Back"
            ]
            
            selected_action = questionary.select("Choose action:", choices, style=menu_style).ask()
            
            if selected_action == "🔄 Refresh Accessories":
                continue
            elif selected_action == "🎛️  Control Characteristic":
                # Simple control: ask for aid.cid and value
                char_input = questionary.text("Enter characteristic (format: aid.cid):").ask()
                if char_input:
                    try:
                        aid_str, cid_str = char_input.split('.')
                        aid = int(aid_str)
                        cid = int(cid_str)
                        value_input = questionary.text("Enter value (true/false for bool, number for others):").ask()
                        if value_input.lower() in ['true', 'false']:
                            value = value_input.lower() == 'true'
                        else:
                            value = float(value_input) if '.' in value_input else int(value_input)
                        control_characteristic(alias, aid, cid, value)
                    except ValueError:
                        console.print("[red]❌ Invalid format. Use aid.cid[/red]")
            elif selected_action == "🗑️  Unpair Device":
                if questionary.confirm(f"Are you sure you want to unpair {alias}?").ask():
                    pairing_file = os.path.join(HOMEKIT_STORAGE_DIR, f"{alias}.json")
                    if os.path.exists(pairing_file):
                        os.remove(pairing_file)
                        console.print(f"[green]✅ Unpaired {alias}.[/green]")
                        break
                    else:
                        console.print("[red]❌ Pairing file not found.[/red]")
            elif selected_action == "⬅️  Back":
                break

def interactive_menu():
    console.print("\n[bold green]🏠 Home Manager[/bold green]", justify="center")
    console.print("[dim]Control your Apple HomeKit devices[/dim]\n", justify="center")
    
    while True:
        choices = [
            "🔍 Discover Devices",
            "🔗 Pair Device",
            "📱 Manage Devices",
            "🚪 Exit"
        ]
        
        selected = questionary.select("Main Menu:", choices, style=menu_style).ask()
        
        if selected == "🔍 Discover Devices":
            devices = discover_devices()
            if devices:
                console.print(f"\n[bold cyan]Found {len(devices)} unpaired device(s):[/bold cyan]")
                for i, device in enumerate(devices, 1):
                    console.print(f"[magenta]{i}.[/magenta] {device['name']} (ID: {device['id']})")
            else:
                console.print("[yellow]⚠️  No unpaired devices found.[/yellow]")
        elif selected == "🔗 Pair Device":
            devices = discover_devices()
            if not devices:
                console.print("[yellow]⚠️  No unpaired devices found. Discover first.[/yellow]")
                continue
            
            console.print("\n[bold cyan]Available devices:[/bold cyan]")
            for i, device in enumerate(devices, 1):
                console.print(f"[magenta]{i}.[/magenta] {device['name']} (ID: {device['id']})")
            
            device_choice = questionary.text("Enter device number to pair:").ask()
            try:
                idx = int(device_choice) - 1
                device = devices[idx]
                setup_code = questionary.text("Enter setup code (XXX-XX-XXX):").ask()
                alias = questionary.text("Enter alias for device:").ask()
                if setup_code and alias:
                    pair_device(device['id'], setup_code, alias)
            except (ValueError, IndexError):
                console.print("[red]❌ Invalid selection.[/red]")
        elif selected == "📱 Manage Devices":
            manage_devices()
        elif selected == "🚪 Exit":
            console.print("[bold green]👋 Goodbye![/bold green]")
            break

def main():
    if not HOMEKIT_ENABLED:
        console.print("[red]❌ HomeKit library not installed. Please install with: pip install homekit[IP][/red]")
        sys.exit(1)
    
    interactive_menu()

if __name__ == '__main__':
    main()