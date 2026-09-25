import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GUARD = Path(os.path.expanduser("~")) / ".claude" / "hooks" / "scripts" / "resource-guard.py"
PY = sys.executable
FAILED = []

spec = importlib.util.spec_from_file_location("resource_guard", GUARD)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

_HOST_TOOLCHAIN = g.host_toolchain


def host_toolchain(command):
    return _HOST_TOOLCHAIN(command, str(Path(tempfile.gettempdir()) / "resource-guard-test"))


def check(label, got, want):
    ok = got == want
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILED.append(label)
        print(f"      实得 {got!r}")
        print(f"      期望 {want!r}")


def run(payload):
    r = subprocess.run(
        [PY, str(GUARD)],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    return r.stdout.decode("utf-8", "replace").strip(), r.returncode


def decision(out):
    if not out:
        return None
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"]


def reason(out):
    return json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]


# 独占清单、容器运行状态与活跃会话数都依赖本机实况。判据二若照实机跑，断言只能写成
# 「要么放行要么提问」，两种结果都接受，等于不测。这里在子进程里把它们替换掉。
PATCH = (
    "g.read_exclusive = lambda: [{'container': 'deploy-nginx-1', 'service': 'nginx',"
    " 'project': 'deploy', 'label': 'x'}]\n"
    "g.running_containers = lambda: {'deploy-nginx-1'}\n"
    "g.other_session_count = lambda sid: (2, False)\n"
)
NO_BUSY_PATCH = (
    "g.running_containers = lambda: set()\n"
    "g.other_session_count = lambda sid: (2, False)\n"
)

# docker compose run 起的一次性容器名字带随机后缀，登记时给不出完整名字，只能给前缀。
PREFIX_ENTRY = (
    "{'container': 'deploy-frontend-build-run-*',"
    " 'container_prefix': 'deploy-frontend-build-run-', 'service': 'frontend-build',"
    " 'project': 'deploy', 'label': 'x'}"
)


def prefix_patch(running):
    return (
        f"g.read_exclusive = lambda: [{PREFIX_ENTRY}]\n"
        f"g.running_containers = lambda: {running!r}\n"
        "g.other_session_count = lambda sid: (2, False)\n"
    )


