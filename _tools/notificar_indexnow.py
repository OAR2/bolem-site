"""Notify IndexNow of published sitemap pages changed since the last accepted batch."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = 'https://api.indexnow.org/indexnow'


def inventory():
    host = (ROOT/'CNAME').read_text().strip()
    pages = {}
    for loc in ET.parse(ROOT/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
        url = loc.text
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc != host:
            raise ValueError('Sitemap URL outside configured HTTPS host')
        route = parsed.path.lstrip('/')
        path = ROOT/(route+'index.html' if not route or route.endswith('/') else route+'.html')
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError('Invalid sitemap path')
        pages[url] = hashlib.sha256(path.read_bytes()).hexdigest()
    return host, pages


def changed_urls(current, previous):
    return sorted(url for url in current.keys() | previous.keys() if current.get(url) != previous.get(url))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True, help='Last successful inventory, outside the public website')
    parser.add_argument('--submit', action='store_true', help='Send notifications; otherwise preview only')
    args = parser.parse_args()
    host, pages = inventory()
    previous = json.loads(args.state.read_text()) if args.state.exists() else {}
    urls = changed_urls(pages, previous)
    if any(urlsplit(url).netloc != host for url in urls):
        raise ValueError('Previous state includes another host')
    print(f'{len(urls)} new, changed or removed URLs; {len(pages)} current public pages.')
    if not args.submit:
        print('\n'.join(urls))
        return
    if urls:
        key = (ROOT/'indexnow-key.txt').read_text().strip()
        if not re.fullmatch(r'[a-zA-Z0-9-]{8,128}', key):
            raise ValueError('Invalid IndexNow key')
        key_url = f'https://{host}/indexnow-key.txt'
        with urllib.request.urlopen(key_url, timeout=30) as response:
            if response.read().decode().strip() != key:
                raise ValueError('Published key differs; wait for deployment')
        for start in range(0, len(urls), 10000):
            payload = {'host': host, 'key': key, 'keyLocation': key_url, 'urlList': urls[start:start+10000]}
            request = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(), headers={'Content-Type':'application/json; charset=utf-8'}, method='POST')
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status not in (200,202):
                    raise RuntimeError(f'Unexpected status {response.status}')
                print(f'IndexNow HTTP {response.status}: URLs received'+('; key verification pending' if response.status==202 else '')+'. This is not confirmation of indexing.')
    args.state.parent.mkdir(parents=True, exist_ok=True)
    args.state.write_text(json.dumps(pages, indent=2)+'\n')


if __name__ == '__main__':
    main()
