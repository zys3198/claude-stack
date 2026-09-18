#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
cat > src/discount.py <<'EOF'
def new_user_discount():
    return 0.2
EOF
