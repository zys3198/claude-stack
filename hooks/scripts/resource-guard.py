# 资源守卫：PreToolUse 阶段拦截三类破坏本机 Docker 使用约定、且可以客观判定的动作。
# 规则依据见 ~/.claude/CLAUDE.md 第 6.3 节（容器内存上限、独占资源先协商、
# 一律在容器内执行）与第 8 节。
#
# 判据一：docker-compose 文件改动后，相对改动前新增的服务必须同时声明 mem_limit 与
#   security_opt。只检查新增的服务，历史文件里本来就缺限制的老服务不重复报，
#   否则在一个整体没有限制的文件（例如生产环境的 compose）里每改一行都会触发。
# 判据二：命令要对 session-hygiene.json 独占清单里的容器做变更动作，该容器正在运行，
#   且本机另有活跃 Claude 会话时提请确认。容器与端口属于本机资源，按机器共享，
#   不按项目隔离，因此别的项目里的会话也计入。docker compose run 起的一次性容器
#   名字带随机后缀，登记时给不出完整名字，这类条目改填 container_prefix，按前缀认。
# 判据三：命令要在宿主机上跑构建工具链（pnpm、mvn、java、node 之类）时提请确认。
#   同一批名字写在容器内执行的命令里（docker compose exec <服务> mvn test）不在起首
#   位置，不会被拦。
#
# 只拦可以客观判定的动作，不做主观推测，其余一律放行。
# 判定方式是把命令拆成词，要求目标命令出现在命令起首位置（行首，或管道与分号、
# 换行、包装命令、环境变量赋值之后），再逐个取出目标服务名与容器名比对，
# 不用「命令里是否出现某个子串」来判断。
# 换行、分号、sh -c / cmd /c / powershell -Command / eval 的载荷都会先拆开再扫，
# 因此把命令写成多行、用分号连接、或包一层 shell 都取得到起首位置。
#
# 已知覆盖不到的情形：命令替换 $(...) 里的文本取不到；
# 变量拼接的命令名（CMD=pnpm; $CMD build）静态分析看不到；
# compose 文件不是合法 YAML、或改动前的内容读不到时跳过判据一；
# 判据一只看 Write/Edit/MultiEdit 的改动内容，Bash 里的改写按「写文件命令加目标文件名」
# 粗判，因此 python -c "open(...)" 与变量拼出来的目标路径取不到；
# 判据二只认命令里显式写出的服务名与容器名，不带服务名的 docker compose up -d
# 要靠 -p 项目名、-f 所在目录名、--project-directory、命令里的 cd 目标或当前目录名
# 对上项目才会命中，五者都对不上时放行；判据三不含 python，理由见 HOST_TOOLCHAIN。
# 本守卫定位是防止误建，不作为安全边界。
# 异常写入 resource-guard.log，不阻塞工具调用。

import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

import yaml

CLAUDE = Path(os.path.expanduser("~")) / ".claude"
LOGFILE = CLAUDE / "resource-guard.log"
HYGIENE = CLAUDE / "session-hygiene.json"

COMPOSE_FILE = re.compile(r"^[\w.-]*compose[\w.-]*\.ya?ml$", re.I)
# heredoc 起始标记：<<EOF、<<'EOF'、<<-EOF。用来把正文从命令里剥掉。
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")
# 新增服务必须同时具备的两项。依据 CLAUDE.md 第 6.3 节与第 8 节：
# 内存上限防单容器吃光本机，禁止提权防容器内进程拿到 root 之外的额外权限。
REQUIRED_KEYS = ("mem_limit", "security_opt")
# 判据一在 Bash 路径上的粗判：这些命令会把内容写进文件，取出目标文件名比对 compose 文件名。
WRITE_COMMANDS = {"tee", "cp", "mv"}
# sed 只有带 -i 时才写回原文件，不带 -i 是只读过滤。
INPLACE_COMMANDS = {"sed"}

