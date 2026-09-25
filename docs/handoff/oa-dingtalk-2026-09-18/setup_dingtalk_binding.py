import base64
import json
import re
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:9540"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))
ENV_FILE = "C:/ZYS/Code/dtsf/.claude/worktrees/dingtalk-oa-finance/deploy/.env.dingtalk.local"

MARKET_ENTITY_CODE = "OA_MAIN"
BINDING_CODE = "OA_MAIN"
SECRET_REF = "DTSF_DINGTALK_OA_MAIN_APP_SECRET"


def env_value(name):
    with open(ENV_FILE, encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped.startswith(name + "="):
                return stripped.split("=", 1)[1].strip()
    raise SystemExit("环境变量未找到: " + name)


def send(method, path, token=None, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", token)
    try:
        with OPENER.open(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(raw)
        except ValueError:
            parsed = {"msg": raw[:200]}
        return error.code, parsed


def solve_captcha(image_data_url):
    svg = base64.b64decode(image_data_url.split(",", 1)[1]).decode("utf-8")
    return "".join(re.findall(r"<text[^>]*>([^<]*)</text>", svg))


def login(user, password):
    _, captcha = send("GET", "/api/auth/imageCaptcha")
    data = captcha["data"]
    _, body = send(
        "POST",
        "/api/auth/login",
        payload={
            "userName": user,
            "password": password,
            "captchaId": data["captchaId"],
            "captchaCode": solve_captcha(data["image"]),
        },
    )
    if body.get("code") != "0000":
        raise SystemExit("登录失败: code=" + str(body.get("code")))
    return body["data"]["token"]


def create_market_entity(token):
    payload = {
        "id": 0,
        "code": MARKET_ENTITY_CODE,
        "name": "OA 主体验收主体",
        "shortName": "OA验收主体",
        "entityType": "子公司",
        "parentCode": "ZT-GROUP",
        "taxNo": "",
        "financeOrg": "OA验收主体",
        "businessScope": "",
        "independentAccounting": "是",
        "sortNo": 10,
        "status": "enabled",
    }
    status, body = send("POST", "/api/business/dataPlatform/marketEntity", token, payload)
    print("市场主体: HTTP", status, "code", body.get("code"), "msg", str(body.get("msg"))[:60])


def create_binding(token):
    payload = {
        "bindingCode": BINDING_CODE,
        "marketEntityCode": MARKET_ENTITY_CODE,
        "corpId": env_value("DTSF_DINGTALK_CORP_ID"),
        "appKey": env_value("DTSF_DINGTALK_APP_KEY"),
        "agentId": None,
        "secretRef": SECRET_REF,
    }
    status, body = send("POST", "/api/oa/dingtalk-directory/bindings", token, payload)
    print("企业绑定: HTTP", status, "code", body.get("code"), "msg", str(body.get("msg"))[:60])
    data = body.get("data") or {}
    print("  绑定编码存在:", bool(data.get("bindingCode")), "状态:", data.get("status"))


def list_bindings(token):
    status, body = send("GET", "/api/oa/dingtalk-directory/bindings", token)
    rows = body.get("data") or []
    print("绑定列表: HTTP", status, "条数", len(rows))
    for row in rows:
        print(
            "  编码", row.get("bindingCode"),
            "状态", row.get("status"),
            "通讯录开关", row.get("directorySyncEnabled"),
            "密钥已注入", row.get("secretConfigured"),
            "推送已连接", row.get("streamConnected"),
        )


if __name__ == "__main__":
    token = login("admin_mgr", "123456")
    create_market_entity(token)
    create_binding(token)
    list_bindings(token)
