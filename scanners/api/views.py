from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..scanners.dorks import main

from scanners.scanners.dns import DNSResolver
from scanners.scanners.whois_scan import resolve_whois
from scanners.scanners.nmap_scan import run_nmap_scan
import json
from pathlib import Path

@api_view(['GET'])
def busqueda_dork(request):
    try:
        query = request.GET.get('q', '') #obtengo parametro url
        resultados = main(query)         #llamo funcion main y le paso el query
        return Response({"Resultados": resultados})
    except Exception as e:
        return Response({"error":str(e)}, status=400)


@api_view(['GET'])
def escaneo_dns(request):
    try:
        domain = request.GET.get("domain")
        if not domain:
            return Response({"error": "Parámetro 'domain' es requerido"}, status=400)

        dns = DNSResolver(domain)
        dns_records = dns.resolve_all()
        whois_info = resolve_whois(domain)
        nmap_results = []

        if dns_records.get("A"):
            for ip in dns_records["A"]:
                nmap_results.extend(run_nmap_scan(ip))
        else:
            for ip in dns.resolve_ns_ips():
                nmap_results.extend(run_nmap_scan(ip))

        report = {
            "domain": domain,
            "records": dns_records,
            "whois": whois_info,
            "nmap": nmap_results
        }

        Path("reportes_dns").mkdir(exist_ok=True)
        with open(f"reportes_dns/{domain}_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        return Response(report)

    except Exception as e:
        return Response({"error": str(e)}, status=500)