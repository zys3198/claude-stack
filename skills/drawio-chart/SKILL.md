---
name: drawio-chart
description: Draw.io 配图专家：根据需求生成专业的 draw.io 图表，支持流程图、架构图、时序图、ER图等，可导出为 PNG/SVG/PDF 格式。视觉风格与 floracat-architecture-diagram 保持一致。触发词：画图、流程图、架构图、时序图、drawio、配图、做个图、draw.io、状态机图、ER图、思维导图。
---

# Draw.io 配图协议

## 工作模式

| 场景 | 模式 | 说明 |
|-----|------|------|
| 用户描述图表需求 | **生成模式** | 根据描述生成 draw.io XML 格式图表 |
| 指定导出格式 | **导出模式** | 将生成的 .drawio 文件导出为 PNG/SVG/PDF |

## 支持的图表类型

| 类型 | 适用场景 | 关键元素 |
|-----|---------|---------|
| **流程图** | 业务流程、算法逻辑、决策树 | 圆角矩形、菱形判断、箭头连线 |
| **架构图** | 系统架构、模块关系 | 分层容器、组件框、数据流向 |
| **时序图** | 服务调用、消息传递 | 生命线、消息箭头、激活条 |
| **ER图** | 数据库设计、实体关系 | 圆柱体、关系线、属性框 |
| **状态机图** | 状态转换、生命周期 | 圆形/圆角矩形、转换箭头 |
| **思维导图** | 知识结构、概念梳理 | 中心节点、分支节点、层级关系 |

---

## 一、通用技术架构绘图规范

### 配色系统

#### 核心语义类别

| 语义类别 | 填充色 | 文字色 | 边框色 | 用途 |
|---------|-------|--------|--------|------|
| **Gateway/Entry** | `#005D7B` | `#FFFFFF` | `none` | API网关、负载均衡、入口点 |
| **Business Service** | `#E99151` | `#FFFFFF` | `none` | 核心业务服务、领域服务 |
| **Infrastructure Service** | `#7C3AED` | `#FFFFFF` | `none` | 基础设施服务（认证、日志、监控） |
| **Client/Frontend** | `#0891B2` | `#FFFFFF` | `none` | 前端、用户、客户端 |
| **External/3rd Party** | `#64748B` | `#FFFFFF` | `none` | 外部API、第三方服务 |

#### 数据存储类别

| 语义类别 | 填充色 | 文字色 | 边框色 | 用途 |
|---------|-------|--------|--------|------|
| **Primary DB** | `#E99151` | `#FFFFFF` | `none` | 主数据库、核心存储 |
| **Replica DB** | `#E4C189` | `#2D3748` | `none` | 从库、只读副本 |
| **Cache** | `#4CA497` | `#FFFFFF` | `none` | 缓存服务（Redis、Memcached） |
| **Message Queue** | `#4CA497` | `#FFFFFF` | `none` | 消息队列（Kafka、RabbitMQ） |
| **Search Engine** | `#0891B2` | `#FFFFFF` | `none` | 搜索引擎（Elasticsearch） |
| **Object Storage** | `#7C3AED` | `#FFFFFF` | `none` | 对象存储（S3、OSS） |

#### 状态类别

| 语义类别 | 填充色 | 文字色 | 边框色 | 用途 |
|---------|-------|--------|--------|------|
| **Success/Status** | `#4CA497` | `#FFFFFF` | `none` | 正常流、成功状态 |
| **Alert/Danger** | `#DC2626` | `#FFFFFF` | `none` | 异常流、错误状态 |
| **Warning/Retry** | `#E99151` | `#FFFFFF` | `none` | 重试、降级、熔断状态 |
| **Info/Neutral** | `#94A3B8` | `#FFFFFF` | `none` | 中性状态、待处理 |

#### 容器类别

| 语义类别 | 填充色 | 文字色 | 边框色 | 用途 |
|---------|-------|--------|--------|------|
| **Group/Infra** | `none` | `#2D3748` | `#005D7B` | 容器、网络、分组区域 |
| **Network Zone** | `#F8FAFC` | `#2D3748` | `#E2E8F0` | 网络分区、安全域 |

### 全局常量

