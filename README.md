# Cisco Network Automation Tool

## Overview

A production-ready Network Automation Tool built using Python and Netmiko for Cisco IOS devices.

The tool automates:

- Configuration deployment
- Device validation
- Configuration backups
- Error handling
- Logging
- Multi-device concurrent execution

## Features

### Device Inventory Management

- JSON-based inventory
- Multi-device support
- SSH-based access

### Configuration Automation

- Automated deployment of Cisco IOS commands
- Batch configuration execution
- Validation before and after deployment

### Backup Management

- Automatic running-config backup
- Timestamped backup files
- Local backup storage

### Logging

- Detailed execution logs
- Error reporting
- Device-level status tracking

### Parallel Execution

- ThreadPoolExecutor
- Simultaneous execution on multiple devices
- Improved deployment speed

## Technologies

- Python
- Netmiko
- Paramiko
- ThreadPoolExecutor
- JSON
- Cisco IOS

## Project Structure

```text
cisco-network-automation-tool
│
├── network_automation.py
├── inventory.json
├── commands.txt
├── requirements.txt
├── test_without_devices.py
├── README.md
└── backups/
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python network_automation.py
```

## Author

Soumya Mehta