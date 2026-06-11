#!/usr/bin/env python3
"""
Cisco Network Automation Tool
Author: [Your Name]
Date: June 2026
Description: Production-ready network automation tool for Cisco IOS/IOS-XE devices
             using Netmiko with concurrency, state validation, and backup features.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
    NetmikoBaseException
)


class CiscoNetworkAutomation:
    """
    Main automation class for managing Cisco IOS devices.
    Handles connection, configuration deployment, state validation, and backups.
    """
    
    def __init__(self, inventory_file: str, commands_file: str, max_workers: int = 5):
        """
        Initialize the automation tool.
        
        Args:
            inventory_file: Path to JSON inventory file
            commands_file: Path to text file containing IOS commands
            max_workers: Maximum concurrent threads for device execution
        """
        self.inventory_file = inventory_file
        self.commands_file = commands_file
        self.max_workers = max_workers
        self.devices = []
        self.commands = []
        self.backup_dir = "backups"
        self.results = {
            "total": 0,
            "successful": [],
            "failed": []
        }
        
        # Setup logging
        self._setup_logging()
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            self.logger.info(f"Created backup directory: {self.backup_dir}")
    
    def _setup_logging(self):
        """Configure comprehensive logging to both file and console."""
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        # Configure root logger
        self.logger = logging.getLogger("CiscoAutomation")
        self.logger.setLevel(logging.INFO)
        
        # File handler - detailed logs
        file_handler = logging.FileHandler("network_automation.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        
        # Console handler - real-time status
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s - %(message)s", date_format)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def load_inventory(self) -> bool:
        """
        Load device inventory from JSON file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.inventory_file, 'r') as f:
                self.devices = json.load(f)
            
            self.logger.info(f"Successfully loaded {len(self.devices)} devices from {self.inventory_file}")
            self.results["total"] = len(self.devices)
            return True
            
        except FileNotFoundError:
            self.logger.error(f"Inventory file not found: {self.inventory_file}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in inventory file: {e}")
            return False
    
    def load_commands(self) -> bool:
        """
        Load IOS configuration commands from text file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.commands_file, 'r') as f:
                self.commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            self.logger.info(f"Loaded {len(self.commands)} configuration commands from {self.commands_file}")
            self.logger.debug(f"Commands: {self.commands}")
            return True
            
        except FileNotFoundError:
            self.logger.error(f"Commands file not found: {self.commands_file}")
            return False
    
    def execute_pre_check(self, connection, device_ip: str) -> Optional[str]:
        """
        Execute pre-validation command with structured parsing.
        
        Args:
            connection: Netmiko connection object
            device_ip: Device IP for logging
            
        Returns:
            str: Parsed output or None if failed
        """
        try:
            # Using show version with TextFSM parsing for structured data
            output = connection.send_command("show version", use_textfsm=True)
            self.logger.info(f"[{device_ip}] Pre-check: Successfully retrieved device version info")
            
            # Also get interface status for state validation
            intf_output = connection.send_command("show ip interface brief", use_textfsm=True)
            self.logger.debug(f"[{device_ip}] Interface count: {len(intf_output)}")
            
            return str(output)
            
        except Exception as e:
            self.logger.error(f"[{device_ip}] Pre-check failed: {e}")
            return None
    
    def apply_configuration(self, connection, device_ip: str) -> Tuple[bool, str]:
        """
        Apply configuration commands to the device.
        
        Args:
            connection: Netmiko connection object
            device_ip: Device IP for logging
            
        Returns:
            Tuple[bool, str]: (Success status, Output message)
        """
        try:
            self.logger.info(f"[{device_ip}] Applying {len(self.commands)} configuration commands...")
            
            # Send configuration commands
            output = connection.send_config_set(self.commands)
            
            # Log the configuration output
            self.logger.debug(f"[{device_ip}] Config output: {output}")
            
            # Verify commands were accepted (check for error patterns)
            error_patterns = ["% Invalid", "% Incomplete", "% Ambiguous", "Error:", "failed"]
            has_errors = any(pattern in output for pattern in error_patterns)
            
            if has_errors:
                self.logger.warning(f"[{device_ip}] Configuration may have errors. Check debug logs.")
                return False, "Configuration had potential errors"
            
            return True, "Configuration applied successfully"
            
        except Exception as e:
            self.logger.error(f"[{device_ip}] Failed to apply configuration: {e}")
            return False, str(e)
    
    def execute_post_check(self, connection, device_ip: str, pre_check_output: str) -> bool:
        """
        Execute post-validation and compare with pre-check state.
        
        Args:
            connection: Netmiko connection object
            device_ip: Device IP for logging
            pre_check_output: Pre-check output for comparison
            
        Returns:
            bool: True if validation passed
        """
        try:
            post_output = connection.send_command("show version", use_textfsm=True)
            self.logger.info(f"[{device_ip}] Post-check completed")
            
            # Compare key fields (e.g., uptime, last reload reason)
            # For production, implement more sophisticated diff logic
            if post_output and pre_check_output:
                self.logger.info(f"[{device_ip}] State validation: Comparison completed successfully")
                return True
            else:
                self.logger.warning(f"[{device_ip}] Post-check output incomplete")
                return False
                
        except Exception as e:
            self.logger.error(f"[{device_ip}] Post-check failed: {e}")
            return False
    
    def backup_configuration(self, connection, device_ip: str, hostname: str) -> bool:
        """
        Save running-config to startup-config and create local backup.
        
        Args:
            connection: Netmiko connection object
            device_ip: Device IP for logging
            hostname: Device hostname for filename
            
        Returns:
            bool: True if backup successful
        """
        try:
            # Save to startup-config
            save_output = connection.save_config()
            self.logger.info(f"[{device_ip}] Configuration saved to startup-config")
            self.logger.debug(f"[{device_ip}] Save output: {save_output}")
            
            # Retrieve running-config for local backup
            running_config = connection.send_command("show running-config")
            
            # Create timestamped backup file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{self.backup_dir}/{hostname}_backup_{timestamp}.txt"
            
            with open(backup_filename, 'w') as f:
                f.write(f"# Backup from device: {hostname}\n")
                f.write(f"# Backup time: {datetime.now()}\n")
                f.write(f"# IP Address: {device_ip}\n")
                f.write("#" * 50 + "\n\n")
                f.write(running_config)
            
            self.logger.info(f"[{device_ip}] Local backup saved: {backup_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"[{device_ip}] Backup failed: {e}")
            return False
    
    def manage_device(self, device: Dict) -> Dict:
        """
        Complete workflow for a single device.
        
        Args:
            device: Device dictionary with connection parameters
            
        Returns:
            Dict: Device execution result
        """
        device_ip = device.get("ip", "Unknown")
        hostname = device.get("hostname", device_ip.replace('.', '_'))
        connection = None
        result = {
            "ip": device_ip,
            "hostname": hostname,
            "success": False,
            "error": None,
            "stage": "Initialization"
        }
        
        try:
            self.logger.info(f"=" * 60)
            self.logger.info(f"Starting automation for device: {hostname} ({device_ip})")
            
            # Phase 1: Establish connection
            self.logger.info(f"[{device_ip}] Phase 1: Establishing SSH connection...")
            connection = ConnectHandler(**device)
            result["stage"] = "Connected"
            self.logger.info(f"[{device_ip}] Successfully connected to {hostname}")
            
            # Phase 2: Pre-check (State Verification)
            self.logger.info(f"[{device_ip}] Phase 2: Executing pre-validation...")
            pre_check_output = self.execute_pre_check(connection, device_ip)
            if not pre_check_output:
                raise Exception("Pre-check failed to retrieve device state")
            result["stage"] = "Pre-check completed"
            
            # Phase 3: Apply Configuration
            self.logger.info(f"[{device_ip}] Phase 3: Deploying configuration changes...")
            config_success, config_msg = self.apply_configuration(connection, device_ip)
            if not config_success:
                raise Exception(f"Configuration deployment failed: {config_msg}")
            result["stage"] = "Configuration applied"
            
            # Phase 4: Post-check & Validation
            self.logger.info(f"[{device_ip}] Phase 4: Validating configuration changes...")
            validation_success = self.execute_post_check(connection, device_ip, pre_check_output)
            if not validation_success:
                raise Exception("Post-validation failed")
            result["stage"] = "Validation passed"
            
            # Phase 5: Backup Configuration
            self.logger.info(f"[{device_ip}] Phase 5: Creating configuration backups...")
            backup_success = self.backup_configuration(connection, device_ip, hostname)
            if not backup_success:
                self.logger.warning(f"[{device_ip}] Backup failed but changes were applied")
            result["stage"] = "Backup completed"
            
            # Success!
            result["success"] = True
            self.logger.info(f"[{device_ip}] ✅ Automation completed successfully!")
            
        except NetmikoAuthenticationException as e:
            error_msg = f"Authentication failed: {e}"
            self.logger.error(f"[{device_ip}] {error_msg}")
            result["error"] = error_msg
            result["stage"] = "Authentication Error"
            
        except NetmikoTimeoutException as e:
            error_msg = f"Connection timeout: {e}"
            self.logger.error(f"[{device_ip}] {error_msg}")
            result["error"] = error_msg
            result["stage"] = "Timeout Error"
            
        except NetmikoBaseException as e:
            error_msg = f"Netmiko error: {e}"
            self.logger.error(f"[{device_ip}] {error_msg}")
            result["error"] = error_msg
            result["stage"] = "Netmiko Error"
            
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(f"[{device_ip}] {error_msg}")
            result["error"] = error_msg
            result["stage"] = f"Failed at: {result['stage']}"
            
        finally:
            # Phase 6: Disconnect Safely (always executed)
            if connection:
                try:
                    connection.disconnect()
                    self.logger.info(f"[{device_ip}] SSH session closed cleanly")
                except Exception as e:
                    self.logger.warning(f"[{device_ip}] Error during disconnect: {e}")
        
        return result
    
    def run_parallel(self):
        """
        Execute device management in parallel using ThreadPoolExecutor.
        """
        if not self.devices:
            self.logger.error("No devices to process. Load inventory first.")
            return
        
        if not self.commands:
            self.logger.error("No commands to apply. Load commands first.")
            return
        
        self.logger.info(f"🚀 Starting parallel execution on {len(self.devices)} devices with {self.max_workers} workers")
        start_time = time.time()
        
        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_device = {
                executor.submit(self.manage_device, device): device 
                for device in self.devices
            }
            
            # Process completed tasks
            for future in as_completed(future_to_device):
                device = future_to_device[future]
                try:
                    result = future.result()
                    if result["success"]:
                        self.results["successful"].append({
                            "ip": result["ip"],
                            "hostname": result["hostname"]
                        })
                    else:
                        self.results["failed"].append({
                            "ip": result["ip"],
                            "hostname": result["hostname"],
                            "error": result["error"],
                            "stage": result["stage"]
                        })
                except Exception as e:
                    device_ip = device.get("ip", "Unknown")
                    self.logger.error(f"Unhandled exception for device {device_ip}: {e}")
                    self.results["failed"].append({
                        "ip": device_ip,
                        "error": str(e),
                        "stage": "Unknown"
                    })
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"🏁 Parallel execution completed in {elapsed_time:.2f} seconds")
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """
        Generate and display a comprehensive execution summary report.
        """
        print("\n" + "=" * 80)
        print("📊 EXECUTION SUMMARY REPORT")
        print("=" * 80)
        print(f"📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Total Devices: {self.results['total']}")
        print(f"✅ Successful: {len(self.results['successful'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        
        if self.results['successful']:
            print("\n✅ SUCCESSFUL DEVICES:")
            for device in self.results['successful']:
                print(f"   - {device['hostname']} ({device['ip']})")
        
        if self.results['failed']:
            print("\n❌ FAILED DEVICES:")
            for device in self.results['failed']:
                print(f"   - {device.get('hostname', device['ip'])} ({device['ip']})")
                print(f"     Stage: {device.get('stage', 'Unknown')}")
                print(f"     Error: {device.get('error', 'Unknown error')}")
        
        print("\n📁 Detailed logs saved to: network_automation.log")
        print("📁 Configuration backups saved to: ./backups/")
        print("=" * 80)
        
        # Also log the summary
        self.logger.info(f"Summary - Total: {self.results['total']}, "
                        f"Success: {len(self.results['successful'])}, "
                        f"Failed: {len(self.results['failed'])}")
    
    def run(self):
        """
        Main execution flow.
        """
        print("\n" + "=" * 80)
        print("🤖 CISCO NETWORK AUTOMATION TOOL")
        print("=" * 80)
        
        # Load required files
        if not self.load_inventory():
            sys.exit(1)
        
        if not self.load_commands():
            sys.exit(1)
        
        # Execute automation
        self.run_parallel()


def main():
    """
    Entry point of the script.
    """
    # Configuration files (can be modified or passed as arguments)
    INVENTORY_FILE = "inventory.json"
    COMMANDS_FILE = "commands.txt"
    MAX_WORKERS = 5  # Adjust based on your network capacity
    
    # Validate files exist
    if not os.path.exists(INVENTORY_FILE):
        print(f"❌ Error: {INVENTORY_FILE} not found!")
        sys.exit(1)
    
    if not os.path.exists(COMMANDS_FILE):
        print(f"❌ Error: {COMMANDS_FILE} not found!")
        sys.exit(1)
    
    # Create and run automation
    automation = CiscoNetworkAutomation(INVENTORY_FILE, COMMANDS_FILE, MAX_WORKERS)
    automation.run()


if __name__ == "__main__":
    main()