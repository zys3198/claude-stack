import base64
import json
import re
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:9540"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _send(req):
    try:
        with OPENER.open(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        print("HTTP " + str(error.code) + " body=" + error.read().decode("utf-8", "replace"))
        raise
    except urllib.error.URLError as error:
        print("URLError " + str(error.reason))
        raise


def post(path, payload, token=None):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", token)
    return _send(req)


def get(path, token=None):
    req = urllib.request.Request(BASE + path, method="GET")
    if token:
        req.add_header("Authorization", token)
    return _send(req)


def solve_captcha(captcha_id, image_data_url):
    svg = base64.b64decode(image_data_url.split(",", 1)[1]).decode("utf-8")
    return "".join(re.findall(r"<text[^>]*>([^<]*)</text>", svg))


def login(user_name, password):
    captcha = get("/api/auth/imageCaptcha")["data"]
    code = solve_captcha(captcha["captchaId"], captcha["image"])
    body = post(
        "/api/auth/login",
        {
            "userName": user_name,
            "password": password,
            "captchaId": captcha["captchaId"],
            "captchaCode": code,
        },
    )
    return body


if __name__ == "__main__":
    user = sys.argv[1]
    pwd = sys.argv[2]
    out_path = sys.argv[3]
    result = login(user, pwd)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False)
    data = result.get("data") or {}
    print("code=" + str(result.get("code")))
    print("userName=" + str(data.get("userName")))
    print("roleCode=" + str(data.get("roleCode")))
    print("tokenKeys=" + ",".join(sorted(k for k in data if "oken" in k)))
