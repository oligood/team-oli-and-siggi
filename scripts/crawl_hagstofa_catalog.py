import os
import json
import requests

BASE_URL = "https://px.hagstofa.is/pxis/api/v1/is"
OUTPUT_FILE = "data/hagstofa_catalog.json"


def fetch_nodes(subpath: str = ""):
    url = f"{BASE_URL}/{subpath}" if subpath else BASE_URL
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return []


def crawl_catalog(max_tables: int = 150):
    os.makedirs("data", exist_ok=True)
    catalog = []
    queue = [""]
    
    print("Crawling Statistics Iceland PX-Web API categories...")
    while queue and len(catalog) < max_tables:
        current = queue.pop(0)
        items = fetch_nodes(current)
        for it in items:
            node_id = it.get("id") or it.get("dbid") or ""
            node_path = f"{current}/{node_id}" if current else node_id
            node_type = it.get("type", "l" if "dbid" in it else "")

            if node_type == "t":
                table_code = node_id.replace(".px", "")
                table_title = it.get("text", "")
                table_url = f"{BASE_URL}/{node_path}"
                catalog.append({
                    "id": table_code,
                    "title": table_title,
                    "url": table_url,
                    "category": current.split("/")[0] if current else "General"
                })
                print(f"[{len(catalog)}] {table_code}: {table_title[:60]}")
                if len(catalog) >= max_tables:
                    break
            elif node_type == "l":
                queue.append(node_path)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(catalog)} tables to '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    crawl_catalog(max_tables=100)
