import urllib.request
import re

try:
    req = urllib.request.Request('https://nasa-firms-deployment.vercel.app', headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    js_match = re.search(r'src="(/assets/index-[^"]+\.js)"', html)
    if js_match:
        js_url = 'https://nasa-firms-deployment.vercel.app' + js_match.group(1)
        print("JS URL:", js_url)
        js_req = urllib.request.Request(js_url, headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
        js = urllib.request.urlopen(js_req).read().decode('utf-8')
        if 'URLSearchParams' in js:
            print("URLSearchParams is in the live JS bundle! Update successful.")
        else:
            print("URLSearchParams NOT FOUND in JS. Vercel hasn't deployed or served the new version yet.")
except Exception as e:
    print("Error:", e)