COMPOSE_VERBS = {"up", "down", "create", "start", "restart", "stop", "kill", "rm", "run"}
DOCKER_VERBS = {"create", "start", "restart", "stop", "kill", "rm", "run", "update"}
# docker container restart X、docker volume rm X 这类写法在动词前多一层名词。
DOCKER_OBJECT_NOUNS = {"container", "volume", "image", "network", "service"}
# 会改变当前目录的命令，用来推断不带 -p/-f 的整项目命令作用于哪个项目。
CD_TOKENS = {"cd", "pushd", "chdir"}
# 这两个子命令的位置实参是镜像名与容器内命令，容器名只来自 --name。
# 把位置实参当容器名收集会把镜像名一起收进来。
DOCKER_NAME_BY_OPT = {"create", "run"}
# 会吃掉下一个词的选项。漏登记一项只会让它后面的取值被当成位置实参，
# 最坏结果是多问一次，不会漏报，因此只登记常见项。
COMPOSE_OPTS_WITH_VALUE = {
    "-f", "--file", "-p", "--project-name", "--profile", "--env-file",
    "--project-directory", "--ansi", "--progress", "--parallel", "--context", "-c",
}
DOCKER_OPTS_WITH_VALUE = {
    "-v", "--volume", "-p", "--publish", "-e", "--env", "-w", "--workdir",
    "-u", "--user", "-m", "--memory", "-c", "--cpu-shares", "--name", "--network",
    "--net", "--label", "--mount", "--entrypoint", "--restart", "--env-file",
    "--log-driver", "--stop-signal", "--cpus", "--memory-swap",
}
# 命令起首位置出现这些名字时按「宿主机上的构建工具链」拦下。依据 CLAUDE.md 第 6.3 节：
# 在本机运行的构建、测试与服务一律在容器内执行，宿主机只保留只读查看、git 与 docker。
# 不含 python：宿主机上的 python 在本机只用于只读查看（查进程与端口、跑 ~/.claude 下的
# 状态脚本），而它是通用解释器，命令行上看不出是查一下还是起一个服务。
HOST_TOOLCHAIN = {
    "pnpm", "npm", "npx", "yarn", "bun", "corepack",
    "node", "vite", "tsc", "vue-tsc", "tsx", "ts-node", "webpack",
    "mvn", "mvnw", "gradle", "gradlew", "java", "javac",
}
# 命令名之前可以挡着包装命令与环境变量赋值，此时它仍然处在命令起首位置。
COMMAND_PREFIX = {"env", "sudo", "time", "nohup", "exec", "command", "xargs", "winpty"}
# 这些包装命令自己会吃掉若干选项与取值（`timeout 300 mvn test`、`nice -n 10 pnpm build`），
# 被包装的命令名字因此不紧跟在包装命令后面。它们之后到本子句结束都按命令起首位置处理，
# 宁可多问一次也不漏。不含 python：见 HOST_TOOLCHAIN 里的理由。
WRAPPER_WITH_ARGS = {
    "timeout", "nice", "ionice", "stdbuf", "setsid", "chroot", "doas",
    "watch", "parallel", "unbuffer", "taskset", "wsl", "start",
}
# 回溯扫描时要一起认的两类：它们都会吃掉若干选项与取值，被包装的命令名字因此不紧跟在后面。
PREFIX_WITH_ARGS = COMMAND_PREFIX | WRAPPER_WITH_ARGS
# 这些命令把后面的一段文本当成新的 shell 命令执行，需要拆出来再扫一遍。
SHELL_INTERPRETERS = {"sh", "bash", "zsh", "dash", "ksh", "ash", "cmd", "powershell", "pwsh"}
EVAL_COMMANDS = {"eval"}
ENV_ASSIGN = re.compile(r"^\w+=")
# shlex 因引号不闭合拆不开时的兜底切分：shell 控制符与普通词各自成词，
# 形态与 punctuation_chars 的正常输出一致，下游判据不需要区分两种来源。
FALLBACK_TOKENS = re.compile(r"[;&|()<>]+|[^\s;&|()<>]+")

DOCKER_TIMEOUT = 10
AGENTS_TIMEOUT = 20


def log(message):
    try:
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{stamp} {message}\n")
    except OSError:
        pass


REASONS = []


def ask(reason):
    # 三条判据可能同时命中，结论先攒着，最后只输出一个 JSON 对象。
    # 分两次打印会让钩子的标准输出变成两行 JSON，调用方无法解析。
    REASONS.append(reason)


def is_control(token):
    # shell 控制符与重定向。出现在命令位置说明前一个子句已经结束，
    # docker 跟在它后面算新命令的起首位置。
    # 拆词会把连续的控制符合成一个词（&&、;;），因此按字符判定而不是逐个比对。
    if not token:
        return False
    if all(c in ";|&()" for c in token):
        return True
    return bool(re.match(r"^\d*[<>]", token))


