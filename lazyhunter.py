import requests
import datetime
import argparse
import signal
import os
import time
import random

# ANSI color codes
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Hardcoded banner in green
BANNER = f"{GREEN}"
BANNER += "______                          ______  __             _____\n"
BANNER += "___  / ______ __________  __    ___  / / /___  __________  /_____________\n"
BANNER += "__  /  _  __ `/__  /_  / / /    __  /_/ /_  / / /_  __ \  __/  _ \_  ___/\n"
BANNER += "_  /___/ /_/ /__  /_  /_/ /     _  __  / / /_/ /_  / / / /_ /  __/  /\n"
BANNER += "/_____\__,_/ _____/\__, /      /_/ /_/  \__,_/ /_/ /_/\__/ \___//_/\n"
BANNER += "                   /____/                                           v1.0\n"
BANNER += "                                    LazyHunter Recon Tool Dev @iamunixtz\n"
BANNER += f"{RESET}"

def signal_handler(sig, frame):
    choice = input(f"\n{YELLOW}Do you want to quit? (y/n): {RESET}")
    if choice.lower() == 'y':
        print(f"{RED}Exiting...{RESET}")
        exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Get severity level color
def get_severity_color(cvss_score):
    if cvss_score is None:
        cvss_score = 0
    if cvss_score >= 9.0:
        return f"{RED}[CRITICAL]{RESET}"
    elif cvss_score >= 7.0:
        return f"{RED}[HIGH]{RESET}"
    elif cvss_score >= 4.0:
        return f"{YELLOW}[MEDIUM]{RESET}"
    else:
        return f"{GREEN}[LOW]{RESET}"

# Fetch CVE details
def fetch_cve_details(cve_id):
    url = f"https://cvedb.shodan.io/cve/{cve_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

# Log results
def log_results(ip, data, show_cves, show_ports, show_hosts, show_cve_ports):
    timestamp = f"{YELLOW}[INFO]{RESET}"
    log_lines = []

    if show_ports or not any([show_cves, show_hosts, show_cve_ports]):
        if data.get("ports"):
            ports_colored = ', '.join(f"{GREEN}{port}{RESET}" for port in data["ports"])
            log_lines.append(f"{timestamp} {BLUE}[{ip}]{RESET} [PORTS: {GREEN}{ports_colored}{RESET}]")

    if show_cves or not any([show_ports, show_hosts, show_cve_ports]):
        if data.get("vulns"):
            for cve in data["vulns"]:
                cve_info = fetch_cve_details(cve)
                severity = get_severity_color(cve_info.get("cvss_v3", 0))
                log_lines.append(f"{timestamp} {BLUE}[{ip}]{RESET} [{GREEN}{cve}{RESET}] {severity}")

    if show_cve_ports or not any([show_cves, show_ports, show_hosts]):
        if data.get("vulns") and data.get("ports"):
            ports_colored = ', '.join(f"{GREEN}{port}{RESET}" for port in data["ports"])
            for cve in data["vulns"]:
                cve_info = fetch_cve_details(cve)
                severity = get_severity_color(cve_info.get("cvss_v3", 0))
                log_lines.append(f"{timestamp} {BLUE}[{ip}]{RESET} [{GREEN}{cve}{RESET}] {severity} [PORTS: {GREEN}{ports_colored}{RESET}]")

    if show_hosts or not any([show_cves, show_ports, show_cve_ports]):
        if data.get("hostnames"):
            hostnames_colored = ', '.join(f"{GREEN}{host}{RESET}" for host in data["hostnames"])
            log_lines.append(f"{timestamp} {BLUE}[{ip}]{RESET} [HOSTNAMES: {GREEN}{hostnames_colored}{RESET}]")

    for line in log_lines:
        print(line)
        time.sleep(10)  # Delay for output

# Process a single IP
def process_ip(ip, show_cves, show_ports, show_hosts, show_cve_ports):
    url = f"https://internetdb.shodan.io/{ip}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        log_results(ip, data, show_cves, show_ports, show_hosts, show_cve_ports)
    else:
        print(f"{RED}[ERROR]{RESET} Failed to fetch data for {ip}")

# Main function
def main():
    os.system("clear")  # Clear screen
    print(BANNER.center(80))
    parser = argparse.ArgumentParser(description="LazyHunter - Automated Bug Hunting Recon Tool")
    parser.add_argument("-f", "--file", help="File containing a list of IPs")
    parser.add_argument("--ip", help="Single IP to scan")
    parser.add_argument("--cves", action="store_true", help="Show CVEs")
    parser.add_argument("--ports", action="store_true", help="Show open ports")
    parser.add_argument("--host", action="store_true", help="Show hostnames")
    parser.add_argument("--cve+ports", dest="cve_ports", action="store_true", help="Show CVEs with severity level and open ports")
    args = parser.parse_args()

    if args.ip:
        print(f"{YELLOW}[INFO]{RESET} Target: {args.ip}")
        process_ip(args.ip, args.cves, args.ports, args.host, args.cve_ports)
    elif args.file:
        with open(args.file, "r") as file:
            ips = file.read().splitlines()
            print(f"{YELLOW}[INFO]{RESET} Target File: {os.path.basename(args.file)}")
            print(f"{YELLOW}[INFO]{RESET} Total IPs: {len(ips)}")
            for ip in ips:
                process_ip(ip, args.cves, args.ports, args.host, args.cve_ports)
    else:
        print(f"{YELLOW}[INFO]{RESET} No specific options selected, displaying all results...")
        process_ip("127.0.0.1", True, True, True, True)  # Default to all enabled

    print(f"\n{YELLOW}[INFO]{RESET} Scan Completed")

if __name__ == "__main__":
    main()
