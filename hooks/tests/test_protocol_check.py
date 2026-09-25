"""protocol_check.py 的外部行为测试：夹具目录 + 跑脚本 + 断言输出。

直接 `python test_protocol_check.py`，无 pytest 包装，与 hooks/tests/ 下其余测试同形。
只断言退出码与输出文字，不导入被测算法的内部函数——判据改实现时这份测试不用改。
夹具用 tempfile 现搭，不留固定样本树。

正例：一份干净夹具跑全量，八类全通过、退出 0。
反例：每类各造一处违规，断言退出 1 且报出对应事实。
边界：恰好在阈值上 / 差一点 / 空目录 / 占位符，断言判与不判的分界。
"""
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

CHECK = Path(__file__).resolve().parents[1] / "scripts" / "protocol_check.py"

# 控制台默认 GBK，断言失败时打印的细节里可能带替换字符，先切 UTF-8 免得打印本身抛错。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FAILED = []


def check(label, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + label + ("" if cond else f"   ← {detail}"))
    if not cond:
        FAILED.append(label)


def build(root, spec):
    """spec: {相对路径: 内容}；路径以 / 结尾的建成空目录。

    newline="" 关掉写盘的换行翻译：体积边界那条要按字节精确凑数，
    默认翻译会把每个 \\n 变成 \\r\\n，凑不准。
    """
    for rel, text in spec.items():
        p = Path(root) / rel
        if rel.endswith("/"):
            p.mkdir(parents=True, exist_ok=True)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(text)


