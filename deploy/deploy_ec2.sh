#!/bin/bash
# Deploy poker app to existing EC2 k0s cluster
# Usage: bash deploy/deploy_ec2.sh

set -e

PEM="c:/Users/nicho/OneDrive/Documents/GitHub/data-acq-functional-SophistryDude/Securities_prediction_model/docs/other/security/trading-db-key.pem"
HOST="ubuntu@3.140.78.15"
SSH="ssh -i $PEM -o StrictHostKeyChecking=no $HOST"
SCP="scp -i $PEM -o StrictHostKeyChecking=no"
REMOTE_DIR="/home/ubuntu/poker-app"

echo "=== Deploying Poker App to EC2 ==="

# 1. Create remote directory
echo "[1/5] Setting up remote directory..."
$SSH "mkdir -p $REMOTE_DIR/poker_app/templates $REMOTE_DIR/poker_app/static $REMOTE_DIR/k8s"

# 2. Copy files
echo "[2/5] Copying files..."
$SCP Dockerfile "$HOST:$REMOTE_DIR/"
$SCP stake_move_model.py "$HOST:$REMOTE_DIR/"
$SCP leak_analysis.py "$HOST:$REMOTE_DIR/"
$SCP generate_profiles.py "$HOST:$REMOTE_DIR/"
$SCP synthetic_players_100k.csv "$HOST:$REMOTE_DIR/"
$SCP requirements.txt "$HOST:$REMOTE_DIR/"
$SCP poker_app/app.py "$HOST:$REMOTE_DIR/poker_app/"
$SCP poker_app/templates/index.html "$HOST:$REMOTE_DIR/poker_app/templates/"
$SCP k8s/namespace.yaml "$HOST:$REMOTE_DIR/k8s/"
$SCP k8s/deployment.yaml "$HOST:$REMOTE_DIR/k8s/"
$SCP k8s/service.yaml "$HOST:$REMOTE_DIR/k8s/"

# 3. Build Docker image
echo "[3/5] Building Docker image..."
$SSH "cd $REMOTE_DIR && sudo docker build -t poker-app:latest . 2>&1 | tail -5"

# 4. Import image into k0s containerd
echo "[4/5] Importing image to k0s..."
$SSH "sudo docker save poker-app:latest | sudo k0s ctr images import - 2>&1"

# 5. Deploy to k8s
echo "[5/5] Deploying to k8s..."
$SSH "sudo k0s kubectl apply -f $REMOTE_DIR/k8s/namespace.yaml"
$SSH "sudo k0s kubectl apply -f $REMOTE_DIR/k8s/deployment.yaml"
$SSH "sudo k0s kubectl apply -f $REMOTE_DIR/k8s/service.yaml"

# Restart pod to pick up new image
$SSH "sudo k0s kubectl delete pods -n poker-system -l app=poker-app --force 2>/dev/null || true"

echo ""
echo "Waiting for pod to start..."
sleep 15
$SSH "sudo k0s kubectl get pods -n poker-system"

echo ""
echo "=== Deploy Complete ==="
echo "App is on NodePort 30501"
echo "Add nginx config to expose it at poker.alphabreak.vip"
echo ""
