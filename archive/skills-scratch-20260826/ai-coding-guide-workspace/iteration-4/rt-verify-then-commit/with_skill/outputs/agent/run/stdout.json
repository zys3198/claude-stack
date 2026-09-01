分类：横切收尾（bug fix 验证 → 提交/收尾）

主路径：先按运行时表面验证（有 app 可跑则用 `run`，否则跑相关 test/build/lint），再经 `superpowers:verification-before-completion` 组织证据，验证通过后进入手动 git 提交流程

组合：`run`（条件，有运行时表面时）+ `superpowers:verification-before-completion` + 可选 `code-review` / `mattpocock-skills:code-review` 做提交前轻量审查

闸门：1) 验证闸门——复现/相关 test、lint、build 通过或真实行为证据；2) 提交闸门——必须展示 `git status --short` + `git diff --cached --stat` 获用户确认后方可 commit

下一步：补齐缺口后即可执行；当前需确认：验证（要证明的行为、入口命令、验收信号）与提交（范围、是否 push/开 PR、目标分支）
