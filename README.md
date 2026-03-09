# Peters-Disk-Utils (v1.0.0-alpha)

A lightweight, cross-platform CLI suite for indexing, visualizing, and navigating disk storage. Built for developers and power users who need to analyze large directory structures and explore them offline.

## 🛠 Features

- **Single-Pass Indexing**: High-performance recursive scanning using `os.scandir`.
- **Interactive Navigator**: A REPL-style terminal interface to explore your disk index without touching the actual filesystem.
- **Visual Analytics**: Automatically generates a Ring (Donut) Chart of storage distribution.
- **OS-Aware Exclusions**: Pre-configured to skip virtual filesystems (Linux) and protected system folders (Windows).
- **Centralized Config**: Control targets, output names, and verbosity via _config.ini_.
- **Silent Logging**: Comprehensive error tracking using the `logging` module to keep your terminal clean.

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have Python 3.10 or higher installed. Install the required dependencies:

```bash
pip install matplotlib colorama
```

### 2. Configuration

The suite requires a _config.ini_ file in the root directory.

Use this template and rename it to _config.ini_ in order to configure the program with the best settings.

```ini
; -- Default configuration template --
; Rename to 'config.ini' to start using this configuration

[GENERAL]
; Set to True for full logs, False for single-line status
Verbose = False
; How many errors to show in the terminal summary
ErrorLimit = 20
; Whether to print the error summary at the end of the scan
ShowSummary = True

[PATHS]
; Default names for your outputs
JsonOutput = disk-index.json
ChartOutput = analysis.pdf
; Log file for permission errors
LogFile = nls-errors.log

; Default directories to scan if no --target param is provided
[DEFAULT_TARGETS]
Windows = C:/Users
Linux = /home

[EXCLUDE]
; Linux-specific virtual/system files
LinuxDirs = /proc, /sys, /dev, /run, /snap, /var/lib/lxd
; Windows-specific system files that often cause permission errors
WindowsDirs = C:/System Volume Information, C:/$Recycle.Bin, C:/Windows/CSC
```

## 📖 Usage Guide

### Step 1: Indexing _disk-nls.py_

Run the analyzer to create a JSON snapshot of your drive and a visual PDF chart.

```Bash
# Uses the default target from config.ini
python disk-nls.py

# Manually specify a target and enable verbose logging
python disk-nls.py --target /var/www --verbose

```

### Step 2: Navigating _disk-nav.py_

Explore the generated index interactively using our built-in CLI tool:

```Bash
# Loads the default JsonOutput from config.ini
python disk-nav.py
```

#### Navigator Commands

- ls: List current directory contents (sorted by size).
- cd {dir}: Enter a directory.
- cd ..: Move to the parent directory.
- clear: Clear the terminal screen.
- help: Show available commands.
- exit: Close the navigator.

## ⚠️ Known Issues (Alpha)

1. Some system-level folders remain inaccessible without Admin/Sudo privileges. Check _nls-errors.log_ for details when indexing system directories.
2. Very large disk indexes (multi-terabyte) may consume significant RAM during JSON generation. While we work on a solution for this, you might want to avoid indexing non-user directories.
