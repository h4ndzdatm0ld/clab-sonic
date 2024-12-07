import os
import json
import argparse
from typing import Dict


def load_json(file_path: str) -> Dict:
    """Load JSON data from a file."""
    print(f"Loading JSON data from {file_path}...")
    with open(file_path, "r") as file:
        data = json.load(file)
    print(f"Successfully loaded JSON data from {file_path}.")
    return data


def update_config(default_attrs: Dict, config_path: str) -> None:
    """
    Update a config file with default attributes if keys are missing.

    Args:
        default_attrs (Dict): Default attributes to add if missing.
        config_path (str): Path to the configuration file to update.
    """
    print(f"Reading configuration file: {config_path}")
    with open(config_path, "r") as file:
        config_data = json.load(file)

    updated = False
    for key, value in default_attrs.items():
        if key not in config_data:
            print(f"Key '{key}' missing in {config_path}. Adding it.")
            config_data[key] = value
            updated = True

    if updated:
        with open(config_path, "w") as file:
            json.dump(config_data, file, indent=4)
        print(f"Updated {config_path} with missing keys.")
    else:
        print(f"No updates needed for {config_path}.")


def find_and_update_configs(base_dir: str, default_attrs_path: str) -> None:
    """
    Find and update all node config files with default attributes.

    Args:
        base_dir (str): Base directory to search for node configuration files.
        default_attrs_path (str): Path to the JSON file with default attributes.
    """
    print(f"Loading default attributes from {default_attrs_path}...")
    default_attrs = load_json(default_attrs_path)

    print(f"Starting search for configuration files in {base_dir}...")
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                config_path = os.path.join(root, file)
                print(f"Found configuration file: {config_path}")
                update_config(default_attrs, config_path)

    print("Finished processing all configuration files.")


def main() -> None:
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Update node configuration files with default attributes."
    )
    parser.add_argument(
        "--base-dir",
        required=True,
        help="Base directory to search for node config files (e.g., clab-sonic).",
    )
    parser.add_argument(
        "--defaults",
        required=True,
        help="Path to the defaultConfigAttrs.json file containing default attributes.",
    )

    args = parser.parse_args()

    # Validate arguments
    if not os.path.isdir(args.base_dir):
        print(
            f"Error: Base directory '{args.base_dir}' does not exist or is not a directory."
        )
        return

    if not os.path.isfile(args.defaults):
        print(f"Error: Default attributes file '{args.defaults}' does not exist.")
        return

    print(
        f"Starting configuration update process with base directory '{args.base_dir}' and defaults file '{args.defaults}'."
    )
    find_and_update_configs(args.base_dir, args.defaults)
    print("Configuration update process completed successfully.")


if __name__ == "__main__":
    main()
