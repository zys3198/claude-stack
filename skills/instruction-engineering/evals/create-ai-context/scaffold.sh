#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
cat > README.md <<'EOF'
# tiny-app
最小的 Go Web 服务示例，用于测试 AI 上下文工程。
- src/main.go: HTTP 入口
- src/db.go: 数据库连接
- src/handler.go: 业务 handler
EOF
cat > src/main.go <<'EOF'
package main
func main() { startServer() }
EOF
cat > src/db.go <<'EOF'
package main
func connect() error { return nil }
EOF
cat > src/handler.go <<'EOF'
package main
func handler() string { return "hello" }
EOF
