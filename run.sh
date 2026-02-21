#!/bin/bash

# run.sh - UVic Job Board Scraper Runner
# Provides three modes: manual login (no cookies), manual with cookie saving, and automated with saved cookies

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
COOKIE_DIR="${SCRIPT_DIR}/cookies"
CHROME_PROFILE_DIR="${COOKIE_DIR}/chrome_profile"
FIREFOX_PROFILE_DIR="${COOKIE_DIR}/firefox_profile"
LOG_FILE="${SCRIPT_DIR}/scraper.log"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"

# Colors for output (optional, can be removed if not wanted)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo "[*] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[error] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "[*] $1" | tee -a "$LOG_FILE"
}

# Setup virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    # Check if virtual environment already exists
    if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/activate" ]; then
        log_info "Virtual environment already exists at $VENV_DIR"
        return 0
    fi
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not installed. Please install Python3."
        exit 1
    fi
    
    # Create virtual environment
    log_info "Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR" || {
        log_error "Failed to create virtual environment. Trying with virtualenv..."
        if command -v virtualenv &> /dev/null; then
            virtualenv "$VENV_DIR" || {
                log_error "Failed to create virtual environment with virtualenv"
                exit 1
            }
        else
            log_error "Please install python3-venv or virtualenv"
            exit 1
        fi
    }
    
    log_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        log_info "Activating virtual environment..."
        source "$VENV_DIR/bin/activate"
        
        # Check if activation was successful
        if [ -n "$VIRTUAL_ENV" ]; then
            log_success "Virtual environment activated: $VIRTUAL_ENV"
        else
            log_error "Failed to activate virtual environment"
            exit 1
        fi
    else
        log_error "Virtual environment not found at $VENV_DIR"
        exit 1
    fi
}

# Install dependencies in virtual environment
install_dependencies() {
    log_info "Installing dependencies in virtual environment..."
    
    # Ensure we're in the virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        log_error "Not in virtual environment. Please activate first."
        exit 1
    fi
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip || {
        log_error "Failed to upgrade pip"
        exit 1
    }
    
    # Install requirements if requirements file exists
    if [ -f "$REQUIREMENTS_FILE" ]; then
        log_info "Installing packages from $REQUIREMENTS_FILE..."
        pip install -r "$REQUIREMENTS_FILE" || {
            log_error "Failed to install requirements"
            exit 1
        }
    else
        log_info "No requirements.txt found, installing selenium and requests..."
        pip install selenium requests || {
            log_error "Failed to install selenium and requests"
            exit 1
        }
    fi
    
    log_success "Dependencies installed"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Setup and activate virtual environment
    setup_venv
    activate_venv
    install_dependencies
    
    # Check for browsers
    if command -v google-chrome &> /dev/null || command -v chrome &> /dev/null || command -v chromium &> /dev/null; then
        CHROME_AVAILABLE=true
        log_info "Chrome/Chromium browser detected"
    else
        CHROME_AVAILABLE=false
        log_info "Chrome/Chromium not found, will use Firefox if available"
    fi
    
    if command -v firefox &> /dev/null; then
        FIREFOX_AVAILABLE=true
        log_info "Firefox browser detected"
    else
        FIREFOX_AVAILABLE=false
    fi
    
    if [ "$CHROME_AVAILABLE" = false ] && [ "$FIREFOX_AVAILABLE" = false ]; then
        log_error "No supported browser found. Please install Chrome or Firefox."
        exit 1
    fi
    
    log_success "Dependency check passed"
}

# Setup directories
setup_directories() {
    log_info "Setting up directories..."
    
    # Create required directories
    mkdir -p "${SCRIPT_DIR}/job_desc"
    mkdir -p "${SCRIPT_DIR}/resume"
    mkdir -p "${SCRIPT_DIR}/data"
    mkdir -p "$COOKIE_DIR"
    
    # Check for resume file
    if [ ! -f "${SCRIPT_DIR}/resume/"* ] && [ ! -f "${SCRIPT_DIR}/resume/"*.pdf ] && [ ! -f "${SCRIPT_DIR}/resume/"*.docx ] && [ ! -f "${SCRIPT_DIR}/resume/"*.txt ]; then
        log_info "No resume file found in resume/ directory. Please add your resume (PDF, DOCX, or TXT format)."
    fi
    
    log_success "Directory setup complete"
}

