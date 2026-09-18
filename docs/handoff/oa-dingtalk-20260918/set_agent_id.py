import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:9540"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
BINDING = "OA_MAIN"
AGENT_ID = "4884158168"


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


def main():
    token = load_token(sys.argv[1])
    before = current_binding(token)
    payload = {
        "appKey": before.get("appKey"),
        "agentId": AGENT_ID,
        "secretRef": before.get("secretRef"),
        "loginEnabled": before.get("loginEnabled"),
        "directorySyncEnabled": before.get("directorySyncEnabled"),
        "attendanceEnabled": before.get("attendanceEnabled"),
        "messageEnabled": before.get("messageEnabled"),
        "status": before.get("status"),
        "expectedUpdatedAt": before.get("updatedAt"),
    }
    status, body = call("PUT", "/api/oa/dingtalk-directory/bindings/" + BINDING, token, payload)
    print("写入 AgentId: HTTP", status, "code", body.get("code"), "msg", str(body.get("msg"))[:60])
    after = current_binding(token)
    print(
        "核对: AgentId写入成功 =", str(after.get("agentId")) == AGENT_ID,
        "| 密钥已注入 =", after.get("secretConfigured"),
        "| 推送已连接 =", after.get("streamConnected"),
        "| 免登开关 =", after.get("loginEnabled"),
        "| 通讯录开关 =", after.get("directorySyncEnabled"),
        "| 消息开关 =", after.get("messageEnabled"),
        "| 考勤开关 =", after.get("attendanceEnabled"),
    )


if __name__ == "__main__":
    main()
