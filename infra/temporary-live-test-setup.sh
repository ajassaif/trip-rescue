#!/bin/bash
# Executed successfully on the approved temporary AWS host on 18 October 2026.
# Run as ubuntu from ~/trip-rescue. No credentials or keys belong in this file.
set -euo pipefail
cd /home/ubuntu/trip-rescue
test "$(id -un)" = ubuntu
test -f backend/requirements.lock
test -f patterns/tool_selection.py
sudo systemctl is-active --quiet trip-rescue-expiry.timer
sudo systemctl list-timers trip-rescue-expiry.timer --no-pager

python3.12 -m venv /home/ubuntu/decider-venv
/home/ubuntu/decider-venv/bin/python -m pip install --no-cache-dir --upgrade pip
# Official CPU recipe: avoid downloading CUDA runtime wheels.
/home/ubuntu/decider-venv/bin/python -m pip install --no-cache-dir torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
# Pin the official main revision reviewed on 2026-10-17.
/home/ubuntu/decider-venv/bin/python -m pip install --no-cache-dir 'strands-decider[cpu] @ git+https://github.com/strands-labs/strands-decider@930e6d5de16309be32579f5631a7369a3322140c'
python3.12 -m venv /home/ubuntu/api-venv
/home/ubuntu/api-venv/bin/python -m pip install --no-cache-dir -r backend/requirements.lock

sudo tee /etc/systemd/system/trip-rescue-decider.service >/dev/null <<'SERVICE'
[Unit]
Description=Temporary CPU Strands Decider (loopback only)
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/trip-rescue
Environment=OMP_NUM_THREADS=8
Environment=MKL_NUM_THREADS=8
Environment=TOKENIZERS_PARALLELISM=false
ExecStart=/home/ubuntu/decider-venv/bin/strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --device cpu --host 127.0.0.1 --port 8099 --strict-window --max-batch 1 --max-batch-tokens 4096
Restart=no
NoNewPrivileges=true
PrivateTmp=true
[Install]
WantedBy=multi-user.target
SERVICE

sudo tee /etc/systemd/system/trip-rescue-api.service >/dev/null <<'SERVICE'
[Unit]
Description=Temporary Trip Rescue FastAPI (loopback only)
After=network-online.target trip-rescue-decider.service
Wants=network-online.target
[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/trip-rescue
Environment=STRANDS_DECIDER_URL=http://127.0.0.1:8099
Environment=STRANDS_DECIDER_MODEL=strands-decider-2B-qwen3.5-v1-2610
Environment=BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
Environment=AWS_REGION=us-east-1
Environment=AWS_USE_INSTANCE_ROLE=true
Environment=DECIDER_CONFIDENCE_THRESHOLD=0.8
Environment=PROVIDER_TIMEOUT_SECONDS=60
ExecStart=/home/ubuntu/api-venv/bin/python -m uvicorn backend.app:app --host 127.0.0.1 --port 8100 --workers 1
Restart=no
NoNewPrivileges=true
PrivateTmp=true
[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable --now trip-rescue-decider.service trip-rescue-api.service
printf '%s\n' 'Services started; model download/loading may take minutes. This is not proof of readiness or live success.'
printf '%s\n' 'Inspect: sudo journalctl -u trip-rescue-decider -u trip-rescue-api --no-pager -n 80'
printf '%s\n' 'Readiness: curl --fail http://127.0.0.1:8099/health && curl --fail http://127.0.0.1:8100/health'
printf '%s\n' 'Expiry: sudo systemctl list-timers trip-rescue-expiry.timer --no-pager'