def run_patched(payload, patch=PATCH):
    code = (
        "import importlib.util, json, sys, io\n"
        f"spec = importlib.util.spec_from_file_location('g', {str(GUARD)!r})\n"
        "g = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(g)\n"
        + patch +
        f"sys.stdin = io.StringIO(json.dumps({json.dumps(payload, ensure_ascii=False)}))\n"
        "g.main()\n"
    )
    r = subprocess.run(
        [PY, "-c", code],
        capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    return r.stdout.decode("utf-8", "replace").strip(), r.returncode


# --- 拆词与目标提取 ---
t = g.docker_targets("docker compose -f deploy/docker-compose.local.yml --profile dev up -d frontend-dev", ".")
check("compose up 取服务与服务名", (sorted(t["services"]), t["all_services"], t["compose_dir"]),
      (["frontend-dev"], False, "deploy"))

t = g.docker_targets("docker compose -f deploy/docker-compose.local.yml up -d", ".")
check("compose 不带服务名", (sorted(t["services"]), t["all_services"]), ([], True))

t = g.docker_targets("cd /x && docker compose -p myproj down", "/x")
check("控制符之后的 docker 也算起首", (t["project"], t["all_services"]), ("myproj", True))

check("docker restart 取容器名",
      sorted(g.docker_targets("docker restart deploy-nginx-1", ".")["containers"]), ["deploy-nginx-1"])

check("docker rm -f 取容器名",
      sorted(g.docker_targets("docker rm -f deploy-chroma-1", ".")["containers"]), ["deploy-chroma-1"])

check("docker run 只认 --name，不把镜像名当容器名",
      sorted(g.docker_targets("docker run -p 8080:80 --name probe alpine", ".")["containers"]), ["probe"])

check("docker start 的位置实参都是容器名",
      sorted(g.docker_targets("docker start web db", ".")["containers"]), ["db", "web"])

check("只读子命令不触发", g.docker_targets("docker compose -f deploy/docker-compose.local.yml logs -f", "."), None)
check("docker ps 不触发", g.docker_targets("docker ps -a", "."), None)
check("非起首位置的 docker 不触发",
      g.docker_targets("git commit -m '说明 docker compose down 的用法'", "."), None)
check("引号不闭合时仍取出目标",
      sorted(g.docker_targets("docker compose up -d 'x", ".")["services"]), ["'x"])
check("引号不闭合且奇数引号时仍取出容器名",
      sorted(g.docker_targets('echo \\" && docker restart deploy-nginx-1', ".")["containers"]),
      ["deploy-nginx-1"])
check("sh -c 包装里的 docker 也取得到",
      sorted(g.docker_targets("sh -c 'docker restart deploy-nginx-1'", ".")["containers"]),
      ["deploy-nginx-1"])
check("多行命令第二行的 docker 也取得到",
      sorted(g.docker_targets("cd deploy\ndocker compose up -d backend-java", ".")["services"]),
      ["backend-java"])
check("分号紧贴的 docker 也取得到",
      sorted(g.docker_targets("cd deploy; docker compose up -d backend-java", ".")["services"]),
      ["backend-java"])
check("旧式 docker-compose 也认",
      sorted(g.docker_targets(
          "docker-compose -f deploy/docker-compose.local.yml up -d backend-java", ".")["services"]),
      ["backend-java"])
check("docker container restart 的名词形式也认",
      sorted(g.docker_targets("docker container restart deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("跨子句不吞掉后面的 docker",
      sorted(g.docker_targets(
          "docker compose -f deploy/docker-compose.local.yml ps\n"
          "docker compose -f deploy/docker-compose.local.yml restart backend-java", ".")["services"]),
      ["backend-java"])
check("记下命令里的 cd 目标",
      g.docker_targets("cd deploy && docker compose down", ".")["cd_dir"], "deploy")
check("cd 目标带相对路径",
      g.docker_targets("cd ../deploy && docker compose down", "C:/x/y")["cd_dir"], "deploy")
check("--project-directory 取目录名",
      g.docker_targets("docker compose --project-directory deploy down", ".")["project_dir"], "deploy")
check("--project-directory 带相对路径",
      g.docker_targets("docker compose --project-directory ../deploy down", "C:/x/y")["project_dir"],
      "deploy")

# --- Bash 写 compose 文件的目标提取 ---
def write_targets(command):
    return g.compose_write_targets(g.split_tokens(command))


check("重定向取目标", write_targets("echo x > deploy/docker-compose.local.yml"),
      ["deploy/docker-compose.local.yml"])
check("追加重定向取目标", write_targets("echo x >> deploy/docker-compose.local.yml"),
      ["deploy/docker-compose.local.yml"])
check("tee 取目标", write_targets("echo x | tee deploy/docker-compose.local.yml"),
      ["deploy/docker-compose.local.yml"])
check("sed -i 取目标", write_targets("sed -i 's/3306/3307/' deploy/docker-compose.local.yml"),
      ["s/3306/3307/", "deploy/docker-compose.local.yml"])
check("sed -i 带备份后缀", write_targets("sed -i.bak 's/x/y/' deploy/docker-compose.local.yml"),
      ["s/x/y/", "deploy/docker-compose.local.yml"])
check("sed 不带 -i 视为只读", write_targets("sed 's/x/y/' deploy/docker-compose.local.yml"), [])
check("cp 的目标是最后一个位置实参", write_targets("cp a.yml deploy/docker-compose.local.yml"),
      ["deploy/docker-compose.local.yml"])
check("cp 的来源不算目标", write_targets("cp deploy/docker-compose.local.yml /x/y.yml"), ["/x/y.yml"])
check("输入重定向不算目标", write_targets("cat < deploy/docker-compose.local.yml"), [])
check("写普通文件时目标照取", write_targets("echo x > notes.md"), ["notes.md"])
check("不带重定向的读取不取目标",
      write_targets("cat deploy/docker-compose.local.yml"), [])

# --- 独占清单命中 ---
ENTRIES = [
    {"container": "deploy-backend-java-1", "service": "backend-java", "project": "deploy", "label": "重建后端"},
    {"container": "deploy-nginx-1", "service": "nginx", "project": "deploy", "label": "挂载产物"},
]
t = g.docker_targets("docker compose -f deploy/docker-compose.local.yml up -d backend-java", ".")
check("按服务名命中", [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-backend-java-1"])
t = g.docker_targets("docker compose -f deploy/docker-compose.local.yml --profile scale up -d redis", ".")
check("别的服务不命中", g.hit_entries(t, ENTRIES), [])
t = g.docker_targets("docker compose -f deploy/docker-compose.local.yml up -d", ".")
check("整项目启动按 -f 目录命中",
      [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-backend-java-1", "deploy-nginx-1"])
t = g.docker_targets("docker compose -f other/docker-compose.yml up -d", ".")
check("别的项目目录不命中", g.hit_entries(t, ENTRIES), [])
t = g.docker_targets("docker compose -f deploy/docker-compose.local.yml restart nginx", ".")
check("按服务名命中 nginx", [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-nginx-1"])
t = g.docker_targets("docker restart deploy-nginx-1", ".")
check("直接按容器名命中", [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-nginx-1"])
t = g.docker_targets("docker compose down", "C:/ZYS/Code/dtsf/deploy")
check("不带 -p/-f 时按当前目录名命中",
      [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-backend-java-1", "deploy-nginx-1"])
t = g.docker_targets("cd deploy && docker compose down", "C:/ZYS/Code/dtsf")
check("不带 -p/-f 时按命令里的 cd 目标命中",
      [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-backend-java-1", "deploy-nginx-1"])
t = g.docker_targets("cd deploy\ndocker compose down", "C:/ZYS/Code/dtsf")
check("多行命令里不带 -p/-f 的整项目命令也命中",
      [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-backend-java-1", "deploy-nginx-1"])
t = g.docker_targets("docker compose down", "C:/ZYS/Code/dtsf/.claude/worktrees/dingtalk-oa-finance")
check("当前目录名对不上时不命中", g.hit_entries(t, ENTRIES), [])
t = g.docker_targets("sh -c 'docker restart deploy-nginx-1'", ".")
check("sh -c 包装里的容器名也命中", [e["container"] for e in g.hit_entries(t, ENTRIES)], ["deploy-nginx-1"])

# --- compose 判据端到端 ---
BASE = """services:
  mysql:
    image: mysql:8.4
"""
FULL = """services:
  mysql:
    image: mysql:8.4
  redis:
    image: redis:7.4-alpine
    mem_limit: 384m
    security_opt:
      - "no-new-privileges:true"
"""
GAP = """services:
  mysql:
    image: mysql:8.4
  chroma:
    image: chromadb/chroma
    mem_limit: 512m
  redis:
    image: redis:7.4-alpine
    mem_limit: 384m
"""

with tempfile.TemporaryDirectory() as tmp:
    TMP = Path(tmp)
    probe = TMP / "compose-probe.yml"
    probe.write_text(BASE, encoding="utf-8")

    out, rc = run({"tool_name": "Edit", "cwd": str(TMP), "session_id": "me", "tool_input": {
        "file_path": str(probe), "old_string": BASE, "new_string": FULL}})
    check("新增服务写全了两项则放行", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Edit", "cwd": str(TMP), "session_id": "me", "tool_input": {
        "file_path": str(probe), "old_string": BASE, "new_string": GAP}})
    check("新增服务缺 security_opt 时阻断", decision(out), "deny")
    check("阻断点名缺项", "chroma 缺 security_opt" in reason(out), True)

    out, rc = run({"tool_name": "Edit", "cwd": str(TMP), "session_id": "me", "tool_input": {
        "file_path": str(probe), "old_string": "image: mysql:8.4",
        "new_string": "image: mysql:8.4\n    command: --x"}})
    check("改老服务不重复报历史缺口", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Write", "cwd": str(TMP), "session_id": "me", "tool_input": {
        "file_path": str(TMP / "new-compose.yml"), "content": GAP}})
    check("新建文件全部按新增判定", decision(out), "deny")

    out, rc = run({"tool_name": "Write", "cwd": str(TMP), "session_id": "me", "tool_input": {
        "file_path": str(TMP / "notes.md"), "content": GAP}})
    check("非 compose 文件不看", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Edit", "cwd": str(TMP), "session_id": "me", "tool_input": {
        "file_path": str(probe), "old_string": "不存在的片段", "new_string": "x"}})
    check("重放失败时放行", (decision(out), rc), (None, 0))

# --- Bash 判据端到端 ---
with tempfile.TemporaryDirectory() as tmp:
    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml --profile build run --rm frontend-build"}},
        NO_BUSY_PATCH)
    check("未登记的容器不触发", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "git commit -m 'docker compose down 的说明'"}})
    check("提交消息里的 docker 不触发", (decision(out), rc), (None, 0))

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml up -d"}})
    check("整项目启动独占项目时提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml up -d redis"}})
    check("别的服务不提问", decision(out), None)

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose --project-directory deploy down"}})
    check("--project-directory 对上独占项目时提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose --project-directory elsewhere down"}})
    check("--project-directory 对不上时不提问", decision(out), None)

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker restart deploy-nginx-1"}})
    check("重启独占容器时提问", decision(out), "ask")
    check("提问点名容器", "deploy-nginx-1" in reason(out), True)

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "bash -c 'docker restart deploy-nginx-1'"}})
    check("shell 包装里的重启也提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": '"dock"er restart deploy-nginx-1'}})
    check("引号拆写的 docker 也提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": 'echo \\" && docker restart deploy-nginx-1'}})
    check("引号不闭合时判据二仍提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker-compose -f deploy/docker-compose.local.yml restart nginx"}})
    check("旧式 docker-compose 也提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml run --rm frontend-build"}},
        prefix_patch({"deploy-frontend-build-run-68c0c66bbee6"}))
    check("一次性容器按前缀命中时提问", decision(out), "ask")
    check("提问点名服务", "frontend-build" in reason(out), True)

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml run --rm frontend-build"}},
        prefix_patch({"deploy-chroma-1"}))
    check("一次性容器没在跑时不提问", decision(out), None)

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker restart deploy-nginx-1"}},
        "g.read_exclusive = lambda: [{'container': 'deploy-nginx-1', 'service': 'nginx',"
        " 'project': 'deploy', 'label': 'x'}]\n"
        "g.running_containers = lambda: {'deploy-nginx-1-extra'}\n"
        "g.other_session_count = lambda sid: (2, False)\n")
    check("精确名条目不按前缀命中", decision(out), None)

    # 两条判据同时命中，输出必须还是一个 JSON 对象（两行 JSON 调用方解析不了）
    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml up -d nginx && pnpm build"}})
    check("两条判据同时命中时只输出一行", len(out.splitlines()), 1)
    check("阻断优先于询问", decision(out), "deny")
    check("两条判据的理由都在", ("pnpm" in reason(out), "deploy-nginx-1" in reason(out)), (True, True))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {}})
    check("空命令不崩溃", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose up -d '未闭合"}})
    check("引号不闭合但目标不在独占清单时放行", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "sed -i 's/1024m/512m/' deploy/docker-compose.local.yml"}})
    check("sed -i 改写 compose 文件时阻断", decision(out), "deny")
    check("阻断点名文件", "docker-compose.local.yml" in reason(out), True)

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "printf 'services: {}' > deploy/docker-compose.local.yml"}})
    check("重定向改写 compose 文件时阻断", decision(out), "deny")

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "echo 'services: {}' | tee deploy/docker-compose.local.yml"}})
    check("tee 改写 compose 文件时阻断", decision(out), "deny")

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "cat > deploy/docker-compose.local.yml <<'EOF'\nservices: {}\nEOF"}})
    check("heredoc 改写 compose 文件时阻断", decision(out), "deny")

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "bash -c \"echo x > deploy/docker-compose.local.yml\""}})
    check("shell 包装里的改写也阻断", decision(out), "deny")

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "echo x > notes.md"}})
    check("写普通文件放行", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "cat deploy/docker-compose.local.yml"}})
    check("读 compose 文件放行", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml config"}})
    check("docker 只读子命令不因文件名提问", (decision(out), rc), (None, 0))

# --- 绕过路径（F3 至 F8） ---
# docker 的全局选项排在子命令之前，其中一部分要吃下一个词。不消费取值时它的取值
# 会被当成子命令，整个 docker 段因此被跳过。
check("--context 吃取值",
      sorted(g.docker_targets("docker --context default restart deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("--context= 等号写法",
      sorted(g.docker_targets("docker --context=default restart deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("-H 吃取值",
      sorted(g.docker_targets("docker -H tcp://127.0.0.1:2375 restart deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("--log-level 吃取值",
      sorted(g.docker_targets("docker --log-level debug restart deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("取值不看成子命令",
      g.docker_targets("docker --context default ps -a", "."), None)

# 行末反斜杠把下一行接上来，两行合起来才是同一条命令
check("反斜杠续行接上第二行",
      sorted(g.docker_targets("docker restart \\\n  deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("续行之后的容器名照取",
      sorted(g.docker_targets("docker \\\n  restart \\\n  deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("翻倍的反斜杠不算续行",
      sorted(g.docker_targets("echo a \\\\\ndocker restart deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])

# cmd /c 与不带引号的 powershell -Command 后面跟的是整条命令
check("cmd /c 后面整段都是载荷",
      sorted(g.docker_targets("cmd /c docker restart deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("cmd //c 后面整段都是载荷",
      sorted(g.docker_targets("cmd //c docker stop deploy-nginx-1", ".")["containers"]),
      ["deploy-nginx-1"])
check("powershell -Command 后面整段都是载荷",
      sorted(g.docker_targets('powershell -Command docker restart deploy-nginx-1', ".")["containers"]),
      ["deploy-nginx-1"])

# xargs 把标准输入里的词追加到命令末尾，追加部分静态看不到
check("xargs 从管道左侧取容器名",
      sorted(g.docker_targets("echo deploy-nginx-1 | xargs docker restart", ".")["containers"]),
      ["deploy-nginx-1", "echo"])
check("xargs 带选项时也取得到",
      sorted(g.docker_targets("echo deploy-nginx-1 | xargs -I{} docker stop {}", ".")["containers"]),
      ["deploy-nginx-1", "echo", "{}"])
check("换个子句后管道左侧的词不再沿用",
      sorted(g.docker_targets("echo deploy-nginx-1 | cat; xargs docker restart", ".")["containers"]),
      [])

# compose 的 build 会把镜像换掉，算变更动作
check("compose build 取服务名",
      sorted(g.docker_targets(
          "docker compose -f deploy/docker-compose.local.yml build backend-java", ".")["services"]),
      ["backend-java"])
check("compose build 不带服务名",
      g.docker_targets("docker compose -f deploy/docker-compose.local.yml build", ".")["all_services"],
      True)

PREFIXED = [
    {"container": "deploy-frontend-build-run-*",
     "container_prefix": "deploy-frontend-build-run-", "service": "frontend-build",
     "project": "deploy", "label": "构建"},
]
t = g.docker_targets("docker stop deploy-frontend-build-run-68c0c66bbee6", ".")
check("一次性容器按前缀命中条目", [e["container"] for e in g.hit_entries(t, PREFIXED)],
      ["deploy-frontend-build-run-*"])
t = g.docker_targets("docker stop deploy-frontend-build-1", ".")
check("前缀对不上时不命中", g.hit_entries(t, PREFIXED), [])

with tempfile.TemporaryDirectory() as tmp:
    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker --context default restart deploy-nginx-1"}})
    check("--context 绕过时仍提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker -H tcp://127.0.0.1:2375 restart deploy-nginx-1"}})
    check("-H 绕过时仍提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker restart \\\n  deploy-nginx-1"}})
    check("续行绕过时仍提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "cmd /c docker restart deploy-nginx-1"}})
    check("cmd /c 绕过时仍提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "echo deploy-nginx-1 | xargs docker restart"}})
    check("xargs 绕过时仍提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker stop deploy-frontend-build-run-68c0c66bbee6"}},
        prefix_patch({"deploy-frontend-build-run-68c0c66bbee6"}))
    check("按容器名停一次性容器时提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker stop deploy-frontend-build-run-68c0c66bbee6"}},
        prefix_patch({"deploy-chroma-1"}))
    check("一次性容器没在跑时不提问", decision(out), None)

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml build nginx"}})
    check("compose build 独占服务时提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml build redis"}})
    check("compose build 别的服务不提问", decision(out), None)

# --- 宿主工具链判据（拆词层） ---
check("pnpm 在起首位置", host_toolchain("pnpm build"), "pnpm")
check("控制符之后的 pnpm", host_toolchain("cd code/frontend && pnpm install"), "pnpm")
check("mvn 在起首位置", host_toolchain("mvn -pl oa clean test"), "mvn")
check("带引号的绝对路径 node", host_toolchain('"C:/Program Files/nodejs/node.exe" -v'), "node")
check("node_modules 里的可执行文件", host_toolchain("./node_modules/.bin/vite build"), "vite")
check("包装命令之后的工具链", host_toolchain("time pnpm build"), "pnpm")
check("环境变量赋值之后的工具链", host_toolchain("NODE_ENV=test npx vite build"), "npx")
check("容器内执行的 mvn 不算", host_toolchain("docker compose exec backend-java mvn test"), None)
check("容器内执行的 npm 不算", host_toolchain("docker run --rm node:20 npm ci"), None)
check("提交消息里的工具链不算", host_toolchain("git commit -m 'pnpm build 的用法'"), None)
check("普通实参里的工具链不算", host_toolchain("echo time pnpm"), None)
check("python 不在名单里", host_toolchain("python -c 'import psutil'"), None)
check("是 docker 命令就不拦", host_toolchain("docker compose --profile build run --rm frontend-build"), None)

# --- 多行、分号、shell 包装、吃取值的包装命令 ---
check("多行命令第二行的工具链", host_toolchain("cd code/frontend\npnpm build"), "pnpm")
check("分号紧贴的工具链", host_toolchain("cd code/frontend; mvn test"), "mvn")
check("回车分隔的工具链", host_toolchain("cd a\r\npnpm build"), "pnpm")
check("sh -c 载荷", host_toolchain("sh -c 'pnpm build'"), "pnpm")
check("bash -c 载荷里带控制符", host_toolchain('bash -c "cd code/frontend && pnpm build"'), "pnpm")
check("bash -lc 合并短选项", host_toolchain('bash -lc "pnpm install"'), "pnpm")
check("cmd /c 载荷", host_toolchain("cmd /c npm install"), "npm")
check("powershell -Command 载荷", host_toolchain('powershell -Command "pnpm build"'), "pnpm")
check("pwsh -Command 载荷", host_toolchain('pwsh -Command "pnpm build"'), "pnpm")
check("eval 载荷", host_toolchain('eval "pnpm build"'), "pnpm")
check("两层 shell 包装", host_toolchain("bash -c \"sh -c 'pnpm build'\""), "pnpm")
check("timeout 吃取值", host_toolchain("timeout 300 mvn test"), "mvn")
check("nice 吃选项与取值", host_toolchain("nice -n 10 pnpm build"), "pnpm")
check("wsl 包装", host_toolchain("wsl pnpm build"), "pnpm")
check("普通实参里的 sh 不算", host_toolchain("echo sh -c 'pnpm build'"), None)
check("普通实参里的 timeout 不算", host_toolchain("echo timeout 300 mvn test"), None)
check("引号里的分号不切子句", host_toolchain("git commit -m 'a; pnpm build'"), None)
check("引号不闭合时仍认得出工具链", host_toolchain('echo \\" ; pnpm build'), "pnpm")
check("引号里的换行不切子句", host_toolchain("git commit -m 'a\npnpm build'"), None)
check("sudo 无选项", host_toolchain("sudo pnpm build"), "pnpm")
check("sudo 带选项", host_toolchain("sudo -u root pnpm build"), "pnpm")
check("time 带选项", host_toolchain("time -p pnpm build"), "pnpm")
check("xargs 带选项", host_toolchain("xargs -I{} pnpm build"), "pnpm")
check("管道里的 xargs 带选项", host_toolchain("echo x | xargs -I{} pnpm build"), "pnpm")
check("普通实参里的 sudo 不算", host_toolchain("echo sudo -u root pnpm"), None)
check("cmd //c 载荷", host_toolchain("cmd //c npm install"), "npm")
check("cmd /d /c 载荷", host_toolchain("cmd /d /c npm install"), "npm")

# --- heredoc 正文 ---
check("写文件的 heredoc 正文不算命令",
      host_toolchain("cat > notes.md <<'EOF'\npnpm build\nEOF"), None)
check("提交信息走 heredoc 时不算命令",
      host_toolchain("git commit -F - <<'EOF'\nfeat: x\npnpm build 说明\nEOF"), None)
check("无引号标记的 heredoc 正文也剥",
      host_toolchain("cat > notes.md <<EOF\npnpm build\nEOF"), None)
check("剥掉正文后后续子句仍在",
      host_toolchain("cat > notes.md <<'EOF'\n随便写点什么\nEOF\npnpm build"), "pnpm")
check("正文里不是起首位置的工具链不算",
      host_toolchain("cat > notes.md <<'EOF'\n先 pnpm build 再 docker compose up\nEOF"), None)
check("正文交给宿主机 shell 时保留",
      host_toolchain("bash <<'EOF'\npnpm build\nEOF"), "pnpm")
check("sudo 包一层时也保留",
      host_toolchain("sudo bash <<'EOF'\npnpm build\nEOF"), "pnpm")
check("正文交给容器里的 shell 时剥掉",
      host_toolchain("docker compose exec backend-java sh <<'EOF'\nmvn test\nEOF"), None)
check("引号里出现 << 不误判",
      host_toolchain("echo 'a << b' && pnpm build"), "pnpm")

# --- 宿主工具链判据端到端 ---
with tempfile.TemporaryDirectory() as tmp:
    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "cd code/frontend && pnpm build"}})
    check("宿主机跑 pnpm 时阻断", decision(out), "deny")
    check("阻断点名命令", "pnpm" in reason(out), True)

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose --profile build run --rm frontend-build"}},
        NO_BUSY_PATCH)
    check("容器内构建放行", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose exec backend-java mvn -v"}})
    check("容器内 mvn 放行", (decision(out), rc), (None, 0))

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "mvn -v"}})
    check("宿主机跑 mvn 时阻断", decision(out), "deny")

    out, rc = run({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "git status --short"}})
    check("git 命令放行", (decision(out), rc), (None, 0))

# --- 语义授权、远程 Git 与高风险状态 ---
REMOTE_AUTH_PATCH = (
    "g.authorization_match = lambda sid, scope: {'matched': True, 'state_error': None}\n"
)
DOCKER_AUTH_PATCH = (
    "g.read_exclusive = lambda: ["
    "{'container': 'deploy-nginx-1', 'service': 'nginx', 'project': 'deploy', 'label': 'x'},"
    "{'container': 'deploy-backend-java-1', 'service': 'backend-java', 'project': 'deploy', 'label': 'x'}]\n"
    "g.running_containers = lambda: {'deploy-nginx-1', 'deploy-backend-java-1'}\n"
    "g.other_session_count = lambda sid: (2, False)\n"
    "g.authorization_match = lambda sid, scope: {'matched': scope['targets'] == ['deploy-nginx-1'], 'state_error': None}\n"
)
with tempfile.TemporaryDirectory() as tmp:
    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "git push origin main"}}, NO_BUSY_PATCH)
    check("远程 Git 默认提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "git push --force origin main"}}, NO_BUSY_PATCH)
    check("强制推送硬拒绝", decision(out), "deny")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "git push \"origin"}}, NO_BUSY_PATCH)
    check("远程 Git 解析失败硬拒绝", decision(out), "deny")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "git push origin main"}}, NO_BUSY_PATCH + REMOTE_AUTH_PATCH)
    check("同范围远程 Git 授权复用", (decision(out), rc), (None, 0))

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker restart deploy-nginx-1"}}, DOCKER_AUTH_PATCH)
    check("同目标独占容器授权复用", (decision(out), rc), (None, 0))

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f deploy/docker-compose.local.yml up -d"}}, DOCKER_AUTH_PATCH)
    check("扩大独占目标范围重新提问", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker restart deploy-nginx-1"}},
        "g.read_exclusive = lambda: [{'container': 'deploy-nginx-1', 'service': 'nginx', 'project': 'deploy', 'label': 'x'}]\n"
        "g.running_containers = lambda: {'deploy-nginx-1'}\n"
        "g.other_session_count = lambda sid: (2, False)\n"
        "g.authorization_match = lambda sid, scope: {'matched': False, 'state_error': '状态损坏'}\n")
    check("授权状态损坏时不放行", decision(out), "ask")

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "docker compose -f production-compose.yml up -d"}}, NO_BUSY_PATCH)
    check("生产变更进入确认线", decision(out), "ask")

    for command, label in (
        ("git remote -v", "只读 git remote -v 不提问"),
        ("git remote get-url origin", "只读 git remote get-url 不提问"),
        ("git grep production", "搜索 production 不提问"),
        ("rg production .", "只读搜索 production 不提问"),
        ("git diff -- production-config.yml", "读取 production 路径不提问"),
    ):
        out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
            "command": command}}, NO_BUSY_PATCH)
        check(label, (decision(out), rc), (None, 0))

    out, rc = run_patched({"tool_name": "Bash", "cwd": tmp, "session_id": "me", "tool_input": {
        "command": "git remote add origin https://example.invalid/repo.git"}}, NO_BUSY_PATCH)
    check("修改 git remote 仍进入确认线", decision(out), "ask")

print()
print("失败项:", FAILED if FAILED else "无")
sys.exit(1 if FAILED else 0)
