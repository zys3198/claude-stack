修复完成。

## 根因

`other.go:4` 的 `startServer()` 调用了 `login(nil)`，而 `login` 原实现第一行就解引用 `u.Token`（login.go:3）——传 nil 时触发空指针 panic，HTTP 层捕获后返回 500。这解释了"偶发"：只有当请求路径把 nil 的 `*User` 传进来时才崩。

## 改动（2 个文件）

- **src/login.go**：加 nil 守卫，`u == nil || u.Token == ""`（Go 的 `||` 短路，nil 时不会解引用）统一返回 `errInvalidToken`。
- **src/login.go**：补了 `var errInvalidToken = errors.New("invalid token")`。⚠️ 这是**额外判断**：该符号在仓库 3 个文件里都只被引用、没有定义，原代码实际无法编译；不补上 nil 分支就没法返回错误。如果你真实代码库里已有定义（这只是裁剪后的复现），删掉我这一行即可。

## 验证

**未运行**：本机无 Go 工具链（`go` 不在 PATH），我无法执行 `go test`，不能谎称已验证。

验证方式（有 Go 环境的机器上，2 分钟内）：
```
cd src && go test -run TestLogin ./...
```
`TestLoginNilUser` 是回归测试——修复前 `login(nil)` 会 panic，修复后返回错误；另两条覆盖空 token 拒绝、有效 token 通过。
