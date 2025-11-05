#!/bin/bash
# Script para corrigir uap0 no boot
# COLE E EXECUTE TODO NA RASPBERRY PI

set -e

echo "=========================================="
echo "CORRIGINDO uap0 PARA BOOT AUTOMÁTICO"
echo "=========================================="

# 1. Criar serviço que configura uap0
echo "1. Criando serviço uap0-setup..."
sudo tee /etc/systemd/system/uap0-setup.service > /dev/null <<'EOF'
[Unit]
Description=Configure uap0 IP address after interface creation
After=network.target
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=3
ExecStart=/bin/bash -c 'while true; do if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then CURRENT_IP=$(ip addr show uap0 2>/dev/null | grep -oP "inet \K[0-9.]+" || echo ""); if [ "$CURRENT_IP" != "10.3.141.1" ]; then ip addr flush dev uap0 2>/dev/null || true; ip addr add 10.3.141.1/24 dev uap0; ip link set uap0 up; systemctl restart dnsmasq 2>/dev/null || true; fi; sleep infinity; fi; sleep 2; done'

[Install]
WantedBy=multi-user.target
EOF

# 2. Configurar hostapd para aguardar uap0
echo "2. Configurando hostapd para aguardar uap0..."
sudo mkdir -p /etc/systemd/system/hostapd.service.d
sudo tee /etc/systemd/system/hostapd.service.d/wait-uap0.conf > /dev/null <<'EOF'
[Unit]
After=uap0-setup.service
Wants=uap0-setup.service

[Service]
ExecStartPre=/bin/bash -c 'for i in {1..60}; do if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then exit 0; fi; sleep 1; done; echo "Timeout: uap0 not found"; exit 1'
EOF

# 3. Recarregar systemd
echo "3. Recarregando systemd..."
sudo systemctl daemon-reload

# 4. Habilitar e iniciar serviço
echo "4. Habilitando serviço..."
sudo systemctl enable uap0-setup
sudo systemctl start uap0-setup

# 5. Verificar se funcionou
echo ""
echo "5. Verificando status..."
sleep 5

if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then
    echo "✓ Interface uap0 encontrada"
    if ip addr show uap0 2>/dev/null | grep -q "10.3.141.1"; then
        echo "✓ IP 10.3.141.1 configurado com sucesso!"
    else
        echo "⚠️  IP ainda não configurado (aguarde alguns segundos)"
    fi
else
    echo "⚠️  Interface uap0 ainda não existe (será criada pelo RaspAP no boot)"
fi

echo ""
echo "=========================================="
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Agora execute:"
echo "  sudo reboot"
echo ""
echo "Após reboot, verifique:"
echo "  ip addr show uap0"
echo "  (deve mostrar 10.3.141.1)"
echo ""

