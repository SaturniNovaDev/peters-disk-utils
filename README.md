# Peters-Disk-Utils (v1.0.0-stable)

A lightweight, cross-platform CLI suite for indexing, visualizing, and navigating disk storage. Built for developers and power users who need to analyze large directory structures and explore them offline.

## 🛠 Features

- **Single-Pass Indexing**: High-performance recursive scanning using `os.scandir`.
- **Interactive Navigator**: A REPL-style terminal interface to explore your disk index without touching the actual filesystem.
- **Visual Analytics**: Automatically generates a Ring (Donut) Chart of storage distribution.
- **OS-Aware Exclusions**: Pre-configured to skip virtual filesystems (Linux) and protected system folders (Windows).
- **Centralized Config**: Control targets, output names, and verbosity via _config.ini_.
- **Silent Logging**: Comprehensive error tracking using the `logging` module to keep your terminal clean.
- **Cross-Platform**: Works seamlessly on Windows and Linux with the same codebase.
- **Global Usage**: Run the analyzer and navigator from any directory, with outputs saved to the current working directory.

## 🚀 Quick Start

### 1. **Clone the Repository**

```Bash
git clone https://github.com/SaturniNovaDev/peters-disk-utils
```

### 2. **Run the Installer**

On Linux:

```Bash
cd peters-disk-utils
chmod +x setup.sh
./setup.sh
# Follow the instructions in the wizard
```

On Windows:

```PowerShell
cd peters-disk-utils
.\setup.bat
# Follow the instructions in the wizard
```

The installer will guide you through setting up the necessary Python environment, installing dependencies, and configuring your default targets, as well as optionally adding the tools to your system for global access.
This works by creating scripts in your system PATH that point to the main Python files, allowing you to run `disk-nls` and `disk-nav` from any terminal.

Keep in mind that **erasing the files in the repository will break this functionality.** I'm working on a future update which will include an uninstaller script to clean up these PATH entries if needed.

If you do, however, want to remove the tools manually, simply delete the `disk-nls` and `disk-nav` scripts from your system PATH (e.g., `/usr/local/bin/` on Linux or the PATH environment variable on Windows).

## 📖 Usage Guide

### Step 1: Indexing _disk-nls.py_

Run the analyzer to create a JSON snapshot of your drive and a visual PDF chart.

```Bash
# Uses the default target from config.ini
python3 disk-nls.py

# Manually specify a target and enable verbose logging
python3 disk-nls.py --target /var/www --verbose

```

Or, if you have set up the global command:

```Bash
disk-nls # Optionally specify a target with --target and enable verbose logging with --verbose
```

### Step 2: Navigating _disk-nav.py_

Explore the generated index interactively using our built-in CLI tool:

```Bash
# Loads the default JsonOutput from config.ini
python3 ./disk-nav.py
```

Or, if you have set up the global command:

```Bash
disk-nav # Optionally specify a source JSON snapshot with --source
```

#### Navigator Commands

- ls: List current directory contents (sorted by size).
- cd {dir}: Enter a directory.
- cd ..: Move to the parent directory.
- clear: Clear the terminal screen.
- help: Show available commands.
- exit: Close the navigator.

## Notes

1. System directories and virtual filesystems are automatically excluded based on the OS, but you can customize this in the _config.ini_ file under the `[EXCLUSIONS]` section. If you get permission errors during indexing, run the program as administrator/root or adjust the exclusions to skip problematic directories. **NOTE THAT THIS IS VERY INCONVENIENT**, as the next time you want to analyze the disk, or even access the log, chart or index files, you will have to run the program with elevated permissions again. Run as an administrator/root only if you _NEED_ to analyze protected system folders or virtual filesystems, and be cautious when doing so, as it can lead to unintended consequences if you modify or delete important files.

```Bash
sudo disk-nls # Reads config.ini and runs with elevated permissions on Linux
# Or:
sudo python3 disk-nls.py --target / # Run with elevated permissions on Linux
# Or:
python3 disk-nls.py --target /home # Skip non-user directories on Linux
```

## ⚠️ Known Issues (Stable)

1. The Ring Chart may not display correctly if there are too many small files or directories, as they can clutter the visualization.
2. The navigator does not currently support searching or filtering within the index, which can make it difficult to find specific items in large datasets. Future updates will include search functionality.
3. The tool does not currently handle symbolic links or shortcuts, which may lead to inaccurate size calculations or navigation issues.
4. The installer does not currently check for existing PATH entries before adding new ones, which could lead to conflicts if the tools are already installed or if there are naming collisions. I recommend reviewing your PATH after installation and removing any duplicates if necessary.
5. The tool does not currently support incremental updates to the index, meaning that you will need to re-run the analyzer to reflect any changes in the filesystem.
6. The navigation REPL is still very raw and prone to styling errors.
7. The tool is known to log some directories with incorrect sizes due to permission issues or special filesystem features. In some occasions, these might be reflected in the index with a size larger than the disk's own capacity. This is a known issue that I am working on fixing in a future update.
