#!/bin/bash

# Configuration
FORTI_DIR="$HOME/fortibrute"
VENV_DIR="$FORTI_DIR/venv"
PYTHON_SCRIPT="fortibrute.py"
REQUIRED_PACKAGES=("requests")

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python3
if ! command_exists python3; then
    echo "Error: Python3 is not installed. Please install it and try again."
    exit 1
fi

# Check if Python script exists in current directory
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: $PYTHON_SCRIPT not found in the current directory."
    echo "Please ensure the Python script is present and named $PYTHON_SCRIPT."
    exit 1
fi

# Create ට

# Create directory if it doesn't exist
echo "Creating directory $FORTI_DIR..."
mkdir -p "$FORTI_DIR" || {
    echo "Error: Failed to create directory $FORTI_DIR."
    exit 1
}

# Copy Python script to fortibrute directory
echo "Copying $PYTHON_SCRIPT to $FORTI_DIR..."
cp "$PYTHON_SCRIPT" "$FORTI_DIR/" || {
    echo "Error: Failed to copy $PYTHON_SCRIPT to $FORTI_DIR."
    exit 1
}

# Create virtual environment
echo "Creating virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR" || {
    echo "Error: Failed to create virtual environment in $VENV_DIR."
    exit 1
}

# Activate virtual environment and install packages
echo "Activating virtual environment and installing packages..."
source "$VENV_DIR/bin/activate" || {
    echo "Error: Failed to activate virtual environment."
    exit 1
}

for package in "${REQUIRED_PACKAGES[@]}"; do
    echo "Installing $package..."
    pip install "$package" || {
        echo "Error: Failed to install $package."
        deactivate
        exit 1
    }
done

# Deactivate virtual environment
deactivate

# Instructions for running the script
echo "Setup complete!"
echo "To run the script, use the following commands:"
echo "  cd $FORTI_DIR"
echo "  source venv/bin/activate"
echo "  python $PYTHON_SCRIPT --targetservername <server> --userfile <userfile> --passfile <passfile>"
echo "To deactivate the virtual environment after use:"
echo "  deactivate"
