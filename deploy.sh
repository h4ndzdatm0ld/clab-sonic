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

# Function to extract hosts and perform ssh-copy-id
copy_ssh_key_to_clos_hosts() {
  local start_marker="###### CLAB-sonic-clos-START ######"
  local end_marker="###### CLAB-sonic-clos-END ######"
  local user="admin"
  local password="admin"
  local error_log="/tmp/ssh_copy_id_error.log"

  echo "Waiting 1.5 minute for devices to boot up..."
  sleep 90

  echo "Starting SSH key distribution to hosts listed between $start_marker and $end_marker in /etc/hosts..."

  # Extract the relevant IPv4 addresses between the markers in /etc/hosts
  awk "/$start_marker/,/$end_marker/" /etc/hosts | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | while read -r line; do
    local ip=$(echo "$line" | awk '{print $1}')

    echo "Processing host $ip..."
    retries=3
    while (( retries > 0 )); do
      sshpass -p "$password" ssh-copy-id -o StrictHostKeyChecking=no "$user@$ip" 2> "$error_log"
      if [[ $? -eq 0 ]]; then
        echo "SSH key successfully copied to $ip."
        break
      else
        echo "Failed to copy SSH key to $ip. Retries left: $(( retries - 1 ))."
        echo "Error details:"
        cat "$error_log"
        (( retries-- ))
        sleep 10
      fi
    done

    if (( retries == 0 )); then
      echo "ERROR: Exhausted retries for host $ip. Could not copy SSH key."
      echo "Final error details for $ip:"
      cat "$error_log"
    fi
  done

  # Clean up error log
  rm -f "$error_log"
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

# Run the containerlab deployment command
echo "Deploying containerlab setup..."
sudo containerlab -t sonic.yml deploy --reconfigure || echo "Deployment failed. Please check logs."

# Copy SSH keys for CLAB-sonic-clos hosts
copy_ssh_key_to_clos_hosts

echo "Deployment and SSH key setup for CLAB-sonic-clos completed."

echo "Deployment completed."