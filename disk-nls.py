import os
import json
import argparse
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from colorama import Fore, Style, init

matplotlib.use("Agg")

init(autoreset=True)

# Store errors globally to report at the end
encountered_errors = []

# Filter to ignore system directories on Linux
IGNORE_DIRS = {'/proc', '/sys', '/dev', '/run', '/snap', '/var/lib/lxd'}

def build_index(path, verbose=False):
    # Check if the current path is in the ignore list
    if path.rstrip(os.sep) in IGNORE_DIRS:
        if verbose: print(f"{Fore.YELLOW}Skipping virtual/system dir: {path}")
        return {"name": os.path.basename(path), "size": 0, "type": "directory", "children": []}

    name = os.path.basename(path.rstrip(os.sep)) or path
    node = {"name": name, "size": 0, "type": "directory", "children": []}
    
    try:
        # Use a context manager to ensure the iterator is closed immediately
        with os.scandir(path) as it:
            for entry in it:
                try:
                    # MODE: One-line Status
                    if not verbose:
                        status = f"{Fore.CYAN}Indexing: {Fore.WHITE}{entry.path[:60]}"
                        print(f"\r{status:<80}", end="", flush=True)
                    else:
                        print(f"{Fore.CYAN}Indexing {Fore.WHITE}{entry.path} ... ", end="", flush=True)

                    if entry.is_file(follow_symlinks=False):
                        f_size = entry.stat().st_size
                        node["children"].append({"name": entry.name, "size": f_size, "type": "file"})
                        node["size"] += f_size
                        if verbose: print(f"{Fore.GREEN}Done")
                        
                    elif entry.is_dir(follow_symlinks=False):
                        # RECURSION POINT: We only call this ONCE per directory
                        if verbose: print(f"{Fore.YELLOW}Descending")
                        subdir = build_index(entry.path, verbose=verbose)
                        node["children"].append(subdir)
                        node["size"] += subdir["size"]
                        
                except Exception as e:
                    encountered_errors.append(f"Error in {entry.path}: {e}")
                    if verbose: print(f"{Fore.RED}Failed")
                    continue
    except Exception as e:
        encountered_errors.append(f"Access Denied: {path} ({e})")
        
    return node


def generate_visuals(index_data, output_file):
    # Prepare data for the top-level ring chart
    labels = []
    sizes = []

    # Sort children by size to show largest first
    children = sorted(index_data["children"], key=lambda x: x["size"], reverse=True)
    total_size = index_data["size"]

    if total_size == 0:
        print("Disk appears empty or inaccessible.")
        return

    for child in children:
        # Only show items > 1% of total to keep chart clean
        if (child["size"] / total_size) > 0.01:
            labels.append(child["name"])
            sizes.append(child["size"])

    # "Others" category
    others_size = total_size - sum(sizes)
    if others_size > 0:
        labels.append("Others")
        sizes.append(others_size)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140, pctdistance=0.85)

    # Ring/Donut effect
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig.gca().add_artist(centre_circle)

    plt.title(f"Storage Distribution: {index_data['name']}")
    plt.savefig(output_file)
    print(f"Chart saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=str, required=True)
    parser.add_argument("--output", type=str, default="analysis.pdf")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full log instead of one-line status",
    )
    args = parser.parse_args()

    target = os.path.abspath(args.target)

    # Start storing index in full_structure
    print(f"{Fore.YELLOW}Starting scan of {target}...")
    full_structure = build_index(target, verbose=args.verbose)

    # Clean up the status line if not in verbose mode
    if not args.verbose:
        print(f"\r{' ' * 100}\r", end="", flush=True)

    # Final Summary Reporting
    print(f"\n\n{Fore.YELLOW}{'='*20} SCAN SUMMARY {'='*20}")
    if encountered_errors:
        print(f"{Fore.RED}Encountered {len(encountered_errors)} errors during scan:")
        for err in encountered_errors[:20]:  # Show first 20 to avoid flooding
            print(f"{Fore.RED} - {err}")
        if len(encountered_errors) > 20:
            print(f"{Fore.RED} ... and {len(encountered_errors)-20} more.")
    else:
        print(f"{Fore.GREEN}Scan completed with 0 errors.")

    # Metadata and JSON Export
    final_output = {
        "index_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root": target,
        "total_size_bytes": full_structure["size"],
        "structure": full_structure,
    }

    json_filename = "disk-index.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    print(f"\n{Fore.GREEN}Index metadata saved to {json_filename}")

    # Save Visual
    generate_visuals(full_structure, args.output)
