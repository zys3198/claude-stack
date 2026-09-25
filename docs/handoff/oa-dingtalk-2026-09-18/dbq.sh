#!/usr/bin/env bash
# 查询 dtsf 库 Flyway 历史尾部与失败迁移详情；密码从 deploy/.env 读取，不打印。
set -euo pipefail
cd "$(dirname "$0")/../../../../deploy" 2>/dev/null || true

ENV_FILE="C:/ZYS/Code/dtsf/.claude/worktrees/dingtalk-oa-finance/deploy/.env"
MYSQL_ROOT_PASSWORD="$(grep -m1 '^MYSQL_ROOT_PASSWORD=' "$ENV_FILE" | cut -d= -f2-)"

SQL="${1:-SELECT installed_rank,version,description,type,success,installed_on FROM dtsf.flyway_schema_history ORDER BY installed_rank DESC LIMIT 12;}"

docker exec -e MYSQL_PWD="$MYSQL_ROOT_PASSWORD" deploy-mysql-1 mysql -uroot --default-character-set=utf8mb4 --table -e "$SQL"
