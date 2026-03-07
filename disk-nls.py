import os
import json
import argparse
from datetime import datetime
import matplotlib.pyplot as plt
from tqdm import tqdm


def build_index(path, progress_bar=None):
    """
    Recursively builds a nested dictionary of the file system.
    """
    name = os.path.basename(path) or path
    node = {"name": name, "size": 0, "type": "directory", "children": []}

    try:
        with os.scandir(path) as it:
            for entry in it:
                if progress_bar is not None:
                    progress_bar.update(1)

                try:
                    if entry.is_file(follow_symlinks=False):
                        f_size = entry.stat().st_size
                        node["children"].append(
                            {"name": entry.name, "size": f_size, "type": "file"}
                        )
                        node["size"] += f_size
                    elif entry.is_dir(follow_symlinks=False):
                        subdir = build_index(entry.path, progress_bar=progress_bar)
                        node["children"].append(subdir)
                        node["size"] += subdir["size"]
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        pass

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
    parser.add_argument(
        "--target", type=str, required=True, help="Disk unit (C: or D:)"
    )
    parser.add_argument(
        "--output", type=str, default="analysis.pdf", help="Output PDF/Image"
    )
    args = parser.parse_args()

    # Normalize path for Windows
    target = os.path.abspath(args.target)

    print(f"Indexing {target}... This may take a while for large drives.")

    # Using a simple spinner/total-less bar because total files is unknown initially
    with tqdm(
        unit="files", bar_format="{l_bar}{bar:20}{r_bar}", colour="green"
    ) as pbar:
        full_structure = build_index(target, progress_bar=pbar)

    # Add metadata
    final_output = {
        "index_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root": target,
        "total_size_bytes": full_structure["size"],
        "structure": full_structure,
    }

    # Save JSON
    json_filename = "disk_index.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    print(f"Index metadata saved to {json_filename}")

    # Save Visual
    generate_visuals(full_structure, args.output)
