#!/bin/bash

# Exit immediately if any command fails
set -e

# Design Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}=================================================================${NC}"
echo -e "${BLUE}${BOLD}                 WboxAI macOS Builder Script                     ${NC}"
echo -e "${BLUE}${BOLD}=================================================================${NC}"

# 1. Check Python installation
echo -e "\n${BLUE}[1/5] Checking Python 3 installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: python3 could not be found. Please install Python 3 and try again.${NC}"
    exit 1
fi
python3 --version

# 2. Setup Virtual Environment
echo -e "\n${BLUE}[2/5] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "Creating virtual environment 'venv'..."
    python3 -m venv venv
else
    echo -e "Reusing existing virtual environment 'venv'..."
fi

# Activate virtual environment
echo -e "Activating virtual environment..."
source venv/bin/activate

# 3. Install Dependencies
echo -e "\n${BLUE}[3/5] Installing dependencies...${NC}"
echo -e "Upgrading pip..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo -e "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo -e "${RED}WARNING: requirements.txt not found. Installing pyqt6, PyInstaller, sounddevice, and mss manually...${NC}"
    pip install PyQt6 sounddevice numpy python-dotenv mss pillow pyobjc-framework-Cocoa websockets fastapi uvicorn deepgram-sdk pypdf openai httpx certifi
fi

echo -e "Installing PyInstaller..."
pip install pyinstaller

# 4. Clean previous builds
echo -e "\n${BLUE}[4/5] Cleaning up old builds...${NC}"
if [ -d "build" ] || [ -d "dist" ]; then
    echo -e "Removing build/ and dist/ directories..."
    rm -rf build dist
fi

# 5. Build Executable
echo -e "\n${BLUE}[5/6] Compiling macOS executable bundle...${NC}"
if [ -f "main.spec" ]; then
    echo -e "Running PyInstaller on main.spec..."
    pyinstaller --clean main.spec
else
    echo -e "${RED}ERROR: main.spec not found. Cannot build application.${NC}"
    exit 1
fi

# 6. Build DMG
echo -e "\n${BLUE}[6/6] Packaging macOS App into DMG...${NC}"
DMG_NAME="wboxai.dmg"
if [ -d "dist/wboxai.app" ]; then
    echo -e "Creating temporary DMG workspace..."
    rm -rf dist/dmg_temp
    mkdir -p dist/dmg_temp
    cp -R dist/wboxai.app dist/dmg_temp/
    ln -s /Applications dist/dmg_temp/Applications
    
    echo -e "Generating Disk Image (DMG)..."
    if [ -f "dist/$DMG_NAME" ]; then
        rm "dist/$DMG_NAME"
    fi
    hdiutil create -fs HFS+ -volname "WboxAI" -srcfolder dist/dmg_temp "dist/$DMG_NAME"
    rm -rf dist/dmg_temp
    echo -e "DMG packaging successful!"
else
    echo -e "${RED}ERROR: dist/wboxai.app not found. Cannot package DMG.${NC}"
    exit 1
fi

echo -e "\n${GREEN}${BOLD}=================================================================${NC}"
echo -e "${GREEN}${BOLD}                 BUILD COMPLETED SUCCESSFULLY!                   ${NC}"
echo -e "${GREEN}${BOLD}=================================================================${NC}"
echo -e "${BOLD}Your compiled macOS deliverables are located at:${NC}"
echo -e "  --> App Bundle: ${GREEN}${BOLD}$(pwd)/dist/wboxai.app${NC}"
echo -e "  --> DMG Image:  ${GREEN}${BOLD}$(pwd)/dist/$DMG_NAME${NC}"
echo -e ""
echo -e "To install, double-click the DMG and drag WboxAI to Applications, or open the app:"
echo -e "  open dist/wboxai.app"
echo -e ""
echo -e "Note: If you run this app on another Mac, you might need to bypass Gatekeeper with:"
echo -e "  xattr -cr dist/wboxai.app"
echo -e "================================================================="
