#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
cat > src/login.go <<'EOF'
package main

func login(u *User) error {
    if u.Token == "" {
        return errInvalidToken
    }
    return checkSession(u)
}
EOF
cat > src/other.go <<'EOF'
package main

func startServer() {
    _ = login(&User{})
    _ = login(nil)
}
EOF
cat > src/types.go <<'EOF'
package main

type User struct {
    Name  string
    Token string
}

func checkSession(u *User) error { return nil }
EOF
