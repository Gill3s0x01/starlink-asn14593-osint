import requests
import matplotlib.pyplot as plt
from collections import Counter
import json
import csv

asn = "14593"
response = requests.get(f"https://api.bgpview.io/asn/{asn}/prefixes")
data = response.json()

prefixes = data["data"]["ipv4_prefixes"]

countries = []
prefix_details = []

for p in prefixes:
    country_code = p["country_code"] if p["country_code"] else "Desconhecido"
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
        grouped_counts["Outros"] = grouped_counts.get("Outros", 0) + count


plt.figure(figsize=(10, 6))
colors = [
    "#008000" if country == "BR" else "steelblue" for country in grouped_counts.keys()
]

plt.bar(grouped_counts.keys(), grouped_counts.values(), color=colors)
plt.title("Distribuição de Prefixos Starlink por País")
plt.xlabel("País")
plt.ylabel("Quantidade de Prefixos")
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
plt.title("Distribuição (%) de Prefixos Starlink por País")
plt.tight_layout()
plt.show()


with open("prefixos_starlink_detalhado.csv", "w", newline="") as csvfile:
    fieldnames = ["prefix", "country_code", "is_brazil"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in prefix_details:
        writer.writerow(item)


with open("prefixos_por_pais.csv", "w") as f:
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

with open("prefixos_por_pais.json", "w") as f:
    json.dump(json_data, f, indent=4)


with open("prefixos_starlink_detalhado.json", "w") as f:
    json.dump(prefix_details, f, indent=4)

print("✅ Exports completos.")
