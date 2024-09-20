après 

`awk -F': ' '{print $2}' ips.txt | sort -u > onlyips2.txt`

`awk -F '.' '{print $1"."$2"."$3}' onlyips2.txt | sort -u | while read subnet; do seq 0 254 | awk -v prefix="$subnet" '{print prefix"."$1}'; done > ip_ranges.txt`
