#!/bin/bash
# Script para configurar hotspot automático no boot
# Deve ser executado NA RASPBERRY PI

set -e

echo "=========================================="
echo "CONFIGURANDO HOTSPOT AUTOMÁTICO NO BOOT"
echo "=========================================="

# 1. Verificar se RaspAP está instalado
if [ ! -f /etc/raspap/hostapd.ini ]; then
    echo "❌ RaspAP não encontrado!"
    echo "Instale primeiro: curl -sL https://install.raspap.com | bash"
    exit 1
fi

# 2. Configurar RaspAP para iniciar hotspot no boot
echo ""
echo "1. Configurando RaspAP para iniciar hotspot automaticamente..."

# Editar defaults.json do RaspAP
RASPAP_DEFAULTS="/etc/raspap/networking/defaults.json"
if [ -f "$RASPAP_DEFAULTS" ]; then
    # Backup
    sudo cp "$RASPAP_DEFAULTS" "${RASPAP_DEFAULTS}.backup"
    
    # Configurar para hotspot automático
    sudo python3 <<'PYTHON'
import json
import os

defaults_path = "/etc/raspap/networking/defaults.json"
with open(defaults_path, 'r') as f:
    config = json.load(f)

# Configurar hotspot automático
config['ap_enabled'] = True
config['ap_interface'] = 'uap0'
config['ap_ssid'] = 'TrichoPi'
config['ap_passphrase'] = 'tricho2025'
config['ap_channel'] = 6

# Configurar IP do hotspot
if 'ap_ip_address' not in config:
    config['ap_ip_address'] = '10.3.141.1'
if 'ap_subnet_mask' not in config:
    config['ap_subnet_mask'] = '255.255.255.0'
if 'ap_dhcp_range_start' not in config:
    config['ap_dhcp_range_start'] = '10.3.141.50'
if 'ap_dhcp_range_end' not in config:
    config['ap_dhcp_range_end'] = '10.3.141.254'

with open(defaults_path, 'w') as f:
    json.dump(config, f, indent=4)

print("✓ RaspAP configurado para hotspot automático")
PYTHON
else
    echo "⚠️  Arquivo defaults.json não encontrado, configurando manualmente..."
fi

# 3. Criar serviço que configura uap0 após ela ser criada
echo ""
echo "2. Criando serviço para configurar uap0..."

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

# 4. Modificar hostapd para aguardar uap0
echo ""
echo "3. Configurando hostapd para aguardar uap0..."

sudo mkdir -p /etc/systemd/system/hostapd.service.d
sudo tee /etc/systemd/system/hostapd.service.d/wait-uap0.conf > /dev/null <<'EOF'
[Unit]
After=uap0-setup.service
Wants=uap0-setup.service

[Service]
ExecStartPre=/bin/bash -c 'for i in {1..60}; do if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then exit 0; fi; sleep 1; done; echo "Timeout: uap0 not found"; exit 1'
EOF

# 5. Habilitar hotspot no RaspAP
echo ""
echo "4. Habilitando hotspot no RaspAP..."

# Usar raspap para ativar hotspot
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

# 6. Recarregar systemd
echo ""
echo "5. Recarregando systemd..."
sudo systemctl daemon-reload

# 7. Habilitar e iniciar serviços
echo ""
echo "6. Iniciando serviços..."
sudo systemctl enable uap0-setup
sudo systemctl start uap0-setup

# 8. Verificar status
echo ""
echo "=========================================="
echo "VERIFICANDO STATUS..."
echo "=========================================="

sleep 3

if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then
    echo "✓ Interface uap0 encontrada"
    if ip addr show uap0 2>/dev/null | grep -q "10.3.141.1"; then
        echo "✓ IP 10.3.141.1 configurado"
    else
        echo "⚠️  IP ainda não configurado (pode levar alguns segundos)"
    fi
else
    echo "⚠️  Interface uap0 ainda não existe (será criada pelo RaspAP)"
fi

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "Para aplicar, execute:"
echo "  sudo reboot"
echo ""
echo "Após reboot, verifique:"
echo "  ip addr show uap0"
echo "  (deve mostrar 10.3.141.1)"

