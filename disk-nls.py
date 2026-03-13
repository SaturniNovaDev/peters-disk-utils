#!/usr/bin/env python3
import os
import json
import argparse
import logging
import configparser
import platform
import time
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from colorama import Fore, init

# Load Config
config = configparser.ConfigParser()
config.read("config.ini")

matplotlib.use("Agg")
init(autoreset=True)

# OS-Aware Exclusions
current_os = platform.system()
exclude_key = "WindowsDirs" if current_os == "Windows" else "LinuxDirs"
exclude_input = config.get("EXCLUDE", exclude_key, fallback="")
IGNORE_DIRS = (
    {os.path.abspath(d.strip()) for d in exclude_input.split(",")}
    if exclude_input
    else set()
)

# Setup Logging
logging.basicConfig(
    filename=config.get("PATHS", "LogFile", fallback="nls-errors.log"),
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def build_index(path, verbose=False):
    abs_path = os.path.abspath(path)

    if abs_path in IGNORE_DIRS:
        if verbose:
            print(f"{Fore.YELLOW}Skipping excluded dir: {abs_path}")
        return {
            "name": os.path.basename(path) or path,
            "size": 0,
            "type": "directory",
            "children": [],
        }

    name = os.path.basename(path.rstrip(os.sep)) or path
    node = {"name": name, "size": 0, "type": "directory", "children": []}

    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if not verbose:
                        display_path = (
                            entry.path
                            if len(entry.path) < 60
                            else f"...{entry.path[-57:]}"
                        )
                        print(
                            f"\r{Fore.CYAN}Indexing: {Fore.WHITE}{display_path:<60}",
                            end="",
                            flush=True,
                        )
                    else:
                        print(
                            f"{Fore.CYAN}Indexing {Fore.WHITE}{entry.path}...",
                            end="",
                            flush=True,
                        )

                    if entry.is_file(follow_symlinks=False):
                        f_size = entry.stat().st_size
                        node["children"].append(
                            {"name": entry.name, "size": f_size, "type": "file"}
                        )
                        node["size"] += f_size
                    elif entry.is_dir(follow_symlinks=False):
                        subdir = build_index(entry.path, verbose=verbose)
                        node["children"].append(subdir)
                        node["size"] += subdir["size"]
                except Exception as e:
                    logging.error(f"Failed to index {entry.path}: {e}")
    except Exception as e:
        logging.error(f"Access Denied: {path} ({e})")

    return node


def generate_visuals(index_data, output_file):
    labels, sizes = [], []
    children = sorted(index_data["children"], key=lambda x: x["size"], reverse=True)
    total_size = index_data["size"]

    if total_size == 0:
        return

    for child in children:
        if (child["size"] / total_size) > 0.01:
            labels.append(child["name"])
            sizes.append(child["size"])

    others_size = total_size - sum(sizes)
    if others_size > 0:
        labels.append("Others")
        sizes.append(others_size)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, pctdistance=0.85)

    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig.gca().add_artist(centre_circle)

    plt.title(f"Storage Distribution: {index_data['name']}")
    plt.savefig(output_file)
    plt.close(fig)  # Clean up memory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Disk-NLS Analyzer")

    os_name = platform.system()
    default_target = config.get("DEFAULT_TARGETS", os_name, fallback=".")

    parser.add_argument("--target", type=str, default=default_target)
    parser.add_argument(
        "--output", type=str, default=config.get("PATHS", "ChartOutput")
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=config.getboolean("GENERAL", "Verbose"),
    )
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    if not os.path.exists(target):
        print(f"{Fore.RED}Error: Target path '{target}' does not exist.")
        print(
            f"{Fore.YELLOW}Please check your --target argument or the [DEFAULT_TARGETS] in config.ini."
        )
        exit(1)

    print(f"{Fore.YELLOW}Target identified: {Fore.WHITE}{target}")

    start_time = time.time()
    full_structure = build_index(target, verbose=args.verbose)
    end_time = time.time()

    if not args.verbose:
        print(f"\r{' ' * 100}\r", end="", flush=True)

    final_output = {
        "index_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root": target,
        "scan_duration_seconds": round(end_time - start_time, 2),
        "total_size_bytes": full_structure["size"],
        "structure": full_structure,
    }

    json_name = config.get("PATHS", "JsonOutput")
    with open(json_name, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    if config.getboolean("GENERAL", "ShowSummary"):
        print(f"{Fore.YELLOW}{'='*20} SCAN COMPLETE {'='*20}")
        print(
            f"{Fore.WHITE}Total Size: {Fore.GREEN}{full_structure['size'] / (1024**3):.2f} GB"
        )
        print(
            f"{Fore.WHITE}Duration:   {Fore.CYAN}{final_output['scan_duration_seconds']}s"
        )
        print(f"{Fore.WHITE}Log File:   {Fore.CYAN}{config.get('PATHS', 'LogFile')}")
        if final_output["scan_duration_seconds"] > 60:
            print(
                f"{Fore.YELLOW}Note: Long scan times may indicate a very large target or performance issues. Consider excluding more directories or running with verbose mode for detailed logging."
            )
        print(
            f"{Fore.BLUE}Tip: If you get permission errors during scans, consider skipping system directories or running the tool with elevated permissions (e.g., as administrator or with sudo)."
        )

    generate_visuals(full_structure, args.output)
    print(f"{Fore.GREEN}Index and chart saved successfully.")
