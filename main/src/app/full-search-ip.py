import requests
import json

# Em teste
# Configure suas API Keys
IPWHOIS_KEY = "YOUR_IPWHOIS_KEY"
DBIP_KEY = "YOUR_DBIP_KEY"
IPDATA_KEY = "YOUR_IPDATA_KEY"


def consult_api(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consult_bgpview(ip):
    return consult_api(f"https://api.bgpview.io/ip/{ip}")


def consult_ipinfo(ip):
    return consult_api(f"https://ipinfo.io/{ip}/json")


def consult_ipapi(ip):
    return consult_api(
        f"http://ip-api.com/json/{ip}?fields=status,message,query,as,isp,country,city"
    )


def consult_ripe(ip):
    return consult_api(
        f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}"
    )


def consult_rdap(ip):
    return consult_api(f"https://rdap.registro.br/ip/{ip}")


def consult_ipwhois(ip):
    return consult_api(f"https://ipwhois.app/json/{ip}?apikey={IPWHOIS_KEY}")


def consult_dbip(ip):
    return consult_api(f"https://api.db-ip.com/v2/{DBIP_KEY}/{ip}")


def consult_ipdata(ip):
    return consult_api(f"https://api.ipdata.co/{ip}?api-key={IPDATA_KEY}")


def generate_report(ip, results):
    json_file = f"{ip.replace('.', '_')}_full_report.json"
    txt_file = f"{ip.replace('.', '_')}_full_report.txt"

    with open(json_file, "w") as jf:
        json.dump(results, jf, indent=4)

    with open(txt_file, "w") as tf:
        tf.write(f"📊 Relatório completo de OSINT IP para {ip}\n\n")
        for key, val in results.items():
            tf.write(f"== {key.upper()} ==\n")
            if val is None:
                tf.write("Consulta falhou ou dados indisponíveis.\n\n")
                continue
            for k, v in val.items():
                tf.write(f"{k}: {v}\n")
            tf.write("\n")


def main():
    ip = input("Digite o IP para consulta OSINT completa: ").strip()

    results = {
        "bgpview": consult_bgpview(ip),
        "ipinfo": consult_ipinfo(ip),
        "ip-api": consult_ipapi(ip),
        "ripe": consult_ripe(ip),
        "rdap": consult_rdap(ip),
        "ipwhois": consult_ipwhois(ip),
        "db-ip": consult_dbip(ip),
        "ipdata": consult_ipdata(ip),
    }

    generate_report(ip, results)
    print(
        f"\n✅ Consulta completa! Arquivos salvos: {ip.replace('.', '_')}_full_report.json e .txt"
    )


if __name__ == "__main__":
    main()
