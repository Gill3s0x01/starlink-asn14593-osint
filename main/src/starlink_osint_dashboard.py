import requests
import matplotlib.pyplot as plt
from collections import Counter
import subprocess
import ipaddress
import platform
import time
import json
import csv


def get_json_with_retry(url, max_retries=5, delay=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-OSINT-Dashboard"
    }
    for attempt in range(max_retries):
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            print(
                f"⚠️ Rate limit (HTTP 429) em {url} — loading {delay}s and try again..."
            )
            time.sleep(delay)
        else:
            print(f"⚠️ Erro HTTP {resp.status_code} for {url}")
            break
    return None


asn = "14593"

base_url = f"https://api.bgpview.io/asn/{asn}"
response = requests.get(f"{base_url}/prefixes")
data = response.json()

prefixes = data["data"]["ipv4_prefixes"]

countries = []
prefix_details = []

for p in prefixes:
    country_code = p["country_code"] if p["country_code"] else "Unknown"
    countries.append(country_code)
    prefix_details.append(
        {
            "prefix": p["prefix"],
            "country_code": country_code,
            "is_brazil": country_code == "BR",
        }
    )


country_counts = Counter(countries)


total = sum(country_counts.values())
grouped_counts = {}

for country, count in country_counts.items():
    percentage = (count / total) * 100
    if percentage >= 2:
        grouped_counts[country] = count
    else:
        grouped_counts["Others"] = grouped_counts.get("Others", 0) + count


plt.figure(figsize=(10, 6))
colors = [
    "#008000" if country == "BR" else "steelblue" for country in grouped_counts.keys()
]

plt.bar(grouped_counts.keys(), grouped_counts.values(), color=colors)
plt.title("Distribution of Starlink Prefixes by Country")
plt.xlabel("Country")
plt.ylabel("Number of Prefixes")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


plt.figure(figsize=(8, 8))
explode = [0.1 if country == "BR" else 0 for country in grouped_counts.keys()]

plt.pie(
    grouped_counts.values(),
    labels=grouped_counts.keys(),
    autopct="%1.1f%%",
    explode=explode,
    startangle=140,
)
plt.title("Distribution (%) of Starlink Prefixes by Country")
plt.tight_layout()
plt.show()


with open("prefixes_starlink_details.csv", "w", newline="") as csvfile:
    fieldnames = ["prefix", "country_code", "is_brazil"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in prefix_details:
        writer.writerow(item)


with open("prefixes_for_countries.csv", "w") as f:
    f.write("country_code,prefix_count,percentage\n")
    for country, count in country_counts.items():
        percentage = (count / total) * 100
        f.write(f"{country},{count},{percentage:.2f}\n")


json_data = []
for country, count in country_counts.items():
    percentage = (count / total) * 100
    json_data.append(
        {
            "country_code": country,
            "prefix_count": count,
            "percentage": round(percentage, 2),
        }
    )

with open("prefixes_for_countries.json", "w") as f:
    json.dump(json_data, f, indent=4)


with open("prefixes_starlink_details.json", "w") as f:
    json.dump(prefix_details, f, indent=4)


upstreams = get_json_with_retry(f"{base_url}/upstreams")
if upstreams:
    with open("asn_upstreams.json", "w") as f:
        json.dump(upstreams, f, indent=4)
else:
    print(f"⚠️ Failed to collect upstreams after retries.")
    upstreams = {}


downstreams = get_json_with_retry(f"{base_url}/downstreams")
if downstreams:
    with open("asn_downstreams.json", "w") as f:
        json.dump(downstreams, f, indent=4)
else:
    print(f"⚠️ Failed to collect downstreams after retries.")
    downstreams = {}

print("✅ Upstreams and Downstreams collected.")


# Traceroute sampled prefixes
def run_traceroute(ip):
    system = platform.system()
    cmd = []
    if system == "Windows":
        cmd = ["tracert", "-d", ip]
    else:
        cmd = ["traceroute", "-n", ip]
    try:
        result = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True, timeout=30
        )
        return result
    except subprocess.CalledProcessError as e:
        return str(e.output)
    except subprocess.TimeoutExpired:
        return "Timeout"

    # traceroute


tested_ips = set()
for p in prefixes[:3]:
    network = ipaddress.ip_network(p["prefix"])
    ip_test = str(list(network.hosts())[0])

    if ip_test not in tested_ips:
        print(f"🔍 Traceroute for {ip_test}")
        trace_result = run_traceroute(ip_test)
        with open(f"traceroute_{ip_test}.txt", "w") as f:
            f.write(trace_result)
        tested_ips.add(ip_test)
        time.sleep(5)

# hijack or multihoming
prefix_hijack_check = {}

for p in prefixes:
    prefix = p["prefix"]
    hijack_url = f"https://api.bgpview.io/prefix/{prefix}"
    r = requests.get(hijack_url)
    if r.status_code == 200:
        prefix_data = r.json()["data"]
        announced_by = prefix_data.get("announced_by_asns", [])
        if len(announced_by) > 1:
            prefix_hijack_check[prefix] = announced_by

with open("prefixos_multiasn.json", "w") as f:
    json.dump(prefix_hijack_check, f, indent=4)

print("✅ Check for multiple ASNs completed.")
print("✅ Exports completed.")
