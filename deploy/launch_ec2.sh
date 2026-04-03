#!/bin/bash
# Launch an EC2 instance using AWS CLI
# Prerequisites: aws configure (with your AWS credentials)
#
# This creates a t3.medium instance (good enough for Whisper base model)
# with 30GB storage, open ports 22 (SSH) and 80 (HTTP)

set -e

INSTANCE_NAME="poker-pipeline"
AMI_ID="ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS us-east-1 (change for your region)
INSTANCE_TYPE="t3.medium"       # 2 vCPU, 4GB RAM — bump to t3.large for Whisper medium/large
KEY_NAME="${KEY_NAME:-poker-pipeline-key}"
SECURITY_GROUP="poker-pipeline-sg"

echo "=== Launching EC2 for Poker Pipeline ==="

# Create key pair if it doesn't exist
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" &>/dev/null; then
    echo "Creating key pair: $KEY_NAME"
    aws ec2 create-key-pair --key-name "$KEY_NAME" --query 'KeyMaterial' --output text > "${KEY_NAME}.pem"
    chmod 400 "${KEY_NAME}.pem"
    echo "Key saved to ${KEY_NAME}.pem — KEEP THIS FILE SAFE"
fi

# Create security group if it doesn't exist
SG_ID=$(aws ec2 describe-security-groups --group-names "$SECURITY_GROUP" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)
if [ -z "$SG_ID" ] || [ "$SG_ID" = "None" ]; then
    echo "Creating security group: $SECURITY_GROUP"
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP" \
        --description "Poker Pipeline - SSH and HTTP" \
        --query 'GroupId' --output text)

    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 443 --cidr 0.0.0.0/0
fi
echo "Security group: $SG_ID"

# Launch instance
echo "Launching $INSTANCE_TYPE instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SG_ID" \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp3"}}]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' --output text)

echo "Instance ID: $INSTANCE_ID"
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID"

PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo ""
echo "=== EC2 Instance Ready ==="
echo ""
echo "  Instance ID: $INSTANCE_ID"
echo "  Public IP:   $PUBLIC_IP"
echo ""
echo "Connect with:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo ""
echo "Then run the setup script:"
echo "  REPO_URL=https://github.com/YOUR_USERNAME/Poker_videos.git bash deploy/setup_ec2.sh"
echo ""
echo "Your pipeline will be at: http://${PUBLIC_IP}"
echo ""