def run(root, only=None):
    cmd = [sys.executable, str(CHECK), "--root", str(root)]
    if only:
        cmd += ["--only", only]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def run_file(root, rel, only=None, preview=None):
    """写入事件走的那一路：只查被写的这一个文件。

    preview 是「这次写完之后的样子」，走 --content 交给检查器。
    """
    cmd = [sys.executable, str(CHECK), "--root", str(root), "--file", str(Path(root) / rel)]
    if only:
        cmd += ["--only", only]
    if preview is not None:
        temp = Path(root).parent / "preview.txt"
        with open(temp, "w", encoding="utf-8", newline="") as f:
            f.write(preview)
        cmd += ["--content", str(temp)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


TODAY = date.today()

TABLE = """## 资产 → 形态 → L0

| 资产 | 加载形态 | L0 由谁提供 |
|---|---|---|
| `~/.claude/rules/principles.md`（本文件） | 常驻 | 文件自身 |
| `~/.claude/CLAUDE.md` | 常驻 | 路由表 |
| `rules/*.md` | 条件（带 `paths`）／常驻（不带） | 文件头 |
| skill | 按需 | `description` 字段 |
| `docs/protocols/*.md` | 不进上下文 | `protocols-index.md` 对应行 |
| memory | 召回 | `MEMORY.md` 索引行 |
| `notes/` | 不进上下文 | 目录名 |
| hook | 不进上下文（平台执行） | `settings.json` matcher |
"""

GATE = """# 门禁

## 固定字段

| 键 | 说明 |
|---|---|
| `targets` | 目标 |
| `operation_family` | 操作族 |
| `impact_ceiling` | 影响上限 |
| `critical_params` | 关键参数 |

## 别的一节
"""

SCOPE_PY = 'allowed = {"targets", "operation_family", "impact_ceiling", "critical_params"}\n'

MEMORY = """---
name: note-one
description: 一条记忆
metadata:
  type: feedback
---

正文。
"""

CLEAN = {
    "CLAUDE.md": "# 常驻指令\n",
    "rules/principles.md": f"# 资产原则\n\n{TABLE}",
    "skills/demo/SKILL.md": "---\nname: demo\ndescription: 演示\n---\n\n正文。\n",
    "docs/protocols/gate.md": GATE,
    "docs/protocols-index.md": "# 协议索引\n",
    "hooks/scripts/authorization_scope.py": SCOPE_PY,
    "installing/ledger.md": "# 台账\n",
    "projects/demo/memory/note-one.md": MEMORY,
    "projects/demo/memory/MEMORY.md": "# 索引\n\n- [一条](note-one.md)\n",
}


def main():
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)

        # ---------- 正例 ----------
        good = temp / "good"
        build(good, CLEAN)
        code, out = run(good)
        check("正例·八类全跑退出 0", code == 0, out)
        check("正例·输出含八类摘要", all(k in out for k in
              ("门禁", "记忆", "命名", "体积", "重复", "密钥", "生命周期", "映射表")), out)

        def case_dir(name, spec):
            d = temp / name
            build(d, CLEAN | spec)
            return d

        def case(name, spec, only=None):
            return run(case_dir(name, spec), only)

        # ---------- 反例 · 命名 ----------
        code, out = case("naming", {"docs/报告-20260925.md": "x\n"}, "naming")
        check("反例·命名 非 ASCII 与日期格式", code == 1 and "非 ASCII" in out and "YYYY-MM-DD" in out, out)

        # ---------- 反例 · 记忆 frontmatter ----------
        code, out = case("fm", {"projects/demo/memory/bad.md": "没有围栏\n"}, "memory")
        check("反例·记忆缺围栏", code == 1 and "缺 `---` 围栏开头" in out, out)

        code, out = case("fm2", {"projects/demo/memory/bad.md": "---\nname: b\nmetadata:\n  type: 乱写\n---\n\nx\n"}, "memory")
        check("反例·记忆 type 越界", code == 1 and "不在" in out and "乱写" in out, out)

        # ---------- 反例 · 索引 ----------
        spec = {
            "projects/demo/memory/orphan.md": MEMORY.replace("note-one", "orphan").replace("一条记忆", "孤儿"),
        }
        code, out = case("orphan", spec, "memory")
        check("反例·索引孤儿", code == 1 and "没进 MEMORY.md 索引" in out, out)

        spec = {"projects/demo/memory/MEMORY.md": "# 索引\n\n- [没了](vanished.md)\n"}
        code, out = case("deadlink", spec, "memory")
        check("反例·索引死链", code == 1 and "索引指向不存在" in out, out)

        # ---------- 反例 · 体积 ----------
        big = "# 常驻\n\n" + ("字" * 1024 * 20)
        code, out = case("bigresident", {"CLAUDE.md": big}, "size")
        check("反例·常驻超限", code == 1 and "CLAUDE.md" in out and "超过 20 KB" in out, out)

        code, out = case("bigskill", {"skills/demo/SKILL.md": big}, "size")
        check("反例·skill 根入口超限", code == 1 and "skills/demo/SKILL.md" in out, out)

        # ---------- 反例 · 段落重复 ----------
        para = "这一整段是用来做重复判定的样本文字，" * 10
        spec = {
            "skills/demo/SKILL.md": f"---\nname: demo\ndescription: 演示\n---\n\n{para}\n",
            "skills/demo2/SKILL.md": f"---\nname: demo2\ndescription: 演示二\n---\n\n{para}\n",
        }
        code, out = case("dupe", spec, "dupe")
        check("反例·段落重复", code == 1 and "重复" in out and "skills/demo" in out and "skills/demo2" in out, out)

        # ---------- 反例 · 密钥 ----------
        # 假密钥用拼接构造：写成字面量的话，这份测试文件自己会被密钥判据扫出来。
        fake_anthropic = "sk-ant-" + "api03-" + "A" * 24
        code, out = case("secret", {"skills/demo/SKILL.md": f"key: {fake_anthropic}\n"}, "secret")
        check("反例·前缀密钥", code == 1 and "密钥" in out and "sk-ant" in out, out)

        fake_pem = "-----BEGIN " + "RSA PRIVATE KEY" + "-----"
        code, out = case("pem", {"installing/ledger.md": f"{fake_pem}\nMIIE\n"}, "secret")
        check("反例·私钥块", code == 1 and "私钥" in out, out)

        # ---------- 反例 · updated 过期 ----------
        old = (TODAY - timedelta(days=400)).isoformat()
        code, out = case("stale", {"rules/old.md": f"# 老规则\n\n更新：{old}\n"}, "lifecycle")
        check("反例·updated 过期", code == 1 and old in out and "过期" in out, out)

        # ---------- 反例 · 映射表 ----------
        code, out = case("newasset", {"newasset/thing.md": "x\n"}, "map")
        check("反例·未归类顶层条目", code == 1 and "newasset" in out, out)

        short_table = TABLE.replace("| hook | 不进上下文（平台执行） | `settings.json` matcher |\n", "")
        code, out = case("drift", {"rules/principles.md": f"# 资产原则\n\n{short_table}"}, "map")
        check("反例·表与判据漂移", code == 1 and "漂移" in out, out)

        # ---------- 反例 · 门禁漂移 ----------
        code, out = case("gatedrift", {"hooks/scripts/authorization_scope.py": 'allowed = {"targets"}\n'}, "gate")
        check("反例·门禁字段表漂移", code == 1 and "不一致" in out, out)

        # ---------- 边界 ----------
        limit = 20 * 1024
        # 逐字节凑到恰好 20 KB
        head = "# 常驻\n\n"
        exact = head + "x" * (limit - len(head.encode("utf-8")))
        code, out = case("size-exact", {"CLAUDE.md": exact}, "size")
        check("边界·体积恰好 20 KB 通过", code == 0, out)

        over = head + "x" * (limit - len(head.encode("utf-8")) + 1)
        code, out = case("size-over", {"CLAUDE.md": over}, "size")
        check("边界·体积超 1 字节即报", code == 1, out)

        p120 = "重复样本" * 30  # 120 汉字
        spec = {
            "skills/demo/SKILL.md": f"---\nname: demo\ndescription: 演示\n---\n\n{p120}\n",
            "skills/demo2/SKILL.md": f"---\nname: demo2\ndescription: 演示二\n---\n\n{p120}\n",
        }
        code, out = case("dupe-120", spec, "dupe")
        check("边界·恰好 120 字算重复", code == 1, out)

        p119 = "重复样本" * 30 + "字"
        spec = {
            "skills/demo/SKILL.md": f"---\nname: demo\ndescription: 演示\n---\n\n{p119[:119]}\n",
            "skills/demo2/SKILL.md": f"---\nname: demo2\ndescription: 演示二\n---\n\n{p119[:119]}\n",
        }
        code, out = case("dupe-119", spec, "dupe")
        check("边界·119 字不算重复", code == 0, out)

        edge = (TODAY - timedelta(days=180)).isoformat()
        code, out = case("stale-180", {"rules/old.md": f"# 老规则\n\n更新：{edge}\n"}, "lifecycle")
        check("边界·恰好 180 天不过期", code == 0, out)

        edge = (TODAY - timedelta(days=181)).isoformat()
        code, out = case("stale-181", {"rules/old.md": f"# 老规则\n\n更新：{edge}\n"}, "lifecycle")
        check("边界·181 天算过期", code == 1, out)

        code, out = case("empty-memory", {"projects/empty/memory/": ""}, "memory")
        check("边界·空记忆目录不报错", "没有 MEMORY.md" not in out, out)

        placeholders = (
            "api_key: sk-ant-YOUR-KEY-HERE\n"
            "token: 'your-token-here-abcdefghijklmnop'\n"
            "secret = ${SECRET_FROM_ENV}\n"
            "password: PROXY_MANAGED\n"
        )
        code, out = case("placeholders", {"skills/demo/SKILL.md": placeholders}, "secret")
        check("边界·占位符不当密钥", code == 0, out)

        # 未声明日期只计数、不报错
        code, out = case("undeclared", {}, "lifecycle")
        check("边界·无日期标记只计数不报错", code == 0 and "未声明" in out, out)

        # ---------- 收窄：只查被写的那一个文件 ----------
        big2 = "# 常驻\n\n" + ("字" * 1024 * 20)
        narrow = case_dir("narrow", {
            "skills/demo2/SKILL.md": big2, "newasset/thing.md": "x\n", "docs/plain.md": "# 中性\n",
        })
        code, out = run_file(narrow, "docs/plain.md")
        check("收窄·干净文件退出 0", code == 0, out)
        check("收窄·点名查了哪几类", "被写 docs/plain.md · 判据" in out, out)
        check("收窄·别处的超限不报", "SKILL.md" not in out, out)
        check("收窄·别处的未归类条目不报", "newasset" not in out, out)
        check("收窄·判不了的项照样列出", "判不了" in out, out)

        code, out = run_file(narrow, "skills/demo2/SKILL.md")
        check("收窄·被写的超限文件报出来", code == 1 and "超过 20 KB" in out, out)

        code, out = run_file(narrow, "newasset/thing.md")
        check("收窄·被写的未归类条目报出来", code == 1 and "newasset" in out, out)

        code, out = run_file(narrow, "projects/demo/memory/note-one.md")
        check("收窄·干净记忆退出 0", code == 0, out)

        orphan_dir = case_dir("narrow-orphan", {
            "projects/demo/memory/orphan2.md": MEMORY.replace("note-one", "orphan2"),
        })
        code, out = run_file(orphan_dir, "projects/demo/memory/orphan2.md")
        check("收窄·刚写的记忆没进索引报出来", code == 1 and "没进 MEMORY.md 索引" in out, out)

        index_dir = case_dir("narrow-index", {
            "projects/demo/memory/MEMORY.md": "# 索引\n\n- [没了](vanished.md)\n",
        })
        code, out = run_file(index_dir, "projects/demo/memory/MEMORY.md")
        check("收窄·写索引时报整份索引的死链", code == 1 and "索引指向不存在" in out, out)

        # 表侧问题（漂移、某一行找不到对应物）只在写 principles.md 时报
        short2 = TABLE.replace("| hook | 不进上下文（平台执行） | `settings.json` matcher |\n", "")
        drift_dir = case_dir("narrow-drift", {"rules/principles.md": f"# 资产原则\n\n{short2}"})
        code, out = run_file(drift_dir, "CLAUDE.md")
        check("收窄·写别的文件不报表漂移", code == 0, out)
        code, out = run_file(drift_dir, "rules/principles.md")
        check("收窄·写映射表本身才报表漂移（且在阻断区，退出 3）", code == 3 and "漂移" in out, out)

        # ---------- 阻断区：常驻区与原则区给 3，其余区仍旧给 1 ----------
        big3 = "# 常驻\n\n" + ("字" * 1024 * 20)
        code, out = run_file(narrow, "CLAUDE.md", preview=big3)
        check("阻断·常驻区将要超限的写入给 3", code == 3 and "超过 20 KB" in out, out)

        code, out = run_file(narrow, "rules/new-rule.md", preview=big3)
        check("阻断·还没落盘的原则区新文件也算", code == 3 and "new-rule.md" in out, out)

        code, out = run_file(narrow, "skills/demo2/SKILL.md", preview=big3)
        check("阻断·其他区写着超限文件只给 1", code == 1 and "超过 20 KB" in out, out)

        # 判的是「写完之后的样子」：盘上现状与预览不一致时，以预览为准
        code, out = run_file(good, "CLAUDE.md", preview=big3)
        check("阻断·按预览判而不是按盘上现状", code == 3, out)

        # 反过来：盘上已经违规、这次写入是把它改好 → 放行，否则违规文件永远改不动
        fix_dir = case_dir("block-fix", {"CLAUDE.md": big3})
        code, out = run_file(fix_dir, "CLAUDE.md", preview="# 常驻\n\n改小了。\n")
        check("阻断·修掉违规的那次写入放行", code == 0, out)

        code, out = run_file(fix_dir, "CLAUDE.md")
        check("阻断·不传预览时按盘上现状判（同样给 3）", code == 3 and "超过 20 KB" in out, out)

        # 原则区新文件抄别处的段落：重复判据也按预览算
        dupe_dir = case_dir("block-dupe", {
            "skills/demo/SKILL.md": f"---\nname: demo\ndescription: 演示\n---\n\n{para}\n",
        })
        code, out = run_file(dupe_dir, "rules/dup.md", preview=f"# 规则\n\n{para}\n")
        check("阻断·原则区新文件抄别处段落被拦", code == 3 and "重复" in out, out)

        code, out = run_file(dupe_dir, "docs/protocols/probe.md", preview=f"# 协议\n\n{para}\n")
        check("阻断·其他区抄同一段只报告（给 1）", code == 1 and "重复" in out, out)

        # 假密钥用拼接构造：写成字面量的话，这份测试文件自己会被密钥判据扫出来。
        fake2 = "sk-ant-" + "api03-" + "B" * 24
        code, out = run_file(good, "rules/principles.md", preview=f"# 资产原则\n\n{TABLE}\nkey: {fake2}\n")
        check("阻断·原则区写入含密钥被拦", code == 3 and "密钥" in out, out)

        # 全量模式一律只报告：夹具里就有常驻超限，仍旧退出 1
        code, out = run(fix_dir)
        check("阻断·全量模式不阻断，仍给 1", code == 1 and "超过 20 KB" in out, out)

        code, out = run_file(narrow, "../../escape.md")
        check("收窄·根之外的路径直接拒绝", code == 2 and "不在被检查的根" in out, out)

        # 交集为空 = 一类都不跑，不能退化成「八类全跑」
        code, out = run_file(narrow, "docs/plain.md", only="gate")
        check("收窄·与 --only 交集为空则一类都不跑", code == 0 and "判据 （无" in out, out)
        check("收窄·交集为空时不报别类的命中", "20 KB" not in out, out)

        # 判不了的项始终列出
        code, out = run(good, "naming")
        check("判不了·始终显式列出", "判不了" in out, out)

    if FAILED:
        print(f"\n{len(FAILED)} 项未过：")
        for f in FAILED:
            print("  -", f)
        return 1
    print("\nPASS protocol check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
