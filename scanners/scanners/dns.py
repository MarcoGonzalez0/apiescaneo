# app/dns.py
import dns.resolver
from datetime import datetime

class DNSResolver:
    def __init__(self, domain, record_types=None):
        self.domain = domain
        self.record_types = record_types or ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"]
        self.resolver = dns.resolver.Resolver()
        self.records = {}

    def resolve_all(self):
        for record_type in self.record_types:
            try:
                answers = self.resolver.resolve(self.domain, record_type)
                self.records[record_type] = [str(data) for data in answers]
            except Exception:
                self.records[record_type] = []
        return self.records

    def resolve_ns_ips(self):
        ips = self.records.get("A", [])
        ns_records = self.records.get("NS", [])
        for ns in ns_records:
            try:
                ns_ip = self.resolver.resolve(ns.rstrip('.'), 'A')
                ips.extend([str(ip) for ip in ns_ip])
            except:
                continue
        return list(set(ips))
