# app/whois.py
import whois

def resolve_whois(domain):
    try:
        w = whois.whois(domain)
        return {
            "registrar": w.registrar,
            "creation_date": str(w.creation_date),
            "expiration_date": str(w.expiration_date),
            "name_servers": w.name_servers,
            "status": w.status,
            "emails": w.emails,
            "country": w.country,
            "whois_server": w.whois_server,
            "updated_date": str(w.updated_date),
            "domain_name": w.domain_name,
        }
    except Exception as e:
        return {"error": str(e)}
