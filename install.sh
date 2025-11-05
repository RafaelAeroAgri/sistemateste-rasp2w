#!/bin/bash
# Script de instalação completa do Trichogramma Pi
# Para Raspberry Pi Zero 2 W com Raspberry Pi OS

set -e

echo "=========================================="
echo "INSTALAÇÃO TRICHOGRAMMA PI"
echo "=========================================="
echo ""

# Verificar se está rodando na Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Este script deve ser executado na Raspberry Pi"
    exit 1
fi

# 1. Atualizar sistema
echo "1. Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar RaspAP
echo ""
echo "2. Instalando RaspAP (gerenciamento WiFi)..."
if [ ! -f /etc/raspap/hostapd.ini ]; then
    # Configurar iptables para modo legacy
    sudo apt install -y iptables
    sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
    sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy
    
    # Instalar RaspAP
    echo "   Instalando RaspAP (pode demorar 5-10 minutos)..."
    curl -sL https://install.raspap.com | bash -s -- --yes
else
    echo "   ✓ RaspAP já instalado"
fi

# 3. Instalar pigpio
echo ""
echo "3. Instalando pigpio (controle PWM)..."
sudo apt install -y pigpio python3-pigpio

# 4. Instalar dependências Python
echo ""
echo "4. Instalando dependências Python..."
pip3 install --break-system-packages pigpio PyYAML==6.0.1 psutil==5.9.5

# 5. Habilitar pigpiod
echo ""
echo "5. Habilitando daemon pigpiod..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# 6. Instalar serviço HTTP
echo ""
echo "6. Instalando serviço HTTP..."
sudo cp ~/trichogramma-pi/systemd/trichogramma-http.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trichogramma-http
sudo systemctl start trichogramma-http

# 7. Criar script de configuração do uap0
echo ""
echo "7. Configurando interface uap0..."

sudo tee /usr/local/bin/create-uap0.sh > /dev/null <<'EOF'
#!/bin/bash
# Cria interface uap0 para hotspot
systemctl stop wpa_supplicant@wlan0 2>/dev/null || true
if ! ip link show uap0 2>/dev/null | grep -q uap0; then
    ip link set wlan0 down
    iw dev wlan0 interface add uap0 type __ap
fi
ip link set uap0 up
ip addr flush dev uap0
ip addr add 10.3.141.1/24 dev uap0
ip link set wlan0 up
echo "uap0 criada e configurada com IP 10.3.141.1"
EOF

sudo chmod +x /usr/local/bin/create-uap0.sh

# 8. Criar serviço systemd para uap0
sudo tee /etc/systemd/system/create-uap0.service > /dev/null <<'EOF'
[Unit]
Description=Create uap0 virtual interface
Before=hostapd.service
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/create-uap0.sh

[Install]
WantedBy=multi-user.target
RequiredBy=hostapd.service
EOF

# 9. Configurar hostapd para aguardar uap0
sudo mkdir -p /etc/systemd/system/hostapd.service.d
sudo tee /etc/systemd/system/hostapd.service.d/after-uap0.conf > /dev/null <<'EOF'
[Unit]
After=create-uap0.service
Requires=create-uap0.service
EOF

# 10. Habilitar serviços
echo ""
echo "8. Habilitando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable create-uap0
sudo systemctl start create-uap0

echo ""
echo "=========================================="
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "PRÓXIMOS PASSOS:"
echo ""
echo "1. Configurar hotspot no RaspAP:"
echo "   - Acesse: http://raspberrypi.local (ou o IP da Pi)"
echo "   - Login: admin / secret"
echo "   - Hotspot → Configurar:"
echo "     SSID: TrichoPi"
echo "     Senha: tricho2025"
echo "   - DHCP Server → Interface uap0:"
echo "     Router IP: 10.3.141.1"
echo "     Starting IP: 10.3.141.50"
echo "     Ending IP: 10.3.141.254"
echo ""
echo "2. Reboot:"
echo "   sudo reboot"
echo ""
echo "3. Após reboot, conecte no WiFi 'TrichoPi'"
echo "   e acesse: http://10.3.141.1:8080/ping"
echo ""