| 属性 | 值 | 说明 |
|-----|-----|------|
| **Background** | `#F8FAFC` | 与 floracat 一致的画布背景 |
| **Font Family** | `system-ui, -apple-system, PingFang SC, Microsoft YaHei, sans-serif` | 系统字体栈，与 floracat 一致 |
| **Font Size (Title)** | `20` | 图表主标题文字大小 |
| **Font Size (Node)** | `15` | 节点内文字大小 |
| **Font Size (Edge Label)** | `15` | 连线标签文字大小 |
| **Shape** | `rounded=1` | 所有矩形开启圆角 |
| **Edge Style** | `edgeStyle=orthogonalEdgeStyle` | 正交连线（直角） |
| **Edge Width** | `strokeWidth=2` | 连线粗细 2px |
| **Edge Color** | `#94A3B8` | 与 floracat 箭头色一致 |
| **Label BG** | `labelBackgroundColor=#F8FAFC` | 连线文字背景与画布底色同步 |

### 高级设置

| 设置 | 值 | 说明 |
|-----|-----|------|
| **Shadow** | `shadow=1` | 启用投影（draw.io 内置轻阴影，模拟 floracat 的 feDropShadow 效果） |
| **Sketch Mode** | 禁用 | 保持专业感，除非用户明确要求草图风格 |

---

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
- 配色、布局、字体、模板规则与单页一致，查 §一 / §十。

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

## 三、操作流程

### 生成模式

#### Step 1: 需求解析 → 图表类型判定

**输入**：用户自然语言描述
**输出**：图表类型 + 节点清单 + 关系列表

**图表类型决策表**（按关键词匹配）：

| 用户描述中的信号 | 图表类型 | 主方向 |
|----------------|---------|-------|
| 流程、步骤、→、判断、分支、循环 | 流程图 | 垂直 ↓ |
| 架构、分层、模块、拓扑、组件 | 架构图 | 水平 → |
| 调用、消息、交互、顺序、谁先谁后 | 时序图 | 垂直 ↓ |
| 状态、转换、生命周期、 CLOSED/OPEN | 状态机图 | 水平 → 或径向 |
| 实体、关系、数据库、ER、表结构 | ER图 | 水平 → |
| 知识、脑图、思维导图、概念 | 思维导图 | 径向 |
| 不确定或混合信号 | 🔴 STOP | 列出候选类型，等用户确认 |

**失败处理**：用户描述模糊（"画个图"无具体内容）→ 列出上表 6 种类型及各 1 个典型场景，等用户选择后再继续。

#### Step 2: 确定布局参数

**输入**：图表类型 + 节点数量 N
**输出**：主方向、画布宽高、节点坐标分配方案

| N 范围 | 布局策略 | 画布参考 |
|-------|---------|---------|
| ≤ 6 | 单行/单列，间距 60px | 紧凑（≤ 800 宽） |
| 7-15 | 多行/多列网格，间距 60-80px | 中等（800-1100） |
| 16-30 | 分组容器或子图拆分 | 宽幅（1100-1400） |
| > 30 | 🔴 STOP — 要求用户拆分为多张图 | — |

画布尺寸公式：`pageWidth = 最右节点右边缘 + 40`，`pageHeight = 最底节点底边缘 + 40`。不要用固定大画布。

**🔴 CHECKPOINT — N > 6 或复杂图表时**：展示布局方案（主方向、画布宽高、行数×列数、预估节点坐标范围）给用户确认，通过后再进 Step 3。≤ 6 节点的简单图可跳过此检查点直接生成。

#### Step 3: 生成 XML

按 §二 模板 + §一 配色 + §十 布局原则生成 draw.io XML。

节点文字规则：每节点 `value` ≤ 2 行，每行 ≤ 8 个中文字符。放不下就缩短或拆节点，不写完整句子。

#### 🔴 STOP — 生成前检查清单

逐项确认，全部 ✅ 才继续：

- [ ] 图表类型与用户描述匹配（不确定则回 Step 1 询问）
- [ ] 全图主方向一致（同一张图内不混用横竖方向）
- [ ] 节点坐标无重叠（逐节点检查矩形区间不相交）
- [ ] 节点文字 ≤ 2 行 × 8 字
- [ ] 连线标签 ≤ 4 字，短边（< 60px）不放标签
- [ ] 画布边缘留白 ≤ 50px（超出则缩小 pageWidth/pageHeight）

任一项 ❌ → 调整后重新检查。

#### Step 4: 写入文件

保存为 `.drawio` 文件。目标路径文件已存在时 🔴 STOP — 展示路径，等用户确认覆盖或换路径。

#### Step 5: XML 校验

写入后必须检查：
- 每个 mxCell id 唯一（扫描所有 `id="` 属性）
- 无 HTML 标签残留（搜索 `<b>` `<br>` `<div>`）
- source/target 引用的 id 均存在（每条 edge 的 source/target 在节点列表中能找到）

