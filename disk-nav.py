import json
import argparse
import sys


class DiskNavigator:
    def __init__(self, data):
        self.metadata = data
        self.root = data["structure"]
        self.index_date = data.get("index_date", "Unknown")
        self.current_node = self.root
        self.path_stack = []

    def get_current_path_str(self):
        if not self.path_stack:
            return "/"
        return "/" + "/".join([node["name"] for node in self.path_stack])

    def format_size(self, bytes_size):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024

    def list_contents(self):
        print(f"\nLocation: {self.get_current_path_str()} (Indexed: {self.index_date})")

        # Sort children: Directories first, then by size
        children = sorted(
            self.current_node.get("children", []),
            key=lambda x: (x["type"] != "directory", -x["size"]),
        )

        parent_size = self.current_node["size"]

        print(f"{'TYPE':<10} {'NAME':<30} {'SIZE':<15} {'%'}")
        print("-" * 65)

        for item in children:
            percentage = (item["size"] / parent_size * 100) if parent_size > 0 else 0
            type_str = f"[{item['type'].upper()}]"
            size_str = self.format_size(item["size"])

            print(
                f"{type_str:<10} {item['name']:<30} {size_str:<15} {percentage:>5.1f}%"
            )

    def navigate(self):
        while True:
            self.list_contents()
            try:
                cmd_input = (
                    input(f"\n({self.get_current_path_str()}) >>> ")
                    .strip()
                    .split(maxsplit=1)
                )
            except EOFError:
                break

            if not cmd_input:
                continue

            cmd = cmd_input[0].lower()
            arg = cmd_input[1] if len(cmd_input) > 1 else None

            if cmd == "exit" or cmd == "quit":
                break

            elif cmd == "cd":
                if not arg or arg == ".":
                    continue
                elif arg == "..":
                    if self.path_stack:
                        self.current_node = (
                            self.path_stack.pop()
                            if len(self.path_stack) > 1
                            else self.root
                        )
                        if not self.path_stack and self.current_node == self.root:
                            # We've reached root, stack is empty
                            pass
                    else:
                        self.current_node = self.root
                else:
                    # Find directory in children
                    target = next(
                        (
                            c
                            for c in self.current_node.get("children", [])
                            if c["name"].lower() == arg.lower()
                            and c["type"] == "directory"
                        ),
                        None,
                    )
                    if target:
                        self.path_stack.append(self.current_node)
                        self.current_node = target
                    else:
                        print(f"Directory '{arg}' not found.")

            elif cmd == "ls":
                continue  # loop will re-list

            else:
                print(f"Unknown command: {cmd}. Use 'cd', 'ls', or 'exit'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=str, required=True, help="Path to the disk_index.json file"
    )
    args = parser.parse_args()

    try:
        with open(args.source, "r", encoding="utf-8") as f:
            data = json.load(f)

        nav = DiskNavigator(data)
        nav.navigate()
    except FileNotFoundError:
        print(f"Error: Could not find file {args.source}")
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON. File might be corrupted.")
