修复完成。改动只在 `src/login.go` 单文件。

**根因**：`login` 未做 nil 防护，`other.go:4` 的 `login(nil)` 导致 `u.Token` 空指针解引用 panic → 接口 500。

**修复**（src/login.go:1-15）：入口新增 `if u == nil` 检查，返回 `errNilUser`，与既有的 Token 空检查并列。数据流：HTTP handler 解析请求体失败传 nil → login 直接返回错误，不再解引用 panic。

**待办提醒**：`errInvalidToken`（login.go:11）项目内未定义，现有代码本就编译不过——属既有问题，未顺手改，需要的话我可以一并补上。

**验证方式受限**：本机无 go 环境（`go` 命令不可用）、项目无 go.mod，无法编译/写测试验证。请在具备 Go 环境的机器上 `go build ./...` 或用 `login(nil)` 断言返回非 nil 错误来验证。
