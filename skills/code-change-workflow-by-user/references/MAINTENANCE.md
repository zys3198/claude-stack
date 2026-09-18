# 维护说明

本文件给维护 code-change-workflow 的人（和未来会话）看。正文规则见上级 `SKILL.md`，变更记录见上级 `CHANGELOG.md`。

## 版本规则

- frontmatter `version` 与 CHANGELOG 同步，语义化版本：
  - patch：错字、措辞修正、不改变行为的整理。
  - minor：正文新增/收紧执行规则（如 1.1.0 加 Context→追问→执行环）。
  - major：改 `description` 触发边界、拆分或合并 skill、改输入输出契约。
- 每次改动后：CHANGELOG 记一条（来源、改了什么、验证证据、未验证项），安装台账 `C:\Users\zys31\.claude\installing\custom-setup.md` 追加登记。

## 改动流程

1. 先在实验目录做候选副本，不直接改正式 skill（实验规范见 `C:\ZYS\Code\lab-area\CLAUDE.md`）。
2. 改正文规则（minor）：静态核对 + 显式 `/code-change-workflow-by-user` 加载复验。
3. 改 description 触发边界（major 候选）：必须重跑触发验证（正/负向场景），只有显式加载证据时不得宣布自动触发生效。
4. 同步到正式目录后，新 CLI 会话显式加载一次，确认新规则可读。

## evals 怎么跑

- 位置：`evals/<case>/case.yaml`（schema_version "1.0"）；需要落盘文件的 case 配 `context.scaffold_script`（bash，在沙箱 cwd 执行）。判词用确定性 `regex` grader，pattern 贴 SKILL.md 原词。
- 官方 runner（CLI ≥ 2.1.269，2026-09-12 实测已开放，不再有 early-access gate）：

  ```bash
  cd ~/.claude/skills/code-change-workflow-by-user
  claude plugin eval . --scaffold --allow-tools Edit --ablation none --runs 1 --no-publish --trust-plugin
  ```

  - `--scaffold`：执行 case 自带 scaffold_script（作者代码，默认关）；`--allow-tools Edit`：Edit 属 gated 工具，case 的 allowed_tools 声明不够，运行时要再 grant；`--ablation none`：只跑插件臂，省一半；`--no-publish`：HTML 报告不出本机。
  - 调试单次：加 `--case <name> --runs 3 --keep-temp`（保留沙箱与 trace.jsonl，看完按 runner 提示删临时目录）。
- 旧 v1alpha1 布局（`evals/eval.yaml + evals/cases/*.yaml`）已废弃删除，存档在来源实验目录 `evals-legacy-archive/`；`add_dirs` 只授予对 case 目录的读权限、不复制文件，别用它放 fixture。
- 5 个 case：bug-fix（根因）、vague-feature（反问）、research-no-route（负向）、delivery-evidence（交付回执）、missing-acceptance（缺验收先问）。
- Haiku 单跑有措辞波动：先靠 prompt 点名术语原词稳定，再靠 `--runs 3` 抽验，不靠放宽判词凑绿。
- 生成物在 `evals/results/<时间戳>/`（aggregate-result.json + report.html），可随时重跑再生，重要结果自行归档到实验目录。

## 已知验证边界

- 显式加载：已验证（2026-09-12，新 CLI 会话读到全部新规则）。
- 自然语言自动触发：eval 沙箱内已验证（2026-09-12，全部 runner trace 中子会话第一个工具调用均为 Skill code-change-workflow-by-user）；headless `claude -p` 不注入 skill 清单，该载体下探针无效；交互式日常真实任务的肉眼抽检仍保留。
- 真实代码修改闭环：2026-09-12 用 runtime-test fixture 完成红→绿（过期 token 500→401），由主会话执行，非嵌套 skill 会话。

## 相关路径

- 安装台账：`C:\Users\zys31\.claude\installing\custom-setup.md`（### code-change-workflow-by-user 小节）。
- 来源实验：`C:\ZYS\Code\lab-area\exp\2026-09-11-claude-workflow-harness\`（VERIFICATION.md、FINDINGS-DISPOSITION.md、runtime-test/）。
