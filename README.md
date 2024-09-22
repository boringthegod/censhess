# censhess

## Description

Find IPs linked to your list of domains (and/or sub-domains) by turning Censys into an opensource tool (basically, by scrapping it).


Basically for all my neighborhood guys who are too lazy to read the doc / use the api / pay the api ([TLDR](https://twitter.com/gf_256/status/1716645916285768121))


## Requirements

- [Python 3](https://www.python.org/download/releases/3.0/)

- curl_cffi `pip install curl_cffi`

- **Residential proxies to change line 108 and 109**


## Usage

```bash
usage: censhess.py [-h] [--create-range] domains_file ips_output_file

Censhess

positional arguments:
  domains_file     File containing domains to scan
  ips_output_file  File to store found IP addresses

options:
  -h, --help       show this help message and exit
  --create-range   Generate IP ranges from 0 to 255 for each unique IP

Examples:
  ./censhess.py domains.txt ips.txt
  ./censhess.py domains.txt ips.txt --create-range
```