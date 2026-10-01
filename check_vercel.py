import urllib.request
import re

html = urllib.request.urlopen('https://nasa-firms-deployment.vercel.app').read().decode('utf-8')
js_match = re.search(r'src="(/assets/index-[^"]+\.js)"', html)
if js_match:
    js_url = 'https://nasa-firms-deployment.vercel.app' + js_match.group(1)
    print("JS URL:", js_url)
    js = urllib.request.urlopen(js_url).read().decode('utf-8')
    urls = set(re.findall(r'(https?://[^\s\"\'\>\;\`]+)', js))
    print("Found URLs:")
    for url in urls:
        if 'render' in url or 'localhost' in url:
            print(url)
else:
    print("JS bundle not found")
