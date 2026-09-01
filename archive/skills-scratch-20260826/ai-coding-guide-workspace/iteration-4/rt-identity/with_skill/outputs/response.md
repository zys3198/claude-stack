**分类**：流程/元层设计咨询（非编码执行，讨论 `ai-coding-guide` 自身角色边界）。

**主路径**：`ai-coding-guide` 应定位为**单一入口编排器**，只做「任务识别 → 路由分诊 → 组合调用」三件事；生态地图、质量闸门、学习陪跑拆为独立 skill/模块，由它按需触发，而非自己兼任。

**组合**：
- 开工路由：核心职责，内置分诊表，输出「分类/主路径/组合/闸门/下一步」契约。
- 生态地图：独立为 `ecosystem-map` 或融入 `ai-coding-guide` 的只读知识层，供路由时查询，不由它维护。
- 质量闸门：由 `quality-gate` / `verification-before-completion` 等 skill 承担，`ai-coding-guide` 在路由时注明需经过哪些闸门。
- 学习陪跑：由 `learning-personas` / `learning-guide` 承担，`ai-coding-guide` 识别学习信号后转交。

**闸门**：
- 不扩大 `ai-coding-guide` 职责范围：它不应直接改代码、不应直接教学、不应直接跑验收。
- 输出必须明确：谁是执行者、谁是检查者、谁负责学习陪伴。
- 遇到职责重叠时，以「入口归一，能力外拆」为准。

**下一步**：确认这一定位后，可将四项能力写成 `ai-coding-guide` 的契约模板：它只决定「交给谁」，不替别人做事。是否需要我据此草拟一份 `ai-coding-guide` 角色契约文档？
