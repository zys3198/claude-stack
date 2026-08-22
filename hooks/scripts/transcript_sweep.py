#!/usr/bin/env python3
"""扫最近会话 transcript 挖知识缺口（周复盘用，腾讯知识底座文「用即积累」）。

用法: python transcript_sweep.py [天数=7]

扫 ~/.claude/projects/<slug>/*.jsonl（UUID.jsonl，非 transcript.jsonl）中最近 N 天
的 user 消息，去重 + 按日活跃 + CJK 二元词组频次，输出摘要到 metrics/。
周复惯例: 跑完由模型/人工读摘要，挑 2-3 个缺口补进 memory/skill。纯 stdlib。
"""

import json, re, sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"
OUT = Path.home() / ".claude" / "metrics"
MAX_PER_FILE = 2000  # 单文件行数上限，防超大 jsonl 失控（实测可达 33MB）
STOP = set("的了是在我你他她它们有这和就也要与对吧请让帮一下个等会把给被")
CJK = lambda c: "一" <= c <= "鿿"  # 只计中文字符对，英文/代码/路径不进主题统计


def user_texts(path, cutoff):
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return
    if mtime < cutoff:
        return
    try:
        with open(path, encoding="utf-8") as f:
            n = 0
            for ln in f:
                if n >= MAX_PER_FILE:
                    break
                try:
                    obj = json.loads(ln)
                except ValueError:
                    continue
                if obj.get("type") != "user":
                    continue
                msg = obj.get("message") or {}
                c = msg.get("content")
                if isinstance(c, list):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                if not isinstance(c, str) or not c.strip():
                    continue
                n += 1
                yield c.strip(), mtime
    except (OSError, UnicodeDecodeError):
        return


def main() -> int:
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    cutoff = datetime.now().timestamp() - days * 86400
    msgs, per_day, phrases = [], Counter(), Counter()
    if ROOT.is_dir():
        for slug in ROOT.iterdir():
            if not slug.is_dir():
                continue
            for f in slug.glob("*.jsonl"):
                for text, ts in user_texts(f, cutoff):
                    msgs.append(text)
                    per_day[datetime.fromtimestamp(ts).date()] += 1
                    s = re.sub(r"[\s\W_]+", "", text)
                    for i in range(len(s) - 1):
                        if CJK(s[i]) and CJK(s[i + 1]):
                            p = s[i:i+2]
                            if p[0] not in STOP and p[1] not in STOP:
                                phrases[p] += 1
    uniq = len(set(msgs))
    top = [p for p, c in phrases.most_common(60) if c >= 3][:12]
    body = [
        f"# 周复盘 {datetime.now():%Y-%m-%d}",
        f"- 窗口 {days} 天 | user 消息 {len(msgs)} / 去重 {uniq} | 活跃天数 {len(per_day)}",
        "- 高频主题（二元词组，频次≥3，取前12）",
    ] + [f"  - {p} ×{phrases[p]}" for p in top]
    OUT.mkdir(exist_ok=True)
    (OUT / f"transcript-weekly-{datetime.now():%Y%m%d}.md").write_text(
        "\n".join(body) + "\n", encoding="utf-8")
    print(f"window={days}d  msgs={len(msgs)}  uniq={uniq}  active_days={len(per_day)}")
    for p in top:
        print(f"  {p} ×{phrases[p]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
