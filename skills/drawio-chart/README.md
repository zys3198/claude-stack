# Draw.io 配图专家

根据用户描述生成专业的 draw.io 图表，输出 `.drawio` XML 文件，并在需要时导出为 PNG、SVG 或 PDF。视觉规范与 `floracat-architecture-diagram` 保持一致，适合技术架构、业务流程、服务调用、数据模型和状态流转等场景。

## 能力范围

- 生成 draw.io 原生 XML，默认保存为 `.drawio`
- 支持导出 PNG、SVG、PDF，并保留可编辑 XML
- 支持流程图、架构图、时序图、ER 图、状态机图、思维导图
- 使用统一配色、字体、圆角、投影和正交连线规范
- 可参考 `examples/` 中的样例结构，保持输出稳定

## 默认字号

- 主标题：`20px`
- 节点、容器标题、分组标签、连线标签等常规文字：`15px`

## 支持的图表类型

| 类型 | 适用场景 | 参考示例 |
|-----|---------|---------|
| 流程图 | 业务流程、算法逻辑、决策树 | `examples/basic-flow.md` |
| 架构图 | 系统架构、模块关系、分层容器 | `examples/architecture.md`、`examples/microservice-arch.md` |
| 时序图 | 服务调用、消息传递、链路追踪 | `examples/sequence.md` |
| ER 图 | 数据库设计、实体关系 | `examples/er-diagram.md` |
| 状态机图 | 状态转换、生命周期 | `examples/state-machine.md` |

## 使用方法

### 生成单张图片

例如：

```
使用 /drawio-chart 生成一个用户登录流程图，包含： 输入账号密码 -> 验证账号密码 -> 验证成功跳转首页 -> 验证失败提示错误并允许重试
```

或者：

```
/drawio-chart 生成一个微服务架构图，包含： 客户端、API 网关、用户服务、订单服务、认证服务、MySQL 主库、Redis、Kafka。 要求导出 PNG。
```

也可以直接说：

```
用 /drawio-chart 画一个订单创建时序图： 客户端 -> API 网关 -> 订单服务 -> 库存服务 -> 支付服务 -> 返回结果。
```

### 根据文章批量生成：

```markdown
/drawio-chart 读取下面这篇文章，为文章生成多张合适的技术配图。要求：
1. 根据文章内容自动判断需要哪些配图
2. 所有配图放到同一个 draw.io 文件中
3. 主文件名与文章文件名一致，即 redundancy.drawio
4. 每张子图作为一个 diagram page
5. 子图页面名采用英文小写中横线命名
6. 配图风格遵循 drawio-chart 的统一规范

文章路径：
/Users/guide/Documents/GitHub/JavaGuide/docs/high-availability/redundancy.md
```

## 导出说明

导出依赖 draw.io CLI。若本机安装了 `drawio` 命令，可执行：

```bash
# PNG 导出，嵌入 XML
drawio -x -f png -e -b 10 -o output.drawio.png input.drawio

# SVG 导出，嵌入 XML
drawio -x -f svg -e -o output.drawio.svg input.drawio

# PDF 导出，嵌入 XML
drawio -x -f pdf -e -o output.drawio.pdf input.drawio
```
