import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('FREESOUND_API_KEY')

url = f"https://freesound.org/apiv2/search/text/?query=cinematic+sad+strings&filter=duration:[45+TO+180]&fields=id,name,duration,previews&token={token}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Total matching sad strings: {data.get('count', 0)}")
        for res in data.get('results', [])[:6]:
            print(f"ID: {res['id']} | Name: {res['name']} | Dur: {res['duration']:.1f}s")
            print(f"Preview URL: {res.get('previews', {}).get('preview-hq-mp3')}")
except Exception as e:
    print("Error:", e)