def command_name(token):
    # 命令名按最后一段判定，覆盖 node、node.exe、C:/.../node 与 ./node_modules/.bin/vite。
    name = os.path.basename(token.replace("\\", "/")).lower()
    for suffix in (".exe", ".cmd", ".bat"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def is_docker_token(token):
    # 只做精确名字比对，不把 docker-compose 这类写在命令名里的旧式命令算进来。
    return command_name(token) == "docker"


def is_legacy_compose_token(token):
    # 旧式 docker-compose 命令。它自己就相当于 docker compose，中间没有 compose 这个词。
    return command_name(token) == "docker-compose"


def starts_command(tokens, i):
    # tokens[i] 是否处在命令起首位置：行首，或前一个词是控制符、包装命令、环境变量赋值。
    # 包装命令要自己也在起首位置才算数，否则 `echo time pnpm` 这类会把普通实参误判成命令。
    if i == 0:
        return True
    prev = tokens[i - 1]
    if is_control(prev) or ENV_ASSIGN.match(prev):
        return True
    name = command_name(prev)
    if name in WRAPPER_WITH_ARGS:
        return True
    if name in COMMAND_PREFIX:
        return starts_command(tokens, i - 1)
    # 包装命令自己会吃选项与取值，被包装的命令名字不紧跟其后，因此还要看本子句里
    # 更靠前有没有出现过包装命令。sudo -u root、xargs -I{}、time -p 都属这一类。
    j = i - 1
    while j >= 0 and not is_control(tokens[j]):
        if starts_command(tokens, j) and command_name(tokens[j]) in PREFIX_WITH_ARGS:
            return True
        j -= 1
    return False


def norm(path):
    return os.path.normcase(os.path.realpath(os.path.abspath(path)))


def directory_name(target, cwd):
    # 一个目录路径的最后一段。相对路径按 cwd 展开。用来把不带 -p/-f 的整项目命令
    # 对到独占清单的项目名上，只看目录名，不要求该目录真的存在。
    full = target if os.path.isabs(target) else os.path.join(cwd, target)
    return os.path.basename(norm(full)) or None


def lex(text):
    # 拆词。反斜杠写法统一成斜杠；引号不闭合时返回 None 表示无法判定。
    try:
        lexer = shlex.shlex(text.replace("\\", "/"), posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        return list(lexer)
    except ValueError:
        return None


def strip_heredoc_bodies(command):
    # heredoc 正文是数据，里面的工具链名字不是命令，按行剥掉以免误报。
    # 正文交给宿主机上的 shell 解释器执行时（bash <<'EOF'）保留，此时它确实是命令；
    # 交给容器里的 shell（docker compose exec x sh <<'EOF'）时仍按数据剥掉，
    # 否则正文里的 mvn 会因为它前面多出一个子句分隔符而被当成宿主机上的命令。
    # 结束标记行与正文一起剥掉，剩下的那一行仍然带着 <<EOF，拆词时 << 是控制符，不影响后续子句。
    lines = command.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        marks = []
        for m in HEREDOC.finditer(line):
            head = lex(line[:m.start()])
            if head is None:
                # 引号没闭合，认不出这一行是什么命令，保守起见不剥
                continue
            interpreter = [j for j, t in enumerate(head)
                           if command_name(t) in SHELL_INTERPRETERS and starts_command(head, j)]
            if not interpreter:
                marks.append(m.group(2))
        i += 1
        for mark in marks:
            while i < len(lines) and lines[i].strip() != mark:
                i += 1
            i += 1
    return "\n".join(out)


def split_tokens(command):
    # 先剥掉 heredoc 正文，再把换行与分号统一成子句分隔符后拆词，否则把命令写成多行
    # 或用分号连接时，第二行起首的工具链名字取不到起首位置。
    # punctuation_chars 让 shlex 把 ; | & ( ) < > 各自成词，同时保留引号语义，
    # 因此引号里的分号不会被子句切分。
    text = strip_heredoc_bodies(command).replace("\n", ";").replace("\r", ";")
    tokens = lex(text)
    if tokens is not None:
        return tokens
    # 引号不闭合时 shlex 拆不开。返回空会让整条命令跳过三条判据（实测
    # echo \" && docker restart <独占容器> 能绕过，引号个数为偶数时又被正常拦下），
    # 因此退化成按控制符与普通词粗暴切分，照常交给下游扫描。
    return FALLBACK_TOKENS.findall(text.replace("\\", "/"))


def is_shell_c_flag(name, flag):
    # 包装命令后面那个「下一段文本是命令」的开关：sh 系的 -c / -lc，cmd 的 /c，
    # powershell 的 -Command（可缩写成 -c、-com 等）。
    low = flag.lower()
    if name == "cmd":
        # Git Bash 的 MSYS 路径转换会把 /c 当路径改写，逼着人写成 //c
        return low in {"/c", "//c"}
    if name in {"powershell", "pwsh"}:
        # -Command 可以缩写成 -c、-co；去掉前导连字符后再比对前缀
        return len(low) > 1 and low.startswith("-") and "command".startswith(low[1:])
    return bool(re.match(r"^-[a-z]*c$", low))


def payload_after(tokens, i, name):
    # 取包装命令后面被当作 shell 文本执行的那段。eval 直接吃剩下的全部，
    # sh 系与 cmd、powershell 要跟一个开关。
    if name in EVAL_COMMANDS:
        rest = []
        for t in tokens[i + 1:]:
            if is_control(t):
                break
            rest.append(t)
        return " ".join(rest) or None
    j = i + 1
    while j < len(tokens) and not is_control(tokens[j]):
        if is_shell_c_flag(name, tokens[j]):
            return tokens[j + 1] if j + 1 < len(tokens) else None
        j += 1
    return None


def expand_command(command, depth=0):
    # 返回这个命令本身、以及它内部所有被当作 shell 文本执行的载荷，各自拆好词。
    # 覆盖 sh -c '...'、cmd /c ...、powershell -Command ...、eval ...，可嵌套到三层。
    tokens = split_tokens(command)
    if tokens is None:
        return []
    out = [tokens]
    if depth >= 3:
        return out
    for i, token in enumerate(tokens):
        name = command_name(token)
        if name not in SHELL_INTERPRETERS and name not in EVAL_COMMANDS:
            continue
        if not starts_command(tokens, i):
            continue
        payload = payload_after(tokens, i, name)
        if payload:
            out.extend(expand_command(payload, depth + 1))
    return out


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def apply_edits(before, edits):
    # 按 Edit 的行为在内存里重放改动，得到写入之后的完整内容。
    # 找不到 old_string 时返回 None——实际执行会因此失败，守卫不猜结果。
    text = before
    for e in edits:
        old = e.get("old_string")
        new = e.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str):
            return None
        if old not in text:
            return None
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def compose_after(tool, tool_input, cwd):
    # 返回 (改动后内容, 改动前内容)。改动前的内容取不到时值为 None，
    # 该文件此前不存在与它等价。无法判定改动后内容时整体返回 None。
    path = tool_input.get("file_path") or tool_input.get("path")
    if not isinstance(path, str) or not path:
        return None
    full = path if os.path.isabs(path) else os.path.join(cwd, path)
    before = read_text(full)
    if tool == "Write":
        after = tool_input.get("content")
        return (after, before) if isinstance(after, str) else None
    if tool == "Edit":
        if before is None:
            return None
        edits = [tool_input]
    else:
        edits = tool_input.get("edits")
        if not isinstance(edits, list) or not edits or before is None:
            return None
    after = apply_edits(before, edits)
    return None if after is None else (after, before)


def service_map(text):
    # 返回 {服务名: 服务定义}。不是合法 YAML 或没有 services 段时返回 None。
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    if not isinstance(doc, dict):
        return None
    services = doc.get("services")
    if not isinstance(services, dict):
        return None
    return services


def missing_keys(service):
    if not isinstance(service, dict):
        return list(REQUIRED_KEYS)
    return [k for k in REQUIRED_KEYS if not service.get(k)]


def check_compose(tool, tool_input, cwd):
    path = tool_input.get("file_path") or tool_input.get("path")
    name = os.path.basename(str(path).replace("\\", "/")) if isinstance(path, str) else ""
    if not COMPOSE_FILE.match(name):
        return
    got = compose_after(tool, tool_input, cwd)
    if got is None:
        log(f"skip compose check: 无法判定 {name} 改动后的内容")
        return
    after, before = got
    after_services = service_map(after)
    if after_services is None:
        log(f"skip compose check: {name} 改动后不是含 services 段的合法 YAML")
        return
    if before is None:
        before_services = {}
    else:
        before_services = service_map(before)
        if before_services is None:
            log(f"skip compose check: {name} 改动前的内容读不到，无法判定哪些服务是新增的")
            return
    problems = []
    for svc_name, svc in after_services.items():
        if svc_name in before_services:
            continue
        gaps = missing_keys(svc)
        if gaps:
            problems.append(f"{svc_name} 缺 {'、'.join(gaps)}")
    if not problems:
        return
    ask(
        f"docker-compose 文件 {name} 里新增的服务没有写全资源限制：{'；'.join(problems)}。"
        f"依据 ~/.claude/CLAUDE.md 第 6.3 节，每个服务都要同时声明 mem_limit"
        f"（内存上限）与 security_opt（禁止容器内进程提权）。补齐后再写入。"
    )


def is_inplace_flag(token):
    # sed 写回原文件的开关：-i、-Ei、-i.bak，以及长写法 --in-place
    if token.startswith("--"):
        return token == "--in-place"
    return token.startswith("-") and "i" in token[1:]


def compose_write_targets(tokens):
    # 从拆好的词里取出会被写入的文件名。覆盖重定向（>、>>）、tee、cp、mv 与 sed -i。
    # 位置实参里可能混着非文件名（sed 的脚本参数），交给调用方按文件名判定，这里不过滤。
    out = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if re.match(r"^\d*>>?$", token):
            # 重定向符号后面那个词是目标；<< 是输入，不算
            if i + 1 < len(tokens) and not is_control(tokens[i + 1]):
                out.append(tokens[i + 1])
            i += 1
            continue
        name = command_name(token)
        if starts_command(tokens, i) and (name in WRITE_COMMANDS or name in INPLACE_COMMANDS):
            writes = name in WRITE_COMMANDS
            args = []
            j = i + 1
            while j < len(tokens) and not is_control(tokens[j]):
                arg = tokens[j]
                if arg.startswith("-") and arg != "-":
                    if name in INPLACE_COMMANDS and is_inplace_flag(arg):
                        writes = True
                    j += 1
                    continue
                args.append(arg)
                j += 1
            if writes:
                # cp 与 mv 只有最后那个位置实参是写入目标，前面的都是来源
                out.extend(args[-1:] if name in {"cp", "mv"} else args)
            i = j
            continue
        i += 1
    return out


def check_compose_write(command, cwd):
    # 判据一在 Bash 路径上的落地。Write/Edit 能读到改动前后的内容，可以精确比对新增服务；
    # 这里读不到，只能在命中 compose 文件名时提请确认。
    if not isinstance(command, str):
        return
    for tokens in expand_command(command):
        for target in compose_write_targets(tokens):
            name = os.path.basename(target.replace("\\", "/"))
            if COMPOSE_FILE.match(name):
                ask(
                    f"该命令要改写 docker-compose 文件 {name}。依据 ~/.claude/CLAUDE.md 第 6.3 节，"
                    f"新增的服务必须同时声明 mem_limit（内存上限）与 security_opt"
                    f"（禁止容器内进程提权），而通过重定向或 sed 这类写法改写时读不到改动前后的"
                    f"内容，无法自动核对。确认这次改动会写全这两项之后继续。"
                )
                return


def scan_docker(tokens, out):
    # 扫一遍拆好的词，把每一处 docker 变更动作作用的对象写进 out，返回是否匹配到变更动作。
    matched = False
    i = 0
    while i < len(tokens):
        # 只认命令起首位置的 docker。提交消息、配置文件正文里出现的 docker 字样
        # 不在起首位置，不会被当成真的执行。
        if is_docker_token(tokens[i]) and starts_command(tokens, i):
            i += 1
            while i < len(tokens) and tokens[i].startswith("-") and not is_control(tokens[i]):
                i += 1
            if i >= len(tokens):
                break
            # docker container restart X、docker volume rm X 在动词前多一层名词
            if tokens[i] in DOCKER_OBJECT_NOUNS:
                i += 1
            if i >= len(tokens) or is_control(tokens[i]):
                continue
            if tokens[i] != "compose":
                if tokens[i] in DOCKER_VERBS:
                    matched = True
                    verb = tokens[i]
                    i += 1
                    while i < len(tokens) and not is_control(tokens[i]):
                        t = tokens[i]
                        if t.startswith("-") and t != "-":
                            key, sep, value = t.partition("=")
                            if sep:
                                if key == "--name":
                                    out["containers"].add(value)
                                i += 1
                                continue
                            if key in DOCKER_OPTS_WITH_VALUE and i + 1 < len(tokens):
                                if key == "--name":
                                    out["containers"].add(tokens[i + 1])
                                i += 2
                                continue
                            i += 1
                            continue
                        # run 与 create 的位置实参是镜像名与容器内命令，
                        # 只有别的子命令的位置实参才是要操作的容器
                        if verb not in DOCKER_NAME_BY_OPT:
                            out["containers"].add(t)
                        i += 1
                    continue
                # 其余子命令（ps、logs、exec 之类）不改变容器状态
                while i < len(tokens) and not is_control(tokens[i]):
                    i += 1
                continue
            i += 1
        elif is_legacy_compose_token(tokens[i]) and starts_command(tokens, i):
            # 旧式 docker-compose 后面直接跟子命令，没有 compose 这个词
            i += 1
        else:
            # 记下命令里 cd 到哪个目录，供不带 -p/-f 的整项目命令推断所属项目
            if tokens[i].lower() in CD_TOKENS and starts_command(tokens, i):
                target = tokens[i + 1] if i + 1 < len(tokens) else None
                if target and not is_control(target):
                    out["cd_dir"] = directory_name(target, out["cwd"])
            i += 1
            continue
        # 到这里处在 compose 子命令位置
        opts = {}
        args = []
        while i < len(tokens) and not is_control(tokens[i]):
            t = tokens[i]
            if t.startswith("-") and t != "-":
                key, sep, value = t.partition("=")
                if sep:
                    opts[key] = value
                    i += 1
                elif key in COMPOSE_OPTS_WITH_VALUE and i + 1 < len(tokens):
                    opts[key] = tokens[i + 1]
                    i += 2
                else:
                    i += 1
                continue
            args.append(t)
            i += 1
        if args and args[0] in COMPOSE_VERBS:
            matched = True
            out["services"].update(args[1:])
            if len(args) == 1:
                out["all_services"] = True
        out["project"] = opts.get("-p") or opts.get("--project-name") or out["project"]
        file_opt = opts.get("-f") or opts.get("--file")
        if file_opt:
            full = file_opt if os.path.isabs(file_opt) else os.path.join(out["cwd"], file_opt)
            out["compose_dir"] = os.path.basename(os.path.dirname(norm(full))) or None
        dir_opt = opts.get("--project-directory")
        if dir_opt:
            # 这个选项给的是目录，项目名取它的最后一段，与 -f 所在目录名同等对待
            out["project_dir"] = directory_name(dir_opt, out["cwd"])
    return matched


def docker_targets(command, cwd):
    # 取出命令里每一处 docker 变更动作作用的对象，命令本身与它内部由 sh -c、eval
    # 之类传进来的载荷一起扫。
    # 返回 None 表示命令里没有这类动作；否则返回 {services, containers, project,
    # compose_dir, cd_dir, cwd, all_services}。
    out = {"services": set(), "containers": set(), "project": None,
           "compose_dir": None, "project_dir": None, "cd_dir": None,
           "cwd": cwd, "all_services": False}
    matched = False
    for tokens in expand_command(command):
        if scan_docker(tokens, out):
            matched = True
    return out if matched else None


def read_exclusive():
    text = read_text(HYGIENE)
    if text is None:
        return []
    try:
        doc = json.loads(text)
    except ValueError:
        return []
    rows = doc.get("exclusive") if isinstance(doc, dict) else None
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict) and r.get("container")]


