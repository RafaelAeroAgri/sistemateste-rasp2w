#!/bin/bash
# Script para corrigir problema de uap0 no boot
# Deve ser executado NA RASPBERRY PI

echo "=========================================="
echo "CORRIGINDO PROBLEMA uap0 NO BOOT"
echo "=========================================="

# 1. Criar serviço que configura uap0
sudo tee /etc/systemd/system/uap0-setup.service > /dev/null <<'EOF'
[Unit]
Description=Setup uap0 interface IP address
After=network.target
Wants=network-online.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
ExecStart=/bin/bash -c 'while true; do if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then ip addr flush dev uap0 2>/dev/null || true; ip addr add 10.3.141.1/24 dev uap0 2>/dev/null && ip link set uap0 up && systemctl restart dnsmasq && sleep infinity; fi; sleep 2; done'

[Install]
WantedBy=multi-user.target
EOF

# 2. Modificar hostapd para aguardar uap0
sudo mkdir -p /etc/systemd/system/hostapd.service.d
sudo tee /etc/systemd/system/hostapd.service.d/wait-uap0.conf > /dev/null <<'EOF'
[Unit]
After=uap0-setup.service
Requires=uap0-setup.service

[Service]
ExecStartPre=/bin/bash -c 'for i in {1..30}; do if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then exit 0; fi; sleep 1; done; echo "uap0 not ready"; exit 1'
EOF

# 3. Recarregar systemd
sudo systemctl daemon-reload

# 4. Habilitar serviços
sudo systemctl enable uap0-setup
sudo systemctl start uap0-setup

# 5. Configurar hostapd para aguardar
sudo systemctl edit hostapd --force --full <<'EOF'
[Unit]
Description=Access point and authentication server for Wi-Fi and Ethernet
After=network.target
After=uap0-setup.service
Requires=uap0-setup.service

[Service]
Type=forking
PIDFile=/var/run/hostapd.pid
EnvironmentFile=/etc/default/hostapd
ExecStart=/usr/sbin/hostapd -B -P /var/run/hostapd.pid $DAEMON_OPTS ${DAEMON_CONF}
ExecStartPre=/bin/bash -c 'for i in {1..30}; do if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then exit 0; fi; sleep 1; done; echo "uap0 not ready"; exit 1'

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "✅ Serviços configurados!"
echo ""
echo "Agora execute:"
echo "  sudo reboot"
echo ""
echo "Após reboot, verifique:"
echo "  ip addr show uap0"
echo "  (deve mostrar 10.3.141.1)"