校验失败 → 修复后重写，不交付损坏文件。

#### Step 6: 打开预览

```bash
# Windows
start "" "path/to/file.drawio"
# macOS
open "path/to/file.drawio"
```

用户预览后不满意布局 → 根据反馈调整坐标，回到 Step 3 重新生成。

### 导出模式

1. **生成 .drawio 文件**：先生成原生格式
2. **检测 draw.io CLI**：`where drawio`（Windows）/ `which drawio`（macOS/Linux）
3. **CLI 不存在 → 🔴 STOP**：告知用户只生成了 .drawio，附导出命令和安装指引
4. **🔴 CHECKPOINT — 展示导出命令和格式**，等用户确认再执行导出
5. **执行导出**：使用 CLI 导出为指定格式（PNG/SVG/PDF）
6. **导出失败 → 保留 .drawio**：告知用户导出命令和安装指引，不删除源文件
7. **返回结果**：告知用户导出文件路径，默认保留 .drawio 源文件（用户可删除）

---

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

---

## 五、文件命名规范

| 场景 | 命名格式 | 示例 |
|-----|---------|------|
| 流程图 | `{name}-flow.drawio` | `login-flow.drawio` |
| 架构图 | `{name}-arch.drawio` | `system-arch.drawio` |
| 时序图 | `{name}-seq.drawio` | `api-call-seq.drawio` |
| ER图 | `{name}-er.drawio` | `user-db-er.drawio` |
| 导出 PNG | `{name}.drawio.png` | `login-flow.drawio.png` |
| 导出 SVG | `{name}.drawio.svg` | `system-arch.drawio.svg` |
| 导出 PDF | `{name}.drawio.pdf` | `api-doc.drawio.pdf` |

---

## 六、XML 注意事项

1. **ID 唯一性**：每个 `mxCell` 必须有唯一 `id`
2. **XML 转义**：属性值中的特殊字符必须转义（`&amp;` `&lt;` `&gt;` `&quot;`）
3. **注释禁止**：XML 注释中不能使用 `--`（双连字符）
4. **坐标系统**：使用网格对齐，以 10px 为单位
5. **入口点**：使用 `entryX/entryY` 精确控制连线入口位置（0-1 之间）

---

## 七、使用示例

```text
# 生成流程图
请生成一个用户登录流程的 draw.io 图表，包含：输入账号密码 -> 验证 -> 成功/失败分支

# 生成架构图并导出 PNG
生成一个微服务架构图，包含网关、服务层、数据层，导出为 PNG 格式

# 生成时序图
生成一个订单创建的时序图，展示客户端、网关、订单服务、库存服务的交互
```

---

## 八、失败模式处理（if-then 三段式）

| # | 场景 | 触发条件 | 一线修复 | 仍失败兜底 |
|---|------|---------|---------|-----------|
| 1 | 用户需求模糊 | 无法判断图表类型 | 列出 6 种类型及各 1 个典型场景，等用户选择 | 降级为通用架构图 |
| 2 | 不支持的图表类型 | 用户要求甘特图/热力图等 | 明确告知不支持，推荐最接近的类型 | 告知使用专业工具 |
| 3 | 节点过多 | > 30 个节点 | 拆分为多张图或用分组容器 | 按模块拆成子图，每张 ≤ 15 节点 |
| 4 | 用户要求 HTML 节点 | value 中含 `<b>` `<br>` 等 | 拒绝并引导：用 `&#xa;` 换行、`fontStyle=1` 加粗 | 如用户坚持，设置 `html=1` 并标注渲染风险 |
| 5 | draw.io CLI 未安装 | `where drawio` / `which drawio` 失败 | 只生成 .drawio 文件 | 告知导出命令和安装指引 |
| 6 | 导出失败 | drawio 命令返回非零 | 重试一次 | 保留 .drawio 源文件，不自动删除 |
| 7 | XML 语法错误 | 生成后解析报错 | 检查转义字符（`&amp;` `&lt;`）、属性引号 | 从模板重新生成该节点 |
| 8 | 节点重叠 | 坐标矩形区间相交 | 调整 y 坐标确保递增，间距 ≥ 40px | 重新按网格（10px 单位）分配坐标 |
| 9 | 文件写入失败 | 权限不足 | 写入 `%TEMP%`（Windows）/ `/tmp`（Unix） | 告知用户路径，手动保存 |
| 10 | 文件已存在 | 目标路径有同名文件 | 🔴 STOP — 展示路径，等用户确认覆盖或换路径 | 用户不确认则写入带时间戳的新文件名 |

