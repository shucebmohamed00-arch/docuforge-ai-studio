import urllib.request
import json
import time

RENDER_API_KEY = "rnd_pBk6zAeO0z9XEaPlFH84otVQBKEY"
SERVICE_ID = "srv-dc25ha68bjmc73a59eg0"

print("Triggering new Render cloud deployment with cleared cache...")
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SERVICE_ID}/deploys",
    data=json.dumps({"clearCache": "clear"}).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=15) as res:
        data = json.loads(res.read().decode("utf-8"))
        deploy_id = data.get("id")
        print(f"Deploy triggered! ID: {deploy_id}")
except Exception as e:
    print(f"Trigger error: {e}")
    exit(1)

for attempt in range(60):
    time.sleep(8)
    try:
        status_req = urllib.request.Request(
            f"https://api.render.com/v1/services/{SERVICE_ID}/deploys/{deploy_id}",
            headers={"Authorization": f"Bearer {RENDER_API_KEY}"}
        )
        with urllib.request.urlopen(status_req, timeout=10) as sres:
            sdata = json.loads(sres.read().decode("utf-8"))
            status = sdata.get("status")
            print(f"[{time.strftime('%H:%M:%S')}] Deploy Status: {status}", flush=True)
            if status == "live":
                print(">>> RENDER DEPLOYMENT IS LIVE! <<<", flush=True)
                break
            elif status in ["build_failed", "canceled", "deactivated"]:
                print(f"Deploy failed with status: {status}", flush=True)
                break
    except Exception as e:
        print(f"Polling error: {e}", flush=True)