# Get browser driver
get_browser_driver() {
    local browser=$1
    
    if [ "$browser" = "chrome" ]; then
        # Try to find ChromeDriver
        if command -v chromedriver &> /dev/null; then
            log_info "ChromeDriver found in PATH"
            return 0
        fi
        
        # Check common locations
        local locations=(
            "/usr/local/bin/chromedriver"
            "/usr/bin/chromedriver"
            "/opt/chromedriver/chromedriver"
            "${HOME}/.local/bin/chromedriver"
        )
        
        for location in "${locations[@]}"; do
            if [ -f "$location" ] && [ -x "$location" ]; then
                log_info "ChromeDriver found at: $location"
                export PATH="$PATH:$(dirname "$location")"
                return 0
            fi
        done
        
        log_error "ChromeDriver not found. Please install ChromeDriver matching your Chrome version."
        log_info "You can download it from: https://chromedriver.chromium.org/"
        return 1
        
    elif [ "$browser" = "firefox" ]; then
        # Try to find geckodriver
        if command -v geckodriver &> /dev/null; then
            log_info "GeckoDriver found in PATH"
            return 0
        fi
        
        # Check common locations
        local locations=(
            "/usr/local/bin/geckodriver"
            "/usr/bin/geckodriver"
            "/opt/geckodriver/geckodriver"
            "${HOME}/.local/bin/geckodriver"
        )
        
        for location in "${locations[@]}"; do
            if [ -f "$location" ] && [ -x "$location" ]; then
                log_info "GeckoDriver found at: $location"
                export PATH="$PATH:$(dirname "$location")"
                return 0
            fi
        done
        
        log_error "GeckoDriver not found. Please install GeckoDriver for Firefox."
        log_info "You can download it from: https://github.com/mozilla/geckodriver/releases"
        return 1
    fi
    
    return 1
}

