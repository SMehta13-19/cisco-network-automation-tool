# Cisco Network Automation Tool

## Overview

A production-ready Network Automation Tool built using Python and Netmiko for Cisco IOS devices.

### Features

* Multi-device automation
* SSH-based Cisco IOS management
* Configuration deployment
* Pre/Post validation
* Automated configuration backups
* Logging and error handling
* Concurrent execution using multithreading

---

## Architecture

```text
Inventory.json
      │
      ▼
Load Device Inventory
      │
      ▼
SSH Connection (Netmiko)
      │
      ▼
Pre-Validation
      │
      ▼
Deploy Configuration
      │
      ▼
Post-Validation
      │
      ▼
Backup Configuration
      │
      ▼
Logging & Reporting
```

---

## Key Outcomes

* Automated Cisco IOS device management using Python.
* Reduced manual configuration effort.
* Implemented multi-device concurrent execution.
* Added automated backup and validation workflows.
* Centralized logging and exception handling.

---

## Technologies Used

* Python
* Netmiko
* Cisco IOS
* Paramiko
* ThreadPoolExecutor
* JSON
* Logging

---

## Project Structure

```text
cisco-network-automation-tool/
│
├── screenshots/
│   ├── execution1.png
│   ├── execution2.png
│   ├── execution3.png
│   ├── logs1.png
│   ├── logs2.png
│   ├── logs3.png
│   └── structure.png
│
├── backups/
├── network_automation.py
├── inventory.json
├── commands.txt
├── requirements.txt
├── test_without_devices.py
├── README.md
└── .gitignore
```

---

## Demo

### Validation & Initialization

![Execution 1](screenshots/execution1.png)

### Validation Summary & Simulation

![Execution 2](screenshots/execution2.png)

### Expected Production Workflow

![Execution 3](screenshots/execution3.png)

### Device Processing Logs

![Logs 1](screenshots/logs1.png)

### Connection & Timeout Handling

![Logs 2](screenshots/logs2.png)

### Error Reporting & Summary

![Logs 3](screenshots/logs3.png)

### Project Structure

![Project Structure](screenshots/structure.png)

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python network_automation.py
```

Test mode:

```bash
python test_without_devices.py
```

---

## Skills Demonstrated

* Network Automation
* Cisco IOS Management
* Python Development
* Multithreading
* SSH Automation
* Logging & Monitoring
* Exception Handling
* Configuration Management

---

## Author

Soumya Mehta

CCNA Certified | Network Automation Enthusiast

GitHub: https://github.com/SMehta13-19
