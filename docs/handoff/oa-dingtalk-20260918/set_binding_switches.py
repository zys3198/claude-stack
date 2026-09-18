import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:9540"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
BINDING = "OA_MAIN"
SWITCH_KEYS = ("loginEnabled", "directorySyncEnabled", "attendanceEnabled", "messageEnabled")


def load_token(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["data"]["token"]


def call(method, path, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", token)
    try:
        with OPENER.open(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = {"msg": raw[:300]}
        return error.code, parsed


def current_binding(token):
    _, body = call("GET", "/api/oa/dingtalk-directory/bindings", token)
    for row in body.get("data") or []:
        if row.get("bindingCode") == BINDING:
            return row
    raise SystemExit("未找到绑定 " + BINDING)


def report(row):
    print(
        "免登 =", row.get("loginEnabled"),
        "| 通讯录 =", row.get("directorySyncEnabled"),
        "| 消息 =", row.get("messageEnabled"),
        "| 考勤 =", row.get("attendanceEnabled"),
        "| 推送已连接 =", row.get("streamConnected"),
    )


def main():
    token = load_token(sys.argv[1])
    overrides = dict(pair.split("=", 1) for pair in sys.argv[2:])
    for key in overrides:
        if key not in SWITCH_KEYS:
            raise SystemExit("未知开关: " + key)
    before = current_binding(token)
    print("改动前:")
    report(before)
    payload = {
        "appKey": before.get("appKey"),
        "agentId": before.get("agentId"),
        "secretRef": before.get("secretRef"),
        "loginEnabled": before.get("loginEnabled"),
        "directorySyncEnabled": before.get("directorySyncEnabled"),
        "attendanceEnabled": before.get("attendanceEnabled"),
        "messageEnabled": before.get("messageEnabled"),
        "status": before.get("status"),
        "expectedUpdatedAt": before.get("updatedAt"),
    }
    for key, value in overrides.items():
        payload[key] = value.lower() == "true"
    status, body = call("PUT", "/api/oa/dingtalk-directory/bindings/" + BINDING, token, payload)
    print("保存开关: HTTP", status, "code", body.get("code"), "msg", str(body.get("msg"))[:60])
    print("改动后:")
    report(current_binding(token))


if __name__ == "__main__":
    main()
