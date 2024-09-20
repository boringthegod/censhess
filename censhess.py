from curl_cffi import requests
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time

# Proxy configuration remains the same
proxies = {
    "http": "socks5://",
    "https": "socks5://"
}

# Regex pattern to match IPv4 addresses inside <strong> tags
ipv4_pattern = re.compile(r'<strong>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</strong>')

# Lock to prevent race conditions
lock = Lock()

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

            # Extract IPv4 addresses
            ipv4_addresses = ipv4_pattern.findall(response.text)

            # Write the IP addresses to the file
            if ipv4_addresses:
                with lock:
                    with open('ips.txt', 'a') as f:
                        for ip in ipv4_addresses:
                            f.write(f'{domain}: {ip}\n')
            break  # Exit the loop if the request is successful

        except Exception as e:
            print(f"Error processing {domain} on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying {domain}...")
                time.sleep(2)  # Optional: Add a small delay between retries

    if attempt == max_retries - 1:
        print(f"Failed to process {domain} after {max_retries} attempts.")

def main():
    # Read domains from the file
    with open('domains.txt', 'r') as file:
        domains = file.readlines()

    # Create a ThreadPoolExecutor with 10 threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_domain, domains)

if __name__ == "__main__":
    main()