# Run scraper with specified mode
run_scraper() {
    local mode=$1
    local browser_choice=$2
    
    log_info "Starting scraper in mode: $mode"
    
    # Determine browser to use
    local browser=""
    if [ -n "$browser_choice" ]; then
        browser="$browser_choice"
    elif [ "$CHROME_AVAILABLE" = true ]; then
        browser="chrome"
        log_info "Using Chrome as default browser"
    elif [ "$FIREFOX_AVAILABLE" = true ]; then
        browser="firefox"
        log_info "Using Firefox as fallback browser"
    else
        log_error "No browser available"
        exit 1
    fi
    
    # Get driver for chosen browser
    if ! get_browser_driver "$browser"; then
        # Try fallback browser
        if [ "$browser" = "chrome" ] && [ "$FIREFOX_AVAILABLE" = true ]; then
            log_info "Falling back to Firefox"
            browser="firefox"
            if ! get_browser_driver "$browser"; then
                log_error "Failed to get driver for Firefox"
                exit 1
            fi
        elif [ "$browser" = "firefox" ] && [ "$CHROME_AVAILABLE" = true ]; then
            log_info "Falling back to Chrome"
            browser="chrome"
            if ! get_browser_driver "$browser"; then
                log_error "Failed to get driver for Chrome"
                exit 1
            fi
        else
            log_error "No working browser driver found"
            exit 1
        fi
    fi
    
    # Prepare environment variables for Python script
    local env_vars=""
    case "$mode" in
        1)
            # Mode 1: Manual login, no cookies
            log_info "Running in manual mode (no cookie saving)"
            env_vars="SCRAPER_MODE=manual SAVE_COOKIES=false"
            ;;
        2)
            # Mode 2: Manual login, save cookies
            log_info "Running in manual mode with cookie saving"
            env_vars="SCRAPER_MODE=manual SAVE_COOKIES=true"
            
            # Create browser profile directory
            if [ "$browser" = "chrome" ]; then
                mkdir -p "$CHROME_PROFILE_DIR"
                env_vars="$env_vars CHROME_USER_DATA_DIR=$CHROME_PROFILE_DIR"
            elif [ "$browser" = "firefox" ]; then
                mkdir -p "$FIREFOX_PROFILE_DIR"
                env_vars="$env_vars FIREFOX_PROFILE_DIR=$FIREFOX_PROFILE_DIR"
            fi
            ;;
        3)
            # Mode 3: Automated with saved cookies
            log_info "Running in automated mode with saved cookies"
            env_vars="SCRAPER_MODE=auto SAVE_COOKIES=false"
            
            # Check if cookies exist
            if [ "$browser" = "chrome" ]; then
                if [ ! -d "$CHROME_PROFILE_DIR" ] || [ -z "$(ls -A "$CHROME_PROFILE_DIR" 2>/dev/null)" ]; then
                    log_error "No saved Chrome cookies found. Please run mode 2 first to save cookies."
                    exit 1
                fi
                env_vars="$env_vars CHROME_USER_DATA_DIR=$CHROME_PROFILE_DIR"
            elif [ "$browser" = "firefox" ]; then
                if [ ! -d "$FIREFOX_PROFILE_DIR" ] || [ -z "$(ls -A "$FIREFOX_PROFILE_DIR" 2>/dev/null)" ]; then
                    log_error "No saved Firefox cookies found. Please run mode 2 first to save cookies."
                    exit 1
                fi
                env_vars="$env_vars FIREFOX_PROFILE_DIR=$FIREFOX_PROFILE_DIR"
            fi
            ;;
        *)
            log_error "Invalid mode: $mode"
            exit 1
            ;;
    esac
    
    # Add browser choice to environment
    env_vars="$env_vars SCRAPER_BROWSER=$browser"
    
    # Run the scraper
    log_info "Starting job_scrape.py with browser: $browser"
    cd "$SCRIPT_DIR"
    
    if eval "$env_vars python3 ${SCRIPT_DIR}/job_scrape.py"; then
        log_success "Scraping completed successfully"
        
        # Check if job descriptions were created
        if [ -d "${SCRIPT_DIR}/job_desc" ] && [ -n "$(ls -A "${SCRIPT_DIR}/job_desc" 2>/dev/null)" ]; then
            log_info "Found job descriptions, running matcher..."
            
            # Check if matcher API is running
            if curl -s http://localhost:3000 > /dev/null 2>&1; then
                if python3 "${SCRIPT_DIR}/match-client.py"; then
                    log_success "Matcher completed successfully"
                    log_info "Results saved to job_matches.txt"
                else
                    log_error "Matcher failed"
                fi
            else
                log_info "Matcher API not detected at http://localhost:3000"
                log_info "Skipping matching phase. Start the resume-matcher API to enable matching."
            fi
        else
            log_info "No job descriptions found. Skipping matcher."
        fi
    else
        log_error "Scraping failed"
        exit 1
    fi
}

# Clean up virtual environment (optional)
cleanup_venv() {
    log_info "Cleaning up..."
    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null || true
    fi
}

# Main menu
show_menu() {
    echo "========================================="
    echo "  UVic Job Board Scraper - Runner Script"
    echo "========================================="
    echo ""
    echo "Select mode:"
    echo "  1) Manual login (no cookie saving)"
    echo "  2) Manual login with cookie saving"
    echo "  3) Automated run with saved cookies"
    echo "  4) Check dependencies and setup"
    echo "  5) Clean virtual environment"
    echo "  6) Exit"
    echo ""
    echo -n "Enter choice [1-6]: "
}

# Main function
main() {
    # Clear log file
    > "$LOG_FILE"
    
    log_info "UVic Job Board Scraper Runner started"
    
    # Trap cleanup on exit
    trap cleanup_venv EXIT
    
    # Initial dependency check
    check_dependencies
    setup_directories
    
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                run_scraper 1
                ;;
            2)
                run_scraper 2
                ;;
            3)
                run_scraper 3
                ;;
            4)
                check_dependencies
                setup_directories
                ;;
            5)
                log_info "Cleaning virtual environment..."
                if [ -d "$VENV_DIR" ]; then
                    rm -rf "$VENV_DIR"
                    log_success "Virtual environment removed"
                else
                    log_info "Virtual environment not found"
                fi
                ;;
            6)
                log_info "Exiting..."
                exit 0
                ;;
            *)
                log_error "Invalid choice. Please enter 1-6."
                ;;
        esac
        
        echo ""
        echo -n "Press Enter to continue..."
        read -r
    done
}

# Run main function
main