---

## 九、不要做什么（反例清单）

| # | 反模式 | 正确做法 |
|---|--------|---------|
| 1 | 在 mxCell value 中使用 HTML 标签 | 用 `&#xa;` 换行，`fontStyle=1` 加粗 |
| 2 | 混用多种字体 | 全图统一使用系统字体栈 |
| 3 | 用纯黑（#000000）边框 | 边框使用语义类别色或 `strokeColor=none` |
| 4 | 连线标签覆盖箭头 | 短连线不放标签，或只放 1-2 个词 |
| 5 | 生成超大单文件（> 50 节点） | 超过 30 节点拆分为多页/多图 |
| 6 | 跳过 XML 校验直接交付 | 必须检查 id 唯一性和 HTML 残留 |
| 7 | 不确认直接覆盖已有 .drawio 文件 | 同名文件先询问用户 |
| 8 | 画布大面积留白 | 按 §十 原则压缩画布、填充布局 |
| 9 | 同一图内混用横竖方向（上半部分横排，下半部分竖排） | 全图统一主方向，分支方向一致 |
| 10 | 节点文字写成段落/长句 | 节点文字 ≤ 2 行，每行 ≤ 8 字，细节放旁注 |
| 11 | 节点或标签坐标重叠 | 生成后逐节点检查坐标区间是否冲突 |

---

## 十、布局设计原则

生成任何图表前，必须遵守以下四条布局原则。违反任一条即需调整布局后再生。

### 1. 紧凑不留白

- **画布尺寸 = 内容尺寸 + 最小边距（20-30px）**。不要用固定大画布（如 1169×827）只放 5 个节点。根据节点数量和布局方向反推 `pageWidth`/`pageHeight`。
- **行间距/列间距统一**：同行节点 y 坐标相同，同列节点 x 坐标相同，间距保持一致（60-90px，够 edge routing 即可）。
- **边缘到画布边界的留白 ≤ 50px**。如果最后一排节点底部距画布底边超过 50px，缩小 `pageHeight`。

### 2. 方向一致，不混排

- **全图确定一个主方向**：水平（左→右）或垂直（上→下）。所有主流节点沿主方向排列。
- **分支方向固定**：垂直主流的分支统一向右；水平主流的分支统一向下。不要上面分支向右、下面分支向左。
- **架构图的径向布局**是唯一例外（中心节点向四周辐射），但辐射方向应均匀对称，不偏一侧。

### 3. 文字极简

- **节点文字只放关键词**：名词或名词短语，不用完整句子。如用"上下文压缩"而非"Codex 的上下文压缩机制"。
- **每节点 ≤ 2 行文字，每行 ≤ 8 个中文字符**（或等长英文）。放不下就缩短或拆节点。
- **连线标签 ≤ 4 个字**："是/否"、"成功/失败"、"产品规格"等。解释性文字放目标节点或旁注文本节点。
- **旁注/注释用小字**（`fontSize=11-12`，`fontColor=#94A3B8`），不喧宾夺主。
- **配图是辅助理解的，不是重复文章内容**。文章已写的细节不要搬进图里。

### 4. 无重叠

- **生成前算坐标**：每个节点的 `(x, y, width, height)` 构成的矩形不能与任何其他节点的矩形相交。
- **正交连线需要空间**：节点之间的间距 ≥ 40px，给 orthogonalEdgeStyle 留路由空间。
- **连线标签不压箭头**：短边（< 60px）不放标签，或只放 1-2 字。
- **生成后目检**：在 draw.io 中打开确认无重叠，如有则调整坐标重写。

### 布局速查表

| 图表类型 | 推荐主方向 | 画布宽高比 | 典型间距 |
|---------|-----------|-----------|---------|
| 流程图（分支少） | 垂直 ↓ | 3:5 | 行间距 60-80px |
| 流程图（多分支） | 垂直 ↓，分支 → | 2:3 | 主流 70px，分支列偏移 200px+ |
| 架构图（分层） | 水平 → | 5:3 | 列间距 80-100px |
| 架构图（中心辐射） | 径向 | 4:3 | 节点到中心等距 |
| 对比图 | 水平 ←→ | 2:1 | 两栏间距 60-80px |
| 管道/流水线 | 水平 → | 5:1 | 级间距 40-60px |
| 时序图 | 垂直 ↓ | 3:5 | 生命线间距 150-200px |
| 状态机 | 径向/水平 | 因内容而定 | 状态间距 ≥ 100px |