def hit_entries(targets, entries):
    hits = []
    dirs = {targets["project"], targets["compose_dir"], targets["project_dir"],
            targets["cd_dir"], directory_name(".", targets["cwd"])}
    dirs.discard(None)
    for entry in entries:
        if entry["container"] in targets["containers"]:
            hits.append(entry)
            continue
        service = entry.get("service")
        if service and service in targets["services"]:
            hits.append(entry)
            continue
        project = entry.get("project")
        if not targets["all_services"] or not project:
            continue
        # 不带服务名时该命令作用于整个项目，用 -p 项目名、-f 所在目录名、
        # 命令里的 cd 目标或当前工作目录名对项目
        if project in dirs:
            hits.append(entry)
    return hits


def is_running(entry, running):
    # docker compose run 起的一次性容器名字带随机后缀（实测 deploy-nginx-run-68c0c66bbee6），
    # 登记时给不出完整名字，这类条目填 container_prefix，按前缀认。
    prefix = entry.get("container_prefix")
    if prefix:
        return any(name.startswith(prefix) for name in running)
    return entry["container"] in running


def running_containers():
    # 枚举失败时返回 None。返回空集合会被当成「都没有在跑」而放过，
    # 因此失败与空集必须分开表达。
    try:
        r = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DOCKER_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        log(f"docker ps 执行失败：{exc}")
        return None
    if r.returncode != 0:
        log(f"docker ps 返回 {r.returncode}：{(r.stderr or '').strip()[:200]}")
        return None
    return {line.strip() for line in (r.stdout or "").splitlines() if line.strip()}


