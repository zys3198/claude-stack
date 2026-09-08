# XML 结构规范与模板（原 SKILL.md §二 + §六）

> 下沉自 SKILL.md §二、§六（2026-09-08 渐进披露改造）。生成 XML 前查阅；配色查 color-tokens.md，布局查 layout-principles.md（同目录）。

## 二、XML 结构规范

### 文本标签规则

- `mxCell` 的 `value` 中禁止使用 HTML 标签，例如 `&lt;b&gt;`、`&lt;/b&gt;`、`&lt;br&gt;`、`<b>`、`<br>`。
- 需要换行时使用 XML 换行实体 `&#xa;`，不要使用 `<br>` 或 `&lt;br&gt;`。
- 需要强调整段文字时使用样式字段（如 `fontStyle=1`）或拆成独立文本节点，不要在 `value` 中嵌入 HTML。
- 文本节点和图形节点默认使用纯文本渲染，样式中优先设置 `html=0`；除非用户明确要求并确认渲染链支持 HTML，否则不要使用 `html=1`。
- 生成或修改 `.drawio` 后，必须检查文件中是否残留 HTML 标签，重点搜索 `&lt;`、`<b>`、`<br>`。

### 连线标签规则

- 短连接线不要放长标签；如果两个节点距离较近，连线 `value` 应留空，或只放“是 / 否 / 成功 / 失败”这类 1-2 个词。
- 分类说明、原因说明、动作说明优先写进目标节点或旁注节点，不要压在连接线上。
- 连线标签不得覆盖箭头主体。生成或修改流程图后，要重点检查短横线、短竖线、菱形节点左右出口处的标签。

### 基础模板

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2025-01-01T00:00:00.000Z" agent="drawio-chart" version="24.0.0">
  <diagram name="Page-1" id="diagram-id">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0" background="#F8FAFC">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 图表内容 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 多页文件结构（单文件多图模式）

一个 `.drawio` 文件可含多个 `<diagram>` 页，用于文章配图等"多图装一个文件"场景。调用方（如 drawio-article-illustration）声明"单文件多页模式"时启用，否则按上文单页生成。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2025-01-01T00:00:00.000Z" agent="drawio-chart" version="24.0.0">
  <diagram name="thread-lifecycle" id="d1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0" background="#F8FAFC">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 第 1 张图内容 -->
      </root>
    </mxGraphModel>
  </diagram>
  <diagram name="process-vs-thread" id="d2">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0" background="#F8FAFC">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 第 2 张图内容（mxCell id 全局唯一，不可与 d1 重复） -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

要点：
- 每个 `<diagram>` 独立 `id`（全局唯一，不可跨页重复）；`name` 即 draw.io 左下角页签名。
- `name` 用英文 kebab-case（由调用方提供，如 `thread-lifecycle`、`context-switch`）。
- 各页 `mxCell` 的 `id` 必须在整个 `<mxfile>` 内全局唯一（draw.io 按文件去重，不按页）。
- 配色、布局、字体、模板规则与单页一致，查 `color-tokens.md` / `layout-principles.md`（同目录）。

### 标题样式模板

图表主标题必须使用 `fontSize=20`。除主标题外，节点、容器标题、分组标签、连线标签等常规文字统一使用 `fontSize=15`。

```xml
<mxCell id="title" value="图表标题" style="text;html=0;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=20;fontStyle=1;fontColor=#2D3748;" vertex="1" parent="1">
  <mxGeometry x="260" y="20" width="300" height="40" as="geometry"/>
</mxCell>
```

### 节点样式模板

以下模板中的 `{语义类别}` 对应配色表中的行，直接替换 `fillColor`/`fontColor` 即可。

#### 核心语义节点

**通用节点模板**：复制以下 XML，将 `fillColor`/`fontColor` 替换为 §一配色表中对应类别的值。

```xml
<mxCell id="node-id" value="节点名称" style="rounded=1;whiteSpace=wrap;fillColor={类别填充色};strokeColor=none;fontColor={类别文字色};fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

**示例 — Gateway 节点**（`fillColor=#005D7B`, `fontColor=#FFFFFF`）：

```xml
<mxCell id="node-id" value="API 网关" style="rounded=1;whiteSpace=wrap;fillColor=#005D7B;strokeColor=none;fontColor=#FFFFFF;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

其余语义类别（Business Service / Infrastructure Service / Client/Frontend / External）复用通用模板，颜色查 §一核心语义配色表。

#### 数据存储节点

**通用数据存储节点**：DB/对象存储用 `shape=cylinder3`，缓存/队列/搜索用 `shape=rounded=1`。颜色查 §一数据存储配色表。

**示例 — Primary DB（圆柱 + 业务橙）：**
```xml
<mxCell id="node-id" value="MySQL 主库" style="shape=cylinder3;whiteSpace=wrap;fillColor=#E99151;strokeColor=none;fontColor=#FFFFFF;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="80" as="geometry"/>
</mxCell>
```

**示例 — Cache（矩形 + 缓存绿）：**
```xml
<mxCell id="node-id" value="Redis 缓存" style="rounded=1;whiteSpace=wrap;fillColor=#4CA497;strokeColor=none;fontColor=#FFFFFF;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

其余存储类型（Replica DB / Message Queue / Search Engine / Object Storage）复用上述模板，颜色查 §一配色表。

