#!/bin/bash

# Set the directory name
DIR="clab-sonic"

# Function to remove offending keys from known_hosts in parallel
remove_offending_keys() {
  local ip_range="172.20.20.0/24"
  echo "Removing offending keys for IP range $ip_range from known_hosts..."

  # Generate IPs and remove offending keys in parallel
  seq 1 254 | xargs -P 10 -I {} bash -c '
    full_ip="172.20.20.{}"
    ssh-keygen -f "$HOME/.ssh/known_hosts" -R "$full_ip" > /dev/null 2>&1
  '
  echo "Cleared offending keys for IP range $ip_range."
}

# Destroy existing lab gracefully
destroy_existing_lab() {
  echo "Attempting to gracefully destroy any existing lab..."
  sudo containerlab -t sonic.yml destroy -c -a || echo "No existing lab detected or could not destroy the lab."
}

copy_ssh_key_to_clos_hosts() {
  local start_marker="###### CLAB-sonic-clos-START ######"
  local end_marker="###### CLAB-sonic-clos-END ######"
  local user="admin"
  local password="admin"
  local error_log="/tmp/ssh_copy_id_error.log"

  echo "Starting SSH key distribution to hosts listed between $start_marker and $end_marker in /etc/hosts..."

  # Extract hosts and distribute keys sequentially
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
        sleep 5  # Wait 5 seconds before retrying
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

# SSH into hosts and apply configuration in parallel
apply_config_and_change_hostname() {
  local start_marker="###### CLAB-sonic-clos-START ######"
  local end_marker="###### CLAB-sonic-clos-END ######"
  local user="admin"

  echo "Starting configuration replacement and hostname update in parallel..."

  # Extract hosts and run updates in parallel
  awk "/$start_marker/,/$end_marker/" /etc/hosts | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | while read -r line; do
    ip=$(echo "$line" | awk '{print $1}')
    hostname=$(echo "$line" | awk '{print $2}')
    (
      ssh "$user@$ip" <<EOF
        echo "Replacing configuration on $hostname..."
        sudo config replace /tmp/config_db.json -v
        echo "Configuration and hostname update completed for $hostname." 
EOF
      if [[ $? -eq 0 ]]; then
        echo "Successfully updated $hostname ($ip)."
      else
        echo "Failed to update $hostname ($ip)."
      fi
    ) &
  done
  wait
}

# # Clean up the lab and directory
clean_directory() {
  destroy_existing_lab

  if [ -d "$DIR" ]; then
    echo "Directory '$DIR' exists. Deleting it..."
    sudo rm -rf "$DIR"
    echo "Directory '$DIR' has been deleted."
  else
    echo "Directory '$DIR' does not exist. Skipping deletion."
  fi
}

# Main script execution
echo "Starting parallel operations..."

# Run all tasks in parallel where possible
{
  remove_offending_keys &
  clean_directory &
} && wait

echo "Deploying containerlab setup..."
sudo containerlab -t sonic.yml deploy --reconfigure || echo "Deployment failed. Please check logs."

echo "Waiting 1.5 minutes for devices to boot up..."
sleep 120

# Parallelize key copying and host configuration

echo "Deployment and configuration replacement completed."
copy_ssh_key_to_clos_hosts

apply_config_and_change_hostname

echo "Deployment and configuration replacement completed."