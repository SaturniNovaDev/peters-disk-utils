#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}*** Peter's Disk Utils - Linux Setup ***${NC}"

# 1. Choose Setup Mode
read -p "Use recommended defaults? (y/n): " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
    echo -e "${BLUE}Creating config.ini with Linux defaults...${NC}"
    cp config.template config.ini
    # Silently adjust defaults for Linux using sed
    sed -i 's/Verbose = .*/Verbose = False/' config.ini
    sed -i 's/Linux = .*/Linux = \/home/' config.ini
else
    echo -e "${YELLOW}*** Custom Configuration ***${NC}"
    
    # Prompting for values
    read -p "Verbose Mode (True/False) [False]: " verbose
    verbose=${verbose:-False}

    read -p "Error Limit [20]: " error_limit
    error_limit=${error_limit:-20}

    read -p "Show Summary at the end of a scan? (True/False) [True]: " show_summary
    show_summary=${show_summary:-True}

    read -p "Default Linux Scan Target [/home]: " target
    target=${target:-/home}
    
    read -p "Output JSON Name [disk-index.json]: " json_out
    json_out=${json_out:-disk-index.json}

    read -p "Output Chart Name [analysis.pdf]: " chart_out
    chart_out=${chart_out:-analysis.pdf}

    read -p "Output Error Log [nls-errors.log]: " log_file
    log_file=${log_file:-nls-errors.log}

    read -p "Which directories should the program ignore? [/proc, /sys, /dev, /run, /snap]: " linux_dirs
    linux_dirs=${linux_dirs:-/proc, /sys, /dev, /run, /snap}

    # Write the file line by line
    cat <<EOF > config.ini
[GENERAL]
Verbose = $verbose
ErrorLimit = $error_limit
ShowSummary = $show_summary

[PATHS]
JsonOutput = $json_out
ChartOutput = $chart_out
LogFile = $log_file

[DEFAULT_TARGETS]
Windows = C:/Users
Linux = $target

[EXCLUDE]
LinuxDirs = $linux_dirs
WindowsDirs = C:/System Volume Information, C:/\$Recycle.Bin
EOF
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Creating virtual environment... ${NC}"
    python3 -m venv .venv
fi

# 3. Activate and Install dependencies
echo -e "${BLUE}Installing/Updating dependencies...${NC}"
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo ""
echo -e "${BLUE}***${NC}"
echo ""

# 4. System Command Registration (The Fixed Wrapper Logic)
read -p "Would you like to register 'disk-nls' and 'disk-nav' as system commands? (y/n): " save_choice
if [[ "$save_choice" == "y" || "$save_choice" == "Y" ]]; then
    echo -e "${BLUE}Creating robust wrapper scripts in /usr/local/bin...${NC}"
    
    # Get absolute paths
    INSTALL_DIR=$(pwd)
    VENV_PYTHON="$INSTALL_DIR/.venv/bin/python3"

    # Create nls wrapper
    sudo bash -c "cat <<EOF > /usr/local/bin/disk-nls
#!/bin/bash
if [ \$# -gt 0 ]; then
    \"$VENV_PYTHON\" \"$INSTALL_DIR/disk-nls.py\" \"\$@\"
else
    \"$VENV_PYTHON\" \"$INSTALL_DIR/disk-nls.py\"
fi
EOF"

    # Create nav wrapper
    sudo bash -c "cat <<EOF > /usr/local/bin/disk-nav
#!/bin/bash
if [ \$# -gt 0 ]; then
    \"$VENV_PYTHON\" \"$INSTALL_DIR/disk-nav.py\" \"\$@\"
else
    \"$VENV_PYTHON\" \"$INSTALL_DIR/disk-nav.py\"
fi
EOF"

    sudo chmod +x /usr/local/bin/disk-nls /usr/local/bin/disk-nav
    echo -e "${GREEN}Commands registered successfully.${NC}"
fi


echo ""
echo -e "${GREEN}***${NC}"
echo ""

echo -e "${GREEN}Setup Complete! You can now use 'disk-nls' and 'disk-nav' globally.${NC}"