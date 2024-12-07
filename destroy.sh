#!/bin/bash

# Set the directory name
DIR="clab-sonic-5-stage-clos"

# Function to remove offending keys from known_hosts
remove_offending_keys() {
  local ip_range="172.20.20.0/24"
  echo "Removing offending keys for IP range $ip_range from known_hosts..."
  
  # Iterate through IPs in the specified range and remove them
  for ip in $(seq 1 254); do
    full_ip="172.20.20.$ip"
    ssh-keygen -f "$HOME/.ssh/known_hosts" -R "$full_ip" > /dev/null 2>&1
  done

  echo "Cleared offending keys for IP range $ip_range."
}

# Destroy existing lab gracefully
destroy_existing_lab() {
  echo "Attempting to gracefully destroy any existing lab..."
  sudo containerlab -t sonic.yml destroy -c -a || echo "No existing lab detected or could not destroy the lab."
}

# Destroy and clean the directory
clean_directory() {
  # Attempt to destroy the lab first
  destroy_existing_lab

  # Check if the directory exists and remove it
  if [ -d "$DIR" ]; then
    echo "Directory '$DIR' exists. Deleting it..."
    sudo rm -rf "$DIR"
    echo "Directory '$DIR' has been deleted."
  else
    echo "Directory '$DIR' does not exist. Skipping deletion."
  fi
}

# Remove offending keys from known_hosts
remove_offending_keys

# Clean up the lab and directory
clean_directory

echo "Lab destruction completed."