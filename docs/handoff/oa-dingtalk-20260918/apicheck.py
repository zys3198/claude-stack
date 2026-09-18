import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:9540"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def load_token(path):
    with open(path, encoding="utf-8") as handle:
        body = json.load(handle)
    return body["data"]["token"]


def call(method, path, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", token)
    try:
        with OPENER.open(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body.get("code"), body
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = {"raw": raw[:200]}
        return error.code, parsed.get("code"), parsed


if __name__ == "__main__":
    token = load_token(sys.argv[1])
    checks = [
        ("GET", "/api/oa/dingtalk-directory/bindings"),
        ("GET", "/api/oa/dingtalk-directory/bindable-market-entities"),
        ("GET", "/api/oa/dingtalk-messages/dnd/bindings"),
        ("GET", "/api/oa/dingtalk-messages/dnd"),
        ("GET", "/api/oa/dingtalk-messages/templates"),
        ("GET", "/api/oa/dingtalk-messages/outbox"),
        ("GET", "/api/oa/dingtalk-attendance/identities"),
    ]
    for method, path in checks:
        status, code, body = call(method, path, token)
        data = body.get("data")
        if isinstance(data, list):
            shape = "list(" + str(len(data)) + ")"
        elif isinstance(data, dict):
            shape = "dict(" + ",".join(sorted(data.keys())[:6]) + ")"
        else:
            shape = type(data).__name__
        print(method + " " + path + " -> http=" + str(status) + " code=" + str(code) + " data=" + shape + " msg=" + str(body.get("msg"))[:160])
