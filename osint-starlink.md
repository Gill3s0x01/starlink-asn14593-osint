
# 📄 Análise técnica — Starlink ASN 14593 (versão ampliada)

## 📌 Sumário Executivo

Este relatório apresenta uma análise técnico-operacional aprofundada sobre a infraestrutura de rede da **Starlink**, com foco no ASN **14593**, responsável pela distribuição de blocos de endereços IP utilizados na rede de satélites da **SpaceX**. A pesquisa integra técnicas de OSINT, análise forense de rede, consulta a bases BGP públicas e exploração documental, visando apoiar equipes de segurança ofensiva, defensiva, resposta a incidentes e operações de Threat Intelligence.

## 📊 Contexto e Motivação

O uso de conexões via satélite tem crescido exponencialmente tanto para aplicações legítimas quanto para operações cibercriminosas, graças à capacidade de **anonimização geográfica, mobilidade global** e relativa resiliência a bloqueios físicos regionais. A **Starlink**, principal operadora de satélites de baixa órbita (LEO), apresenta desafios adicionais para investigações digitais pela utilização intensiva de **CGNAT (Carrier Grade NAT)** e a atribuição dinâmica de IPs públicos.

## 📡 Arquitetura e Infraestrutura Starlink

### 📍 Topologia de Rede

De acordo com a patente **US11040786B2** e documentação pública:

1. **Usuário:** Terminal de usuário (dish) → conecta via link LEO
2. **Satélite (LEO):** Encaminha o tráfego para o gateway terrestre ou para outro satélite via link laser
3. **Gateway Terrestre:** Antena terrestre conecta via fibra ao backbone regional
4. **Backbone Internet:** Roteamento via ASN **14593** para peers upstream (Nível 1 ou Nível 2)

**CGNAT** ocorre entre a rede Starlink e a internet pública, dificultando a atribuição individual de IPs para terminais residenciais.

### 📍 ASN e Segmentação

- **ASN:** 14593 (Space Exploration Technologies Corp.)
- **Segmentação:**
  - Satélites LEO (Low Earth Orbit)
  - Gateways terrestres
  - Terminais fixos, móveis e empresariais
  - Upstreams e peers Tier 1 (ex.: Telia, GTT, NTT, Level3)

### 📍 Roteamento e Distribuição

- IPs públicos atribuídos dinamicamente via DHCP CGNAT
- IPs fixos e estáticos para planos empresariais premium e aplicações governamentais (militares ou aviação)
- Tabela BGP exposta com rotas ativas e propagadas em [bgp.he.net](https://bgp.he.net/AS14593)

## 📈 Cenário BGP e Prefixos

### 📍 Prefixos e IP Ranges atuais (junho/2025)

Consulta pública:

- [bgp.he.net/AS14593](https://bgp.he.net/AS14593)
- [https://bgpview.io/asn/14593](https://bgpview.io/asn/14593)

**Exemplos de blocos ativos:**

```
142.135.0.0/16
100.64.0.0/10 (CGNAT RFC6598)
2602:810::/36 (IPv6)
```

### 📍 ASN Adjacent / Peers

- **Peers Tier 1:** Telia, GTT, Level3
- **IXPs:** PCH, Equinix IX
- ASN vizinhos: AS1299 (Telia), AS3257 (GTT), AS3356 (Lumen/Level3)

## 🕵️‍♂️ Playbook Operacional — Investigação de Incidentes envolvendo Starlink

### 📌 Fases

**Fase 1 — Identificação ASN:** Whois, BGPView, bgp.he.net  
**Fase 2 — Coleta Prefixos e IPs:** BGPView API, ipinfo.io, db-ip.com  
**Fase 3 — Validação:** ping, traceroute, MTR, Looking Glass  
**Fase 4 — Correlação de Indicadores:** CGNAT, padrões, clusterização de horários  
**Fase 5 — Reporte e Integração:** Relatório, SIEM/TIP, dashboards OSINT  

### 📌 Ferramentas e Comandos

```bash
whois -h whois.radb.net -- '-i origin AS14593' | grep 'route:'
curl ipinfo.io/142.135.0.1
mtr 142.135.0.1
```

## 📊 Integração Python — Dashboard OSINT

Exemplo de coleta de prefixos, agrupamento por país e geração de gráficos em Python com Matplotlib e BGPView API. (código incluído no relatório original)

**Extra:** Consulta de ASN adjacentes

```python
asn = "14593"
neighbors_response = requests.get(f"https://api.bgpview.io/asn/{asn}/peers")
neighbors = neighbors_response.json()['data']['ipv4_peers']

for peer in neighbors:
    print(f"{peer['asn']} - {peer['name']}")
```

## 📜 Documentação e Fontes Técnicas

- [Patente US11040786B2](https://patents.google.com/patent/US11040786B2/en)
- [bgp.he.net/AS14593](https://bgp.he.net/AS14593)
- [bgpview.io/asn/14593](https://bgpview.io/asn/14593)
- [FCC Starlink Gateways](https://fcc.report/FCC-ID/2AWHPR201)
- [Starlink Official Specifications](https://www.starlink.com/specifications)
- [RFC 6598 — 100.64.0.0/10 CGNAT Range](https://datatracker.ietf.org/doc/html/rfc6598)

## 📌 Conclusão

Compreender a dinâmica e arquitetura da rede Starlink permite a analistas de segurança operacionalizar investigações mais assertivas e técnicas, especialmente diante de cenários envolvendo tráfego via satélite com anonimização de origem. A integração de técnicas OSINT, BGP forense e análise de CGNAT possibilita detecção, correlação e atribuição mais eficiente em ambientes onde o uso de satcom está presente.
