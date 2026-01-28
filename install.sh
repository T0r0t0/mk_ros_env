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

# Reload .bashrc
exec bash
