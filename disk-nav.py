import os
import json
import argparse
import configparser
from colorama import Fore, init

init(autoreset=True)

# Load shared configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Get default source from config, fallback to disk-index.json if not found
DEFAULT_SOURCE = config.get("PATHS", "JsonOutput", fallback="disk-index.json")


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
        # Reconstruct path from the stack to ensure clean slashes
        names = [node["name"] for node in self.path_stack[1:]]  # Skip root placeholder
        names.append(self.current_node["name"])
        return "/" + "/".join(names).replace("//", "/")

    def format_size(self, bytes_size):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024

    def list_contents(self):
        # Clear screen for a cleaner 'explorer' feel
        os.system("cls" if os.name == "nt" else "clear")

        print(f"{Fore.MAGENTA}PATH: {Fore.GREEN}{self.get_current_path_str()}")
        print(f"{Fore.MAGENTA}INDEX DATE: {Fore.WHITE}{self.index_date}\n")

        children = sorted(
            self.current_node.get("children", []),
            key=lambda x: (x["type"] != "directory", -x["size"]),
        )
        parent_size = self.current_node["size"]

        header = f"{'TYPE':<10} {'NAME':<35} {'SIZE':<15} {'%'}"
        print(f"{Fore.BLUE}{header}")
        print(f"{Fore.BLUE}{'-' * len(header)}")

        for item in children:
            pct = (item["size"] / parent_size * 100) if parent_size > 0 else 0
            color = Fore.YELLOW if item["type"] == "directory" else Fore.WHITE
            type_label = f"[{item['type'].upper()}]"

            print(
                f"{Fore.CYAN}{type_label:<10} {color}{item['name']:<35} "
                f"{Fore.GREEN}{self.format_size(item['size']):<15} {Fore.RED}{pct:>5.1f}%"
            )

    def navigate(self):
        while True:
            self.list_contents()
            prompt = f"\n{Fore.YELLOW}({self.get_current_path_str()}){Fore.WHITE} >>> "
            try:
                cmd_input = input(prompt).strip().split(maxsplit=1)
            except (EOFError, KeyboardInterrupt):
                break

            if not cmd_input:
                continue
            cmd = cmd_input[0].lower()
            arg = cmd_input[1] if len(cmd_input) > 1 else None

            if cmd in ["exit", "quit"]:
                break
            elif cmd == "help":
                print(f"\n{Fore.GREEN}Available Commands:")
                print(
                    f"{Fore.WHITE}ls          - Refresh and list current directory contents"
                )
                print(f"{Fore.WHITE}cd <dir>    - Enter a directory")
                print(f"{Fore.WHITE}cd ..       - Go back to parent directory")
                print(f"{Fore.WHITE}clear       - Clear the terminal screen")
                print(f"{Fore.WHITE}exit        - Close the navigator")
                input("\nPress Enter to continue...")
            elif cmd == "clear":
                os.system("cls" if os.name == "nt" else "clear")
            elif cmd == "ls":
                continue
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
    parser = argparse.ArgumentParser(description="Interactive Disk Index Navigator")
    # Source is now optional because we have a default from config.ini
    parser.add_argument(
        "--source",
        type=str,
        default=DEFAULT_SOURCE,
        help=f"Path to JSON index (Default: {DEFAULT_SOURCE})",
    )
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"{Fore.RED}Error: Source file '{args.source}' not found.")
        print(
            f"{Fore.YELLOW}Tip: Run disk-nls.py first or check your config.ini [PATHS] settings."
        )
        exit(1)

    try:
        with open(args.source, "r", encoding="utf-8") as f:
            data = json.load(f)

        nav = DiskNavigator(data)
        nav.navigate()
    except json.JSONDecodeError:
        print(
            f"{Fore.RED}Error: Failed to parse '{args.source}'. File may be corrupted."
        )
