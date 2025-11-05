#!/bin/bash
# Script para tornar o Bluetooth sempre detectável e pareável
# Executado automaticamente na inicialização

# Aguarda o Bluetooth inicializar
sleep 5

# Configura via bluetoothctl
bluetoothctl <<EOF
power on
discoverable on
pairable on
agent NoInputNoOutput
default-agent
EOF

# Método alternativo via hciconfig (se bluetoothctl falhar)
hciconfig hci0 up 2>/dev/null
hciconfig hci0 piscan 2>/dev/null || echo "hciconfig não disponível (normal em sistemas modernos)"

echo "Bluetooth configurado: sempre detectável e pareável"

