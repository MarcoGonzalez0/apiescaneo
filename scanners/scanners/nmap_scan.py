# app/nmap.py
import subprocess
import xml.etree.ElementTree as ET
import os

def run_nmap_scan(ip):
    result = []
    try:
        xml_output = f"/tmp/nmap_{ip}.xml"
        subprocess.run(["nmap", "-A", "-Pn", "-T4", "-oX", xml_output, ip],
                       check=True, capture_output=True)
        result = parse_nmap(xml_output)
        os.remove(xml_output)
    except subprocess.CalledProcessError as e:
        result = {"error": str(e)}
    return result

def parse_nmap(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    host = root.find("host")

    host_info = {"ip": "", "ports": []}
    address = host.find("address")
    if address is not None:
        host_info["ip"] = address.attrib["addr"]

    ports = host.find("ports")
    if ports is not None:
        for port in ports.findall("port"):
            port_info = {
                "port": port.attrib["portid"],
                "protocol": port.attrib["protocol"],
                "state": port.find("state").attrib["state"],
                "service": {}
            }
            service = port.find("service")
            if service is not None:
                port_info["service"] = {
                    "name": service.attrib.get("name", ""),
                    "product": service.attrib.get("product", ""),
                    "version": service.attrib.get("version", "")
                }
            host_info["ports"].append(port_info)
    return [host_info]
