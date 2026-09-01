核对通过，修复闭环。

## 修复结果

**根因**：`login()` 对 `*User` 直接解引用（`u.Token`），当上游传入 nil 指针（请求体解析失败 / 用户记录不存在）时触发 nil 指针 panic → 500。触发点是 `other.go:4` 的 `login(nil)`。

**改动**（仅 `src/login.go`，1 个文件）：
1. 入口加 nil 守卫，nil 时返回 `errInvalidUser`，不再解引用 → 消除 panic
2. 补上此前缺失的 `errInvalidToken` 定义（grep 确认原代码里 0 定义，属编译错误）
3. 新增 `errInvalidUser` 哨兵错误（命名可改，语义为"用户对象缺失"）

`other.go`、`types.go` 未动。修复后两条调用路径均走错误返回而非 panic：
- `login(&User{})` → `errInvalidToken`
- `login(nil)` → `errInvalidUser`

## 验证情况

- **静态核对通过**：login 全部调用方（仅 other.go 两处）已覆盖；新增符号均有定义、无幽灵代码；`errors` 导入有使用。
- **编译/运行验证受限**：本机没有 Go 工具链（`go version` 不可用），且这是无 `go.mod`/`main` 的代码片段，无法 `go build`/`go test`。逻辑极简（一个 nil 判断），我已逐路径推演，但"编译通过"这一条没有实测证据——如果你能提供 Go 环境，我可以补一个 `go test` 验证。

**下一步**：在 Go 环境里 `go test` 跑一下（建议加两条用例：`login(nil)` 不 panic 且返回错误、空 token 返回 `errInvalidToken`），确认后即可合入。
