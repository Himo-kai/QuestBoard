# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import sys
import logging
from pathlib import Path
import re
import clipboard
import praw
from dotenv import load_dotenv
from utils import print_header, print_colored, colored
import subprocess

# Get logger - configuration is handled in app.py
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent duplicate logs

def check_xclip_installed():
    """Check if xclip is installed"""
    try:
        subprocess.run(['which', 'xclip'], check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False



ENV_FILE = ".env"

# Check if running in a virtual environment
IN_VENV = hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix

def validate_credentials():
    """Validate Reddit credentials in .env file."""
    try:
        logger.info("Validating Reddit credentials...")
        load_dotenv()
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        
        logger.debug(f"Client ID: {'Present' if client_id else 'Missing'}")
        logger.debug(f"Client Secret: {'Present' if client_secret else 'Missing'}")
        
        if not client_id or not client_secret:
            logger.warning("Missing one or both required credentials")
            return False
            
        # Strip whitespace from credentials
        client_id = client_id.strip()
        client_secret = client_secret.strip()
        
        # More permissive validation for client ID and secret
        if not client_id or len(client_id) < 5:  # Minimum length check
            logger.error(f"Client ID is too short: {client_id}")
            return False
            
        if not client_secret or len(client_secret) < 5:  # Minimum length check
            logger.error("Client secret is too short")
            return False
        
        logger.info("Credentials format is valid, testing Reddit API connection...")
        
        # Test credentials by trying to create a Reddit instance
        try:
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="QuestBoard/1.0"
            )
            # Try a simple operation to verify credentials
            reddit.read_only = True
            subreddit = reddit.subreddit("donedirtcheap")
            # Just check if we can connect
            subreddit.display_name
            logger.info("Successfully validated Reddit credentials")
            return True
        except Exception as e:
            logger.error(f"Reddit API connection failed: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error in validate_credentials: {str(e)}")
        return False

def create_env_file():
    """Create an empty .env file if it doesn't exist"""
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'w') as f:
            f.write("# Reddit API credentials\n")
            f.write("REDDIT_CLIENT_ID=\n")
            f.write("REDDIT_CLIENT_SECRET=\n")
            f.write("REDDIT_USER_AGENT=QuestBoard/1.0\n")
        print_colored("Created empty .env file", "1;32")

def print_header():
    print_colored("\n⚔️  Welcome to QuestBoard's Reddit Setup Wizard ⚔️", "1;34")
    print_colored("This wizard will help you set up your Reddit API credentials.", "1;34")
    print("The wizard can automatically detect credentials from your clipboard.")
    print("\nPress Enter to continue...")
    input()

def print_instructions():
    print_colored("\n1. Create Your Reddit Application", "1;33")
    print("First, make sure you're logged into Reddit: https://www.reddit.com")
    print("\nThen, create your application:")
    print("   1. Visit: https://www.reddit.com/prefs/apps")
    print("   2. Click 'create another app...' at the bottom of the page")
    print("   3. Fill in the form with these details:")
    print(f"      - Name: QuestBoard Reddit Scraper")
    print("      - App type: script")
    print("      - About URL: https://github.com/Himo-kai/questboard")
    print("      - Redirect URI: http://localhost:8080")
    print_colored("\n2. Copy Your Credentials", "1;33")
    print("After creating, you'll see two important values:")
    print("   - Client ID (web app ID)")
    print("   - Secret Key")
    print("\nYou can copy them in these ways:")
    print("   1. Copy both values to your clipboard")
    print("   2. Or enter them manually")
    print("\nFor more help, check Reddit's API documentation:")
    print("   - Reddit API Guide: https://www.reddit.com/dev/api")
    print("   - Reddit API Wiki: https://github.com/reddit-archive/reddit/wiki/API")
    print("\nPress Enter to continue...")
    input()

def extract_credentials(text):
    """Extract client ID and secret from clipboard text"""
    # Common patterns for Reddit credentials
    patterns = {
        'client_id': r'client_id[:\s]*([a-zA-Z0-9]+)',
        'secret': r'secret[:\s]*([a-zA-Z0-9]+)',
        'web_app_id': r'web_app_id[:\s]*([a-zA-Z0-9]+)',
        'client_secret': r'client_secret[:\s]*([a-zA-Z0-9]+)'
    }
    
    matches = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            matches[key] = match.group(1)
    
    return matches

