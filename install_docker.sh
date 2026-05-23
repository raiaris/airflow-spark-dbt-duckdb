#!/usr/bin/env bash
set -e

sudo systemctl stop docker || true
sudo apt-get remove -y docker.io docker-compose-v2 containerd runc || true
sudo apt-get autoremove -y
sudo rm -rf /var/lib/docker /var/lib/containerd /etc/docker || true
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo rm -f /etc/apt/sources.list.d/docker.list /etc/apt/keyrings/docker.gpg || true
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
echo "DOCKER_INSTALL_DONE"
