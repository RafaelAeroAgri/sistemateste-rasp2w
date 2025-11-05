#!/bin/bash
# Configura Raspberry Pi como WiFi Hotspot (Access Point)
# Para uso em campo sem internet

set -e

echo "=========================================="
echo "Configurando WiFi Hotspot - TrichoPi"
echo "=========================================="

# Instalar dependências
echo "Instalando hostapd e dnsmasq..."
sudo apt install -y hostapd dnsmasq

# Parar serviços
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Backup de configurações
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup 2>/dev/null || true
sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true

# Configurar IP estático para wlan0
echo "Configurando IP estático..."
sudo tee -a /etc/dhcpcd.conf > /dev/null <<'EOF'

# Interface wlan0 como hotspot
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF

# Configurar dnsmasq (DHCP server)
echo "Configurando DHCP..."
sudo tee /etc/dnsmasq.conf > /dev/null <<'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/trichopi.local/192.168.4.1
EOF

# Configurar hostapd (Access Point)
echo "Configurando Access Point..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<'EOF'
interface=wlan0
driver=nl80211
ssid=TrichoPi
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=tricho2025
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Apontar para config
sudo tee /etc/default/hostapd > /dev/null <<'EOF'
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Habilitar serviços
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

echo ""
echo "✅ WiFi Hotspot configurado!"
echo ""
echo "SSID: TrichoPi"
echo "Senha: tricho2025"
echo "IP da Pi: 192.168.4.1"
echo ""
echo "Para ativar agora, execute:"
echo "  sudo reboot"
echo ""
echo "Após reboot, conecte no WiFi 'TrichoPi' com senha 'tricho2025'"
echo "Acesse via HTTP: http://192.168.4.1:8080"

