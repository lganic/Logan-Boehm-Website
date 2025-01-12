import os
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

BASE_URL = "https://logan-boehm.com/"

def create_sitemap(directory, output_file="sitemap.xml"):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):  # Only include HTML files
                file_path = os.path.relpath(os.path.join(root, file), directory)
                url = urljoin(BASE_URL, file_path.replace("\\", "/"))
                url_element = ET.SubElement(urlset, "url")
                loc_element = ET.SubElement(url_element, "loc")
                loc_element.text = url

    tree = ET.ElementTree(urlset)
    tree.write(os.path.join(directory, output_file), encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    create_sitemap(".")  # Adjust to your website's build/output directory
