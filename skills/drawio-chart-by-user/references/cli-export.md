# CLI 导出命令（原 SKILL.md §四）

> 下沉自 SKILL.md §四（2026-09-08 渐进披露改造）。导出模式的执行细节；导出失败与 CLI 缺失的兜底见入口 SKILL.md 操作流程。

## 四、CLI 导出命令

### 检测命令

```bash
# macOS/Linux
which drawio

# Windows
where drawio
```

### 导出命令

```bash
# PNG 导出（嵌入 XML）
drawio -x -f png -e -b 10 -o output.drawio.png input.drawio

# SVG 导出（嵌入 XML）
drawio -x -f svg -e -o output.drawio.svg input.drawio

# PDF 导出（嵌入 XML）
drawio -x -f pdf -e -o output.drawio.pdf input.drawio
```

### 打开文件

```bash
# macOS
open filename.drawio

# Linux
xdg-open filename.drawio

# Windows
start filename.drawio
```
