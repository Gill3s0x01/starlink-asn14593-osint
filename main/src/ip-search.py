import requests
import json


def consulta_bgpview(ip):
    url = f"https://api.bgpview.io/ip/{ip}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consulta_ipinfo(ip):
    url = f"https://ipinfo.io/{ip}/json"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consulta_ipapi(ip):
    url = f"http://ip-api.com/json/{ip}?fields=status,message,query,as,isp,country,city"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def consulta_ripe(ip):
    # Vamos usar prefix-overview endpoint do RIPEstat, que retorna info do prefixo e ASN
    url = f"https://stat.ripe.net/data/prefix-overview/data.json?resource={ip}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def extrair_dados(dados_bgpview, dados_ipinfo, dados_ipapi, dados_ripe):
    resultado = {}

    # bgpview
    if dados_bgpview and dados_bgpview.get("status") == "ok":
        asn_data = dados_bgpview["data"].get("asn")
        if asn_data:
            asn = asn_data.get("asn")
            org = asn_data.get("name")
            country = asn_data.get("country_code")
        else:  
            asn = org = country
        prefixes = dados_bgpview["data"].get("prefixes", [])
        prefix = 
            prefixes[0].get("prefix") if prefixes else None
            resultado["bgpview"] = {
                "asn": asn,
                "org": org,
                "country": country,
                "prefix": prefix
            }
            if prefixes else None
        
        resultado["bgpview"] = {
            "asn": asn,
            "org": org,
            "country": country,
            "prefix": prefix,
        }
    else:
        resultado["bgpview"] = None

    # ipinfo
    if dados_ipinfo and "error" not in dados_ipinfo:
        asn_info = dados_ipinfo.get("org", "")
        asn = None
        org = None
        if asn_info:
            parts = asn_info.split(" ", 1)
            if len(parts) == 2:
                asn = parts[0].replace("AS", "")
                org = parts[1]
            else:
                org = asn_info
        country = dados_ipinfo.get("country")
        resultado["ipinfo"] = {"asn": asn, "org": org, "country": country}
    else:
        resultado["ipinfo"] = None

    # ip-api
    if dados_ipapi and dados_ipapi.get("status") == "success":
        asn_info = dados_ipapi.get("as", "")
        asn = None
        org = None
        if asn_info:
            parts = asn_info.split(" ", 1)
            if len(parts) == 2:
                asn = parts[0].replace("AS", "")
                org = parts[1]
            else:
                org = asn_info
        country = dados_ipapi.get("country")
        resultado["ipapi"] = {"asn": asn, "org": org, "country": country}
    else:
        resultado["ipapi"] = None

    # ripe
    if dados_ripe and dados_ripe.get("status") == "ok":
        data = dados_ripe.get("data", {})
        asn = None
        prefix = None
        if data:
            prefixes = data.get("prefixes", [])
            if prefixes:
                prefix = prefixes[0].get("prefix")
                asn = prefixes[0].get("asns")[0] if prefixes[0].get("asns") else None
        resultado["ripe"] = {"asn": asn, "prefix": prefix}
    else:
        resultado["ripe"] = None

    return resultado


def gerar_relatorio(ip, dados_compilados):
    json_file = f"{ip.replace('.', '_')}_asn_compilado.json"
    txt_file = f"{ip.replace('.', '_')}_asn_compilado.txt"

    # Salvar JSON
    with open(json_file, "w") as jf:
        json.dump(dados_compilados, jf, indent=4)

    # Salvar TXT legível
    with open(txt_file, "w") as tf:
        tf.write(f"Relatório compilado ASN para IP: {ip}\n\n")

        for key, val in dados_compilados.items():
            tf.write(f"== Fonte: {key.upper()} ==\n")
            if val is None:
                tf.write("Falha na consulta ou dados não disponíveis.\n\n")
                continue
            for k, v in val.items():
                tf.write(f"{k}: {v}\n")
            tf.write("\n")

        # Checar diferenças básicas
        tf.write("== Análise de diferenças entre fontes ==\n")

        asns = set()
        orgs = set()
        countries = set()

        for val in dados_compilados.values():
            if val:
                asns.add(str(val.get("asn")))
                orgs.add(str(val.get("org")))
                countries.add(str(val.get("country")))

        tf.write(f"ASN encontrados: {', '.join(asns)}\n")
        tf.write(f"Organizações encontradas: {', '.join(orgs)}\n")
        tf.write(f"Países encontrados: {', '.join(countries)}\n")

        if len(asns) > 1:
            tf.write("ATENÇÃO: ASN divergentes encontrados entre as fontes.\n")
        if len(orgs) > 1:
            tf.write("ATENÇÃO: Organizações divergentes encontradas entre as fontes.\n")
        if len(countries) > 1:
            tf.write("ATENÇÃO: Países divergentes encontrados entre as fontes.\n")


def main():
    ip = input("Digite o IP para consulta compilada ASN: ").strip()
    dados_bgpview = consulta_bgpview(ip)
    dados_ipinfo = consulta_ipinfo(ip)
    dados_ipapi = consulta_ipapi(ip)
    dados_ripe = consulta_ripe(ip)

    dados_compilados = extrair_dados(
        dados_bgpview, dados_ipinfo, dados_ipapi, dados_ripe
    )
    gerar_relatorio(ip, dados_compilados)
    print(
        f"Consulta concluída! Arquivos salvos: {ip.replace('.', '_')}_asn_compilado.json e .txt"
    )


if __name__ == "__main__":
    main()
