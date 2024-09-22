from curl_cffi import requests
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time
import sys
import os
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Censhess')
    parser.add_argument('domains_file', type=str, help='File containing domains to scan')
    parser.add_argument('ips_output_file', type=str, help='File to store found IP addresses')
    parser.add_argument('--create-range', action='store_true', help='Generate IP ranges from 0 to 255 for each unique IP')
    return parser.parse_args()

def generate_ip_ranges(ips_file):
    ip_ranges_file = ips_file.replace('.txt', '_ranges.txt')
    unique_subnets = set()

    with open(ips_file, 'r') as f:
        for line in f:
            ip = line.split(': ')[1].strip()
            subnet = '.'.join(ip.split('.')[:3])
            unique_subnets.add(subnet)

    with open(ip_ranges_file, 'w') as f:
        for subnet in sorted(unique_subnets):
            for i in range(255):
                f.write(f'{subnet}.{i}\n')

    print(f"IP ranges generated in {ip_ranges_file}")

def remove_duplicates(file_path):
    seen = set()
    with open(file_path, 'r') as infile, open(file_path + '.tmp', 'w') as outfile:
        for line in infile:
            ip = line.split(': ')[1].strip()
            if ip not in seen:
                outfile.write(line)
                seen.add(ip)
    os.replace(file_path + '.tmp', file_path)

def process_domain(domain):
    domain = domain.strip()
    max_retries = 3
    for attempt in range(max_retries):
        try:
            headers = {
                'Host': 'search.censys.io',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.5',
                'X-Requested-With': 'XMLHttpRequest',
                'Dnt': '1',
                'Referer': f'https://search.censys.io/search?resource=hosts&sort=RELEVANCE&per_page=100&virtual_hosts=EXCLUDE&q={domain}',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
            }

            params = {
                'resource': 'hosts',
                'sort': 'RELEVANCE',
                'per_page': '100',
                'virtual_hosts': 'EXCLUDE',
                'q': domain,
            }

            response = requests.get('https://search.censys.io/_search', params=params, headers=headers, proxies=proxies, timeout=30, impersonate="chrome")

            ipv4_addresses = ipv4_pattern.findall(response.text)

            if ipv4_addresses:
                with lock:
                    with open(ips_output_file, 'a') as f:
                        for ip in ipv4_addresses:
                            f.write(f'{domain}: {ip}\n')
            break

        except Exception as e:
            print(f"Error processing {domain} on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying {domain}...")
                time.sleep(2)

    if attempt == max_retries - 1:
        print(f"Failed to process {domain} after {max_retries} attempts.")

def main():
    args = parse_arguments()

    with open(args.domains_file, 'r') as file:
        domains = file.readlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_domain, domains)

    remove_duplicates(args.ips_output_file)

    if args.create_range:
        generate_ip_ranges(args.ips_output_file)

if __name__ == "__main__":
    ipv4_pattern = re.compile(r'<strong>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</strong>')
    lock = Lock()
    proxies = {
        "http": "socks5:YOUR_PROXY//",
        "https": "socks5:YOUR_PROXY//"
    }
    main()
