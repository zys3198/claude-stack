import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:9540"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
BINDING = "OA_MAIN"


def load_token(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["data"]["token"]


def call(method, path, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", token)
    try:
        with OPENER.open(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = {"msg": raw[:300]}
        return error.code, parsed


def connection_test(token):
    status, body = call(
        "POST", "/api/oa/dingtalk-directory/bindings/" + BINDING + "/connection-test", token
    )
    data = body.get("data") or {}
    print(
        "连接测试: HTTP", status, "code", body.get("code"),
        "ok=", data.get("ok"),
        "换取令牌=", data.get("tokenAcquired"),
        "读取通讯录=", data.get("directoryReadable"),
        "密钥已注入=", data.get("secretConfigured"),
    )
    print("  应用侧消息:", str(data.get("message"))[:80])


def full_sync(token):
    status, body = call(
        "POST", "/api/oa/dingtalk-directory/bindings/" + BINDING + "/full-sync", token
    )
    print("全量同步: HTTP", status, "code", body.get("code"), "msg", str(body.get("msg"))[:80])
    data = body.get("data") or {}
    departments = data.get("departments") or {}
    persons = data.get("persons") or {}
    print(
        "  批次状态:", data.get("status"),
        "部门总数:", departments.get("totalCount"),
        "部门新增:", departments.get("createdCount"),
        "部门更新:", departments.get("updatedCount"),
        "人员总数:", persons.get("totalCount"),
        "人员新增:", persons.get("createdCount"),
        "待激活:", persons.get("pendingActivationCount"),
        "冲突:", persons.get("conflictCount"),
    )


if __name__ == "__main__":
    token = load_token(sys.argv[1])
    step = sys.argv[2] if len(sys.argv) > 2 else "all"
    if step in ("all", "test"):
        connection_test(token)
    if step in ("all", "sync"):
        full_sync(token)
