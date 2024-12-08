import os
import json
import yaml
import argparse
from typing import Any, Dict
from loguru import logger


class ConfigGenerator:
    def __init__(self, base_dir: str, default_attrs_path: str, overrides_path: str, dry_run: bool = True):
        self.base_dir = base_dir
        self.default_attrs_path = default_attrs_path
        self.overrides_path = overrides_path
        self.dry_run = dry_run

    @staticmethod
    def load_json(file_path: str) -> Dict[str, Any]:
        """Load JSON data from a file."""
        logger.info(f"Loading JSON data from {file_path}...")
        with open(file_path, 'r') as file:
            data = json.load(file)
        logger.info(f"Successfully loaded JSON data from {file_path}.")
        return data

    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """Load YAML data from a file."""
        logger.info(f"Loading YAML data from {file_path}...")
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        logger.info(f"Successfully loaded YAML data from {file_path}.")
        return data

    @staticmethod
    def update_dict(target: Dict[str, Any], defaults: Dict[str, Any], path: str = "") -> bool:
        """
        Recursively update a dictionary with default values if keys are missing.

        Args:
            target (Dict[str, Any]): Target dictionary to update.
            defaults (Dict[str, Any]): Default dictionary to compare and update from.
            path (str): The dot-separated path to the current dictionary level.

        Returns:
            bool: True if any updates were made, False otherwise.
        """
        updated = False

        for key, value in defaults.items():
            current_path = f"{path}.{key}" if path else key
            if key not in target:
                logger.warning(f"Adding missing key '{current_path}' with value: {value}")
                target[key] = value
                updated = True
            elif isinstance(value, dict) and isinstance(target[key], dict):
                logger.info(f"Key '{current_path}' exists. Checking nested keys...")
                if ConfigGenerator.update_dict(target[key], value, current_path):
                    updated = True
            else:
                if target[key] != value:
                    logger.warning(
                        f"Updating key '{current_path}': Old Value: {target[key]} -> New Value: {value}"
                    )
                    target[key] = value
                    updated = True

        return updated

    def apply_defaults(self) -> None:
        """
        Apply default attributes to all JSON configuration files in the base directory.
        """
        logger.info(f"Loading default attributes from {self.default_attrs_path}...")
        default_attrs = self.load_json(self.default_attrs_path)

        logger.info(f"Searching for configuration files in {self.base_dir}...")
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith(".json"):
                    config_path = os.path.join(root, file)
                    logger.info(f"Found configuration file: {config_path}")
                    self.update_config(default_attrs, config_path)

        logger.info("Completed applying default attributes.")

    def apply_overrides(self) -> None:
        """
        Apply overrides from the YAML file to specific device configurations.
        """
        logger.info(f"Loading overrides from {self.overrides_path}...")
        overrides_data = self.load_yaml(self.overrides_path)

        overrides = overrides_data.get("overrides", {})
        if not overrides:
            logger.warning("No overrides found in the YAML file.")
            return

        for hostname, override_content in overrides.items():
            config_path = os.path.join(self.base_dir, hostname, "config", "config_db.json")

            if not os.path.isfile(config_path):
                logger.warning(f"Config file for hostname '{hostname}' not found at {config_path}. Skipping.")
                continue

            logger.info(f"Applying overrides for hostname '{hostname}'...")
            self.update_config(override_content, config_path)

        logger.info("Override application process completed.")

    def update_config(self, updates: Dict[str, Any], config_path: str) -> None:
        """
        Update a configuration file with the given updates.

        Args:
            updates (Dict): Updates to apply to the configuration.
            config_path (str): Path to the configuration file to update.
        """
        logger.info(f"Reading configuration file: {config_path}")
        with open(config_path, 'r') as file:
            config_data = json.load(file)

        if self.update_dict(config_data, updates):
            if self.dry_run:
                logger.info(f"[DRY RUN] No changes will be made to {config_path}.")
            else:
                with open(config_path, 'w') as file:
                    json.dump(config_data, file, indent=4)
                logger.info(f"Updated {config_path} with provided updates.")
        else:
            logger.info(f"No updates needed for {config_path}.")

    def run(self) -> None:
        """
        Run the configuration generation process.
        """
        logger.info("Starting configuration generation process.")
        self.apply_defaults()
        self.apply_overrides()
        logger.info("Configuration generation process completed.")

def main() -> None:
    """
    Main entry point for the CLI tool.
    """
    parser = argparse.ArgumentParser(
        description="Generate node configuration files by applying default attributes and overrides."
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

    base_dir = "startupConfigs"
    default_attrs_path = "data/defaultConfigAttrs.json"
    overrides_path = "data/overrides.yml"

    # Validate paths
    if not os.path.isdir(base_dir):
        logger.error(f"Base directory '{base_dir}' does not exist or is not a directory.")
        return

    if not os.path.isfile(default_attrs_path):
        logger.error(f"Default attributes file '{default_attrs_path}' does not exist.")
        return

    if not os.path.isfile(overrides_path):
        logger.error(f"Overrides file '{overrides_path}' does not exist.")
        return

    # Initialize and run the configuration generator
    config_generator = ConfigGenerator(
        base_dir=base_dir,
        default_attrs_path=default_attrs_path,
        overrides_path=overrides_path,
        dry_run=args.dry_run
    )
    config_generator.run()


if __name__ == "__main__":
    main()