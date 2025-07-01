import requests
import json


def consult_bgpview(ip):
    url = f"https://api.bgpview.io/ip/{ip}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consult_ipinfo(ip):
    url = f"https://ipinfo.io/{ip}/json"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consult_ipapi(ip):
    url = f"http://ip-api.com/json/{ip}?fields=status,message,query,as,isp,country,city"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consult_ripe(ip):
    url = f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consult_rdap(ip):
    urls = [
        f"https://rdap.registro.br/ip/{ip}",
        f"https://rdap.arin.net/registry/ip/{ip}",
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json()
        except:
            pass
    return None


def extract_data(data_bgpview, data_ipinfo, data_ipapi, data_ripe, data_rdap):
    results = {}

    # bgpview
    if data_bgpview and data_bgpview.get("status") == "ok":
        asn_data = data_bgpview["data"].get("asn")
        if asn_data:
            asn = asn_data.get("asn")
            org = asn_data.get("name")
            country = asn_data.get("country_code")
        else:
            asn = org = country = "Not found"
        prefixes = data_bgpview["data"].get("prefixes", [])
        prefix = prefixes[0].get("prefix") if prefixes else "Not found"
        results["bgpview"] = {
            "asn": asn,
            "organization": org,
            "country": country,
            "prefix": prefix,
        }
    else:
        results["bgpview"] = None

    # ipinfo
    if data_ipinfo and "error" not in data_ipinfo:
        asn_info = data_ipinfo.get("org", "")
        asn = None
        org = None
        if asn_info:
            parts = asn_info.split(" ", 1)
            if len(parts) == 2:
                asn = parts[0].replace("AS", "")
                org = parts[1]
            else:
                org = asn_info
        country = data_ipinfo.get("country")
        results["ipinfo"] = {"asn": asn, "organization": org, "country": country}
    else:
        results["ipinfo"] = None

    # ip-api
    if data_ipapi and data_ipapi.get("status") == "success":
        asn_info = data_ipapi.get("as", "")
        asn = None
        org = None
        if asn_info:
            parts = asn_info.split(" ", 1)
            if len(parts) == 2:
                asn = parts[0].replace("AS", "")
                org = parts[1]
            else:
                org = asn_info
        country = data_ipapi.get("country")
        city = data_ipapi.get("city")
        results["ip-api"] = {
            "asn": asn,
            "organization": org,
            "country": country,
            "city": city,
        }
    else:
        results["ip-api"] = None

    # ripe
    if data_ripe and data_ripe.get("status") == "ok":
        data = data_ripe.get("data", {})
        asn = None
        prefix = None
        if data:
            prefixes = data.get("prefixes", [])
            if prefixes:
                prefix = prefixes[0].get("prefix")
                asn = prefixes[0].get("asns")[0] if prefixes[0].get("asns") else None
        results["ripe"] = {"asn": asn, "prefix": prefix}
    else:
        results["ripe"] = None

    # rdap
    if data_rdap:
        entities = data_rdap.get("entities", [])
        abuse_email = ""
        name = ""
        for ent in entities:
            roles = ent.get("roles", [])
            if "abuse" in roles:
                abuse_email = ent.get("vcardArray", [])[1][2][3]
            if "registrant" in roles:
                name = ent.get("vcardArray", [])[1][1][3]
        results["rdap"] = {
            "handle": data_rdap.get("handle"),
            "name": name,
            "abuse_email": abuse_email,
            "country": data_rdap.get("country"),
            "ip_version": data_rdap.get("ipVersion"),
            "start_address": data_rdap.get("startAddress"),
            "end_address": data_rdap.get("endAddress"),
            "type": data_rdap.get("type"),
        }
    else:
        results["rdap"] = None

    return results


def generate_report(ip, data_compiled):
    json_file = f"{ip.replace('.', '_')}_asn_report.json"
    txt_file = f"{ip.replace('.', '_')}_asn_report.txt"

    with open(json_file, "w", encoding="utf-8") as jf:
        json.dump(data_compiled, jf, indent=4)

    with open(txt_file, "w", encoding="utf-8") as tf:
        tf.write(f"📄 Full IP OSINT Report for: {ip}\n\n")
        for key, val in data_compiled.items():
            tf.write(f"== {key.upper()} ==\n")
            if val is None:
                tf.write("Query failed or no data available.\n\n")
                continue
            for k, v in val.items():
                tf.write(f"{k}: {v}\n")
            tf.write("\n")


def main():
    ip = input("Enter the IP address for full OSINT query: ").strip()
    data_bgpview = consult_bgpview(ip)
    data_ipinfo = consult_ipinfo(ip)
    data_ipapi = consult_ipapi(ip)
    data_ripe = consult_ripe(ip)
    data_rdap = consult_rdap(ip)

    data_compiled = extract_data(
        data_bgpview, data_ipinfo, data_ipapi, data_ripe, data_rdap
    )
    generate_report(ip, data_compiled)
    print(
        f"\n✅ Query completed! Files saved as: {ip.replace('.', '_')}_asn_report.json and .txt"
    )


if __name__ == "__main__":
    main()