def get_input(prompt: str, default: str = None, required: bool = False, clipboard_check: bool = False):
    """
    Get user input with optional default value, stripping whitespace.
    If clipboard_check is True, tries to extract credentials from clipboard first.
    If required is True, keeps prompting until a non-empty input is provided.
    """
    # Check clipboard first if requested
    if clipboard_check and check_xclip_installed():
        try:
            import subprocess
            clipboard = subprocess.check_output(['xclip', '-o', '-selection', 'clipboard']).decode('utf-8')
            if any(x in clipboard.lower() for x in ['client_id', 'client_secret', 'secret']):
                return extract_credentials(clipboard)
        except Exception as e:
            logger.debug(f"Could not read from clipboard: {e}")
    
    while True:
        # Format prompt with default value if provided
        if default is not None:
            prompt_text = f"{prompt} [{'none' if default == '' else default}]: "
        else:
            prompt_text = f"{prompt}: "
        
        try:
            user_input = input(prompt_text).strip()
            user_input = user_input if user_input else (default or "")
            
            # If input is required and empty, show error and prompt again
            if required and not user_input:
                print_colored("This field is required. Please enter a value.", "1;31")
                continue
                
            return user_input
            
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user.")
            sys.exit(1)

def write_env_file(client_id, client_secret, user_agent):
    with open(ENV_FILE, "w") as f:
        f.write(f"REDDIT_CLIENT_ID={client_id}\n")
        f.write(f"REDDIT_CLIENT_SECRET={client_secret}\n")
        f.write(f"REDDIT_USER_AGENT={user_agent}\n")
    
    print_colored("✅ Setup complete!", "1;32")
    print("Your credentials have been saved to .env file.")
    print("You can now run the QuestBoard application.")

def main():
    # Check if we're in a virtual environment
    if not IN_VENV:
        print_colored("⚠ Warning: It's recommended to run this wizard in a virtual environment.", "1;33")
        print("Would you like to continue anyway? (y/n)")
        if input().lower() != 'y':
            print("Exiting setup wizard.")
            sys.exit(1)

    # Create empty .env file if it doesn't exist
    create_env_file()

    # Check for xclip installation
    if not check_xclip_installed():
        print_colored("⚠️ Clipboard support not available", "1;33")
        print("You can still enter credentials manually.")
        print("If you want to enable clipboard support, install xclip:")
        print("  For Debian/Ubuntu/Mint: sudo apt-get install xclip")
        print("  For Arch/Manjaro: sudo pacman -S xclip")
        print("  For Fedora: sudo dnf install xclip")
        print("\nPress Enter to continue with manual input...")
        input()

    print_header()
    print_instructions()

    # Try to get credentials from clipboard first
    print("\nChecking clipboard for Reddit API credentials...")
    credentials = get_input("Press Enter to check clipboard or type 'skip' to enter manually", default="", clipboard_check=True)
    
    if isinstance(credentials, dict):  # Clipboard credentials found
        client_id = credentials.get('client_id') or credentials.get('web_app_id', '')
        client_secret = credentials.get('secret') or credentials.get('client_secret', '')
        if client_id and client_secret:
            print_colored("\n✅ Successfully extracted credentials from clipboard!", "1;32")
            print(f"Client ID: {client_id}")
            print(f"Client Secret: {'*' * len(client_secret)}")
        else:
            print_colored("\n⚠ Could not extract complete credentials from clipboard. Please enter manually.", "1;33")
            client_id = ""
            client_secret = ""
    
    # If we don't have credentials yet, ask for manual input
    if not isinstance(credentials, dict) or not (client_id and client_secret):
        print_colored("\nPlease enter your Reddit API credentials:", "1;34")
        print("(You can copy these from your Reddit app settings at https://www.reddit.com/prefs/apps)")
        
        while True:
            client_id = get_input("Enter your Reddit Client ID (14+ characters)", required=True, clipboard_check=False)
            # Validate client ID (allowing hyphens and other common characters)
            if len(client_id) < 10:
                print_colored("❌ Invalid Client ID. Must be at least 10 characters long.", "1;31")
                continue
            break
        
        while True:
            client_secret = get_input("Enter your Reddit Client Secret (20+ characters)", required=True, clipboard_check=False)
            # Validate client secret (allowing special characters)
            if len(client_secret) < 5:  # Minimum length check (Reddit's actual minimum)
                print_colored("❌ Invalid Client Secret. Must be at least 5 characters long.", "1;31")
                continue
            break

    # Get user agent (always manual input)
    user_agent = get_input("Enter a user agent string", "QuestBoard/1.0 by your_username")

    # Write to .env file
    write_env_file(client_id, client_secret, user_agent)

if __name__ == "__main__":
    main()
