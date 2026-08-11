# RESTORE_SYMLINKS

> **头注 2026-08-11**：历史流程文档。现行政策 Windows 不手搓 symlink（CLAUDE.md §9），且 `skills/` 已全为真目录（0 软链）、白名单制入 git——本脚本流程已不适用，保留存档。

重建 `C:\Users\zys31\.claude\skills\` 下所有 symlink，指向 `.cc-switch\skills\`。

## 跑法

把下面【脚本】代码块存为 `RESTORE_SYMLINKS.py`，然后：

```bash
python RESTORE_SYMLINKS.py
```

## 适用场景

- symlink 断裂 / 误删
- 换机器后一键恢复
- `.claude\skills\` 被清理过

## 脚本

```python
import os

SRC = r"C:\Users\zys31\.cc-switch\skills"
DST = r"C:\Users\zys31\.claude\skills"

def to_msys2(p):
    # C:\Users\... -> /c/users/... （匹配 Git Bash readlink 输出）
    return "/" + p.lower().replace("\\", "/").replace(":", "")

created, skipped = [], []
os.makedirs(DST, exist_ok=True)
for name in os.listdir(SRC):
    src_path = os.path.join(SRC, name)
    if not os.path.isdir(src_path):
        continue
    dst_path = os.path.join(DST, name)
    if os.path.lexists(dst_path):
        skipped.append(name)
        continue
    os.symlink(to_msys2(src_path), dst_path, target_is_directory=True)
    created.append(name)

print(f"created={len(created)} skipped={len(skipped)}")
if skipped:
    print("skipped:", ", ".join(skipped))
```

## 注意

- 已存在的 symlink **skip 不覆盖**。要重建先手动删旧 link。
- target 用 msys2 格式（`/c/users/...`），匹配现有 symlink 格式。
- 跑前确认 `.cc-switch\skills\` 是当前 skill 源（应为 142 个子目录）。
- Windows 跑 `os.symlink` 需开发者模式或管理员权限；已建过说明环境支持。
