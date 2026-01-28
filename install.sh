#!/bin/bash

# Define the line to add
NEW_PATH_LINE="export PATH=\$PATH:$(pwd)"

# Check if the line already exists in .bashrc
if ! grep -qF "$NEW_PATH_LINE" /home/$(whoami)/.bashrc; then
    # Append the line if it doesn't exist
    echo "$NEW_PATH_LINE" >> /home/$(whoami)/.bashrc
    echo "Added $(pwd) to PATH in .bashrc"
else
    echo "$(pwd) is already in PATH in .bashrc"
fi


echo "Check if docker installed ... "

if !command -v docker &> /dev/null; then
    echo "Docker not found"
    echo "Installing docker. This may take a few minutes..."
    # Add Docker's official GPG key:
    sudo apt update
    sudo apt install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

    sudo apt update

    sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

else
    echo Docker found.
fi

echo installation finished


# Reload .bashrc
exec bash

