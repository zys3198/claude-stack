import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:9540"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def load_token(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["data"]["token"]


def get(path, token):
    req = urllib.request.Request(BASE + path, method="GET")
    req.add_header("Authorization", token)
    try:
        with OPENER.open(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, {"msg": error.read().decode("utf-8", "replace")[:200]}


if __name__ == "__main__":
    token = load_token(sys.argv[1])
    status, body = get("/api/oa/dingtalk-directory/bindings", token)
    rows = body.get("data") or []
    print("HTTP", status)
    for row in rows:
        summary = {
            "bindingCode": row.get("bindingCode"),
            "marketEntityCode": row.get("marketEntityCode"),
            "status": row.get("status"),
            "directorySyncEnabled": row.get("directorySyncEnabled"),
            "secretConfigured": row.get("secretConfigured"),
            "streamConnected": row.get("streamConnected"),
            "secretRefLength": len(str(row.get("secretRef") or "")),
            "hasCallbackFields": any(
                "callback" in key.lower() or "Callback" in key for key in row
            ),
        }
        print(json.dumps(summary, ensure_ascii=False))
