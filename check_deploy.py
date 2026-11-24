import urllib.request
import json
import time

for _ in range(30):
    try:
        req = urllib.request.Request(
            'https://api.render.com/v1/services/srv-dc25ha68bjmc73a59eg0/deploys/dep-dc2ohqrncjis73dj06bg',
            headers={'Authorization': 'Bearer rnd_pBk6zAeO0z9XEaPlFH84otVQBKEY'}
        )
        res = urllib.request.urlopen(req, timeout=10)
        data = json.loads(res.read().decode('utf-8'))
        status = data.get('status')
        print(f"[{time.strftime('%H:%M:%S')}] Deploy Status: {status}", flush=True)
        if status == 'live':
            print("DEPLOY IS LIVE!", flush=True)
            break
        elif status in ['build_failed', 'canceled', 'deactivated']:
            print("Deploy ended with status:", status, flush=True)
            break
    except Exception as e:
        print("Polling error:", e, flush=True)
    time.sleep(10)
