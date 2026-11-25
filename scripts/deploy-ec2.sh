#!/usr/bin/env bash
# PaperBroker — EC2 deploy runbook as a script (DESIGN.md §6.6).
#
# Run ON the box (Ubuntu 24.04) as root:
#   sudo ./scripts/deploy-ec2.sh https://github.com/<you>/paperbroker.git
#
# First run creates /etc/paperbroker/env with placeholder secrets and EXITS —
# edit that file (it is chmod 600), then run the script again to finish.

set -euo pipefail

REPO_URL="${1:?usage: deploy-ec2.sh <repo-url>}"
APP_DIR=/opt/paperbroker
APP_USER=paperbroker

echo "==> packages"
apt-get update -y
apt-get install -y nginx python3 python3-venv nodejs npm git

echo "==> app user + code"
id -u "$APP_USER" >/dev/null 2>&1 || useradd -m "$APP_USER"
mkdir -p "$APP_DIR"
chown "$APP_USER":"$APP_USER" "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR"
else
  sudo -u "$APP_USER" git -C "$APP_DIR" pull --ff-only
fi
mkdir -p "$APP_DIR/data"
chown "$APP_USER":"$APP_USER" "$APP_DIR/data"

echo "==> backend"
sudo -u "$APP_USER" bash -lc "cd $APP_DIR/backend && python3 -m venv .venv && .venv/bin/pip install -e ."

echo "==> frontend"
sudo -u "$APP_USER" bash -lc "cd $APP_DIR/frontend && npm ci --silent && npm run build --silent"

echo "==> secrets + config"
if [ ! -f /etc/paperbroker/env ]; then
  mkdir -p /etc/paperbroker
  cat >/etc/paperbroker/env <<'EOF'
PB_SESSION_SECRET=change-me-openssl-rand-hex-32
PB_DB_PATH=/opt/paperbroker/data/paperbroker.db
PB_STARTING_CASH=100000
PB_ADMIN_EMAILS=you@example.com
PB_ADMIN_PASSWORD=change-me
EOF
  chmod 600 /etc/paperbroker/env
  echo "    -> created /etc/paperbroker/env with placeholders."
  echo "    -> EDIT IT NOW (secrets + your admin email), then re-run this script."
  exit 0
fi

echo "==> seed (instruments + personas)"
chown "root:$APP_USER" /etc/paperbroker/env
chmod 640 /etc/paperbroker/env
sudo -u "$APP_USER" bash -lc "set -a; . /etc/paperbroker/env; cd $APP_DIR/backend && .venv/bin/python -m app.seed"

echo "==> systemd service"
cat >/etc/systemd/system/paperbroker-api.service <<EOF
[Unit]
Description=PaperBroker API
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR/backend
EnvironmentFile=/etc/paperbroker/env
ExecStart=$APP_DIR/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now paperbroker-api

echo "==> nginx (one origin: static + /api proxy)"
cat >/etc/nginx/sites-available/paperbroker <<EOF
server {
    listen 80;
    server_name _;
    root $APP_DIR/frontend/dist;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$remote_addr;
    }
    location / { try_files \$uri /index.html; }
}
EOF
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/paperbroker /etc/nginx/sites-enabled/paperbroker
systemctl enable --now nginx
systemctl reload nginx

echo "==> deploy complete. App: http://<this-instance-public-ip>/"
echo "    Persona logins: fresh@demo / tilted@demo / cooldown@demo (password demo1234)"
echo "    Before judging: re-run  sudo -u $APP_USER bash -c 'set -a; . /etc/paperbroker/env; cd $APP_DIR/backend && .venv/bin/python -m app.seed --personas-only'"
