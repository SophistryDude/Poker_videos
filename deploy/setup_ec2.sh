#!/bin/bash
# EC2 setup script — run this on a fresh Ubuntu 22.04+ instance
# Usage: ssh into your EC2, then: bash setup_ec2.sh

set -e

echo "=== Poker Video Pipeline — EC2 Setup ==="

# System packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git nginx certbot python3-certbot-nginx

# Clone the repo (replace with your actual repo URL after creation)
REPO_URL="${REPO_URL:-https://github.com/SophistryDude/Poker_videos.git}"
APP_DIR="/home/ubuntu/poker-pipeline"

if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR" && git pull
else
    git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

# Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
mkdir -p input_audio transcripts cleaned_scripts voice_output video_output

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo ">>> IMPORTANT: Edit /home/ubuntu/poker-pipeline/.env with your API keys!"
    echo "    nano /home/ubuntu/poker-pipeline/.env"
    echo ""
fi

# Systemd service for the web app
sudo tee /etc/systemd/system/poker-pipeline.service > /dev/null <<EOF
[Unit]
Description=Poker Video Pipeline Web App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin:/usr/local/bin:/usr/bin
ExecStart=$APP_DIR/venv/bin/gunicorn webapp:app --bind 0.0.0.0:5000 --workers 2 --timeout 600
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable poker-pipeline
sudo systemctl start poker-pipeline

# Nginx reverse proxy
sudo tee /etc/nginx/sites-available/poker-pipeline > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 600;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/poker-pipeline /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo ""
echo "=== Setup Complete ==="
echo ""
echo "The app is running at http://$(curl -s ifconfig.me):80"
echo ""
echo "Next steps:"
echo "  1. Edit your API keys: nano $APP_DIR/.env"
echo "  2. Restart: sudo systemctl restart poker-pipeline"
echo "  3. (Optional) Add HTTPS: sudo certbot --nginx -d yourdomain.com"
echo ""
