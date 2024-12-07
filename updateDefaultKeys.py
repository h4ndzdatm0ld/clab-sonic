import os
import json
import argparse
import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_json(file_path: str) -> Dict:
    """Load JSON data from a file."""
    logger.info(f"Loading JSON data from {file_path}...")
    with open(file_path, 'r') as file:
        data = json.load(file)
    logger.info(f"Successfully loaded JSON data from {file_path}.")
    return data


def update_dict(target: Dict[str, Any], defaults: Dict[str, Any]) -> bool:
    """
    Recursively update a dictionary with default values if keys are missing.

    Args:
        target (Dict[str, Any]): Target dictionary to update.
        defaults (Dict[str, Any]): Default dictionary to compare and update from.

    Returns:
        bool: True if any updates were made, False otherwise.
    """
    updated = False

    for key, value in defaults.items():
        if key not in target:
            logger.warning(f"Key '{key}' is missing. Adding it with default value: {value}")
            target[key] = value
            updated = True
        elif isinstance(value, dict) and isinstance(target[key], dict):
            logger.info(f"Key '{key}' exists. Checking nested keys...")
            if update_dict(target[key], value):
                updated = True

    return updated


def update_config(default_attrs: Dict, config_path: str, dry_run: bool) -> None:
    """
    Update a config file with default attributes if keys are missing.

    Args:
        default_attrs (Dict): Default attributes to add if missing.
        config_path (str): Path to the configuration file to update.
        dry_run (bool): If True, do not modify the files but show changes.
    """
    logger.info(f"Reading configuration file: {config_path}")
    with open(config_path, 'r') as file:
        config_data = json.load(file)

    if update_dict(config_data, default_attrs):
        if dry_run:
            logger.info(f"Dry run enabled. No changes will be made to {config_path}.")
        else:
            with open(config_path, 'w') as file:
                json.dump(config_data, file, indent=4)
            logger.info(f"Updated {config_path} with missing keys.")
    else:
        logger.info(f"No updates needed for {config_path}.")


def find_and_update_configs(base_dir: str, default_attrs_path: str, dry_run: bool) -> None:
    """
    Find and update all node config files with default attributes.

    Args:
        base_dir (str): Base directory to search for node configuration files.
        default_attrs_path (str): Path to the JSON file with default attributes.
        dry_run (bool): If True, do not modify the files but show changes.
    """
    logger.info(f"Loading default attributes from {default_attrs_path}...")
    default_attrs = load_json(default_attrs_path)

    logger.info(f"Starting search for configuration files in {base_dir}...")
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                config_path = os.path.join(root, file)
                logger.info(f"Found configuration file: {config_path}")
                update_config(default_attrs, config_path, dry_run)

    logger.info("Finished processing all configuration files.")


def main() -> None:
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Update node configuration files with default attributes."
    )

    # Mutually exclusive group for dry-run and non-dry-run modes
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Enable dry-run mode (default). No changes will be made to the files.",
    )
    group.add_argument(
        "--non-dry-run",
        action="store_false",
        dest="dry_run",
        help="Disable dry-run mode. Changes will be made to the files.",
    )

    args = parser.parse_args()

    # Paths are now constants
    base_dir = "startupConfigs"
    default_attrs_path = "defaultConfigAttrs.json"

    # Validate paths
    if not os.path.isdir(base_dir):
        logger.error(f"Base directory '{base_dir}' does not exist or is not a directory.")
        return

    if not os.path.isfile(default_attrs_path):
        logger.error(f"Default attributes file '{default_attrs_path}' does not exist.")
        return

    dry_run = args.dry_run
    logger.info(f"Starting configuration update process with dry-run set to {dry_run}.")
    find_and_update_configs(base_dir, default_attrs_path, dry_run)
    logger.info("Configuration update process completed successfully.")


if __name__ == "__main__":
    main()