# CoreCheck - IT Support Application

**Version:** 1.0.0  
**Date:** April 2026

---

## Description

CoreCheck is a Windows IT support application that allows you to quickly diagnose a PC and perform certain automatic actions.

## Features

- **System Information**: CPU, RAM, disk space, PC name, OS
- **Network Test**: Internet connection check, response time
- **Quick Analysis**: Problem detection (low disk, saturated RAM, high CPU)
- **Quick Actions**: Clean temporary files, task manager, network settings, Flush DNS
- **Process Scan**: List of active processes, sort by CPU, terminate a process
- **Logs**: History of actions performed

## Installation

1. Make sure you have Python 3.7+ installed
2. Install dependencies:
   ```
   pip install psutil
   ```
3. Launch the application:
   - Double-click `launcher.bat`
   - Or via Python: `python main.py`

## Building the Executable (Optional)

To create a .exe file:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name CoreCheck main.py
```

The executable will be in the `dist/` folder.

## Interface

The application features a modern GUI with:

- System Information section
- Network section
- Quick Actions section
- Processes section
- Logs section
- Dark mode
- Auto-updating stats (every 2 seconds)

## Author

- Senior Python Developer

## License

MIT