def other_session_count(self_id):
    # 返回 (别的活跃会话数, 是否降级)。枚举失败时降级为 0 并由调用方放行。
    try:
        r = subprocess.run(
            ["claude", "agents", "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=AGENTS_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        log(f"claude agents 执行失败：{exc}")
        return 0, True
    if r.returncode != 0:
        log(f"claude agents 返回 {r.returncode}：{(r.stderr or '').strip()[:200]}")
        return 0, True
    try:
        rows = json.loads(r.stdout or "[]")
    except ValueError:
        return 0, True
    if not isinstance(rows, list):
        return 0, True
    return sum(
        1 for d in rows
        if isinstance(d, dict) and d.get("sessionId") and d.get("sessionId") != self_id
    ), False


def host_toolchain(command):
    # 返回命令起首位置出现的宿主工具链命令名，没有则返回 None。提交消息、配置文件正文
    # 以及容器内执行的命令里出现的这些名字不在起首位置，不会被当成要在宿主机上执行。
    # 命令本身与它内部由 sh -c、eval 之类传进来的载荷一起扫。
    for tokens in expand_command(command):
        for i, token in enumerate(tokens):
            name = command_name(token)
            if name in HOST_TOOLCHAIN and starts_command(tokens, i):
                return name
    return None


def check_host_toolchain(command):
    if not isinstance(command, str):
        return
    name = host_toolchain(command)
    if name is None:
        return
    ask(
        f"该命令要在宿主机上执行 {name}。依据 ~/.claude/CLAUDE.md 第 6.3 节，需要在本机"
        f"运行的构建、测试与服务一律在容器内执行，宿主机只保留只读查看、git 与 docker 命令。"
        f"改到容器内执行，或在 compose 里加一个对应服务。"
    )


def check_docker(command, cwd, self_id):
    if not isinstance(command, str):
        log(f"skip docker check: command 不是字符串（{type(command).__name__}）")
        return
    targets = docker_targets(command, cwd)
    if targets is None:
        return
    hits = hit_entries(targets, read_exclusive())
    if not hits:
        return
    running = running_containers()
    if running is None:
        return
    busy = [e for e in hits if is_running(e, running)]
    if not busy:
        return
    count, degraded = other_session_count(self_id)
    if degraded or not count:
        return
    names = "、".join(e["container"] for e in busy)
    labels = "；".join(f"{e['container']}：{e.get('label', '')}" for e in busy)
    ask(
        f"该命令要变更容器 {names}，它登记在 ~/.claude/session-hygiene.json 的独占清单里，"
        f"当前正在运行，且本机另有 {count} 个活跃 Claude 会话。{labels}。"
        f"确认没有别的会话在用它之后继续。"
    )


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):
        sys.exit(0)
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    tool = payload.get("tool_name") or ""
    cwd = payload.get("cwd") or os.getcwd()
    try:
        if tool == "Bash":
            command = tool_input.get("command")
            check_compose_write(command, cwd)
            check_docker(command or "", cwd, payload.get("session_id"))
            check_host_toolchain(command)
        else:
            check_compose(tool, tool_input, cwd)
    except Exception as exc:
        import traceback
        log(f"check failed: {exc}\n{traceback.format_exc()}")
    if REASONS:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": "\n".join(REASONS),
            },
        }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