#### 状态节点

复用通用节点模板，`fillColor` 按状态语义选择。示例：

**Success 节点（正常流，`#4CA497`）：**
```xml
<mxCell id="node-id" value="处理成功" style="rounded=1;whiteSpace=wrap;fillColor=#4CA497;strokeColor=none;fontColor=#FFFFFF;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

**Alert/Danger 节点（异常流，`#DC2626`）：**
```xml
<mxCell id="node-id" value="处理失败" style="rounded=1;whiteSpace=wrap;fillColor=#DC2626;strokeColor=none;fontColor=#FFFFFF;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="140" height="60" as="geometry"/>
</mxCell>
```

Warning / Info 颜色查 §一状态配色表，其余模板不变。

**菱形判断节点：**
```xml
<mxCell id="decision-id" value="条件?" style="rhombus;whiteSpace=wrap;fillColor=#005D7B;strokeColor=none;fontColor=#FFFFFF;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="200" width="120" height="80" as="geometry"/>
</mxCell>
```

**分组容器（Group/Infra）：**
```xml
<mxCell id="group-id" value="服务集群" style="swimlane;whiteSpace=wrap;fillColor=none;strokeColor=#005D7B;dashed=1;strokeWidth=2;fontColor=#2D3748;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;" vertex="1" parent="1">
  <mxGeometry x="50" y="50" width="400" height="250" as="geometry"/>
</mxCell>
```

### 连线样式模板

**标准连线（带标签）：**
```xml
<mxCell id="edge-id" value="HTTP" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;strokeWidth=2;strokeColor=#94A3B8;labelBackgroundColor=#F8FAFC;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;fontColor=#64748B;" edge="1" source="source-id" target="target-id" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**无标签连线：**
```xml
<mxCell id="edge-id" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;strokeWidth=2;strokeColor=#94A3B8;" edge="1" source="source-id" target="target-id" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**虚线连接（异步/间接）：**
```xml
<mxCell id="edge-id" value="异步消息" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;dashed=1;strokeWidth=2;strokeColor=#94A3B8;labelBackgroundColor=#F8FAFC;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=15;fontColor=#64748B;" edge="1" source="source-id" target="target-id" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

#### 状态机专用模板

**起点（实心圆）：**
```xml
<mxCell id="sm-start" value="" style="ellipse;fillColor=#2D3748;strokeColor=none;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="30" height="30" as="geometry"/>
</mxCell>
```

**终点（双圆）：**
```xml
<mxCell id="sm-end" value="" style="ellipse;fillColor=#2D3748;strokeColor=#2D3748;strokeWidth=3;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;" vertex="1" parent="1">
  <mxGeometry x="100" y="400" width="30" height="30" as="geometry"/>
</mxCell>
```

**状态节点（圆角矩形）：** 复用通用节点模板，`fillColor` 按状态语义选择（正常=#4CA497，警告=#E99151，异常=#DC2626）。

**状态转换（含回环）：** 状态机中"取消→回到待支付"等回环箭头，用 `curved=1` 弯曲避开正向箭头：
```xml
<mxCell id="sm-trans" value="取消" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;strokeWidth=2;strokeColor=#94A3B8;curved=1;labelBackgroundColor=#F8FAFC;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=13;fontColor=#64748B;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;" edge="1" source="source-id" target="target-id" parent="1">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="250" y="350" />
      <mxPoint x="50" y="350" />
    </Array>
  </mxGeometry>
</mxCell>
```

#### 时序图专用模板

**生命线头部（参与者框）：**
```xml
<mxCell id="seq-part" value="服务名" style="rounded=1;whiteSpace=wrap;fillColor=#005D7B;strokeColor=none;fontColor=#FFFFFF;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=14;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="30" width="120" height="40" as="geometry"/>
</mxCell>
```

**生命线（虚线竖线）：**
```xml
<mxCell id="seq-line" value="" style="endArrow=none;dashed=1;strokeWidth=1;strokeColor=#94A3B8;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="160" y="70" as="sourcePoint" />
    <mxPoint x="160" y="500" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

**同步消息（实线箭头）：**
```xml
<mxCell id="seq-msg" value="请求" style="endArrow=block;endFill=1;strokeWidth=2;strokeColor=#94A3B8;labelBackgroundColor=#F8FAFC;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=13;fontColor=#64748B;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="160" y="120" as="sourcePoint" />
    <mxPoint x="400" y="120" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

**返回消息（虚线箭头）：**
```xml
<mxCell id="seq-ret" value="响应" style="endArrow=block;endFill=0;dashed=1;strokeWidth=2;strokeColor=#94A3B8;labelBackgroundColor=#F8FAFC;fontFamily=system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif;fontSize=13;fontColor=#64748B;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="400" y="150" as="sourcePoint" />
    <mxPoint x="160" y="150" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

---

## XML 注意事项（原 §六）

1. **ID 唯一性**：每个 `mxCell` 必须有唯一 `id`
2. **XML 转义**：属性值中的特殊字符必须转义（`&amp;` `&lt;` `&gt;` `&quot;`）
3. **注释禁止**：XML 注释中不能使用 `--`（双连字符）
4. **坐标系统**：使用网格对齐，以 10px 为单位
5. **入口点**：使用 `entryX/entryY` 精确控制连线入口位置（0-1 之间）
