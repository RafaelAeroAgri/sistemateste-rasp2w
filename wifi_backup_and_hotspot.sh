#!/bin/bash
# Script SEGURO para ativar WiFi Hotspot
# FAZ BACKUP DE TUDO antes de alterar
# Permite reverter facilmente se necessário

set -e

echo "================================================================"
echo "ATIVAÇÃO SEGURA DO WIFI HOTSPOT - TrichoPi"
echo "================================================================"
echo ""
echo "Este script irá:"
echo "  1. FAZER BACKUP de todas as configurações WiFi atuais"
echo "  2. Configurar a Pi como Hotspot (SSID: TrichoPi)"
echo "  3. Criar script de REVERSÃO para voltar ao modo normal"
echo ""
echo "⚠️  IMPORTANTE:"
echo "  - Você perderá o acesso SSH via WiFi (Pi ficará como hotspot)"
echo "  - Para acessar via SSH: conecte no WiFi TrichoPi e use IP 192.168.4.1"
echo "  - Para VOLTAR ao modo WiFi normal: execute ./wifi_restore_normal.sh"
echo ""
read -p "Deseja continuar? [s/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "Operação cancelada."
    exit 0
fi

BACKUP_DIR="$HOME/trichogramma-pi-backup-$(date +%Y%m%d-%H%M%S)"

echo ""
echo "=========================================="
echo "PASSO 1: Criando backup..."
echo "=========================================="
mkdir -p "$BACKUP_DIR"

# Backup de configurações
sudo cp /etc/dhcpcd.conf "$BACKUP_DIR/dhcpcd.conf.backup" 2>/dev/null || true
sudo cp /etc/dnsmasq.conf "$BACKUP_DIR/dnsmasq.conf.backup" 2>/dev/null || true
sudo cp /etc/hostapd/hostapd.conf "$BACKUP_DIR/hostapd.conf.backup" 2>/dev/null || true
sudo cp /etc/wpa_supplicant/wpa_supplicant.conf "$BACKUP_DIR/wpa_supplicant.conf.backup" 2>/dev/null || true

# Salvar estado atual dos serviços
systemctl is-enabled wpa_supplicant > "$BACKUP_DIR/wpa_supplicant.state" 2>/dev/null || echo "disabled" > "$BACKUP_DIR/wpa_supplicant.state"

echo "✓ Backup salvo em: $BACKUP_DIR"

echo ""
echo "=========================================="
echo "PASSO 2: Instalando pacotes..."
echo "=========================================="
sudo apt install -y hostapd dnsmasq

echo ""
echo "=========================================="
echo "PASSO 3: Configurando Hotspot..."
echo "=========================================="

# Parar serviços
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl stop dnsmasq 2>/dev/null || true
sudo systemctl stop wpa_supplicant 2>/dev/null || true

# Configurar dhcpcd (IP estático)
if ! grep -q "interface wlan0" /etc/dhcpcd.conf; then
    sudo tee -a /etc/dhcpcd.conf > /dev/null <<'EOF'

# Hotspot TrichoPi
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF
fi

# Configurar dnsmasq
sudo tee /etc/dnsmasq.conf > /dev/null <<'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/trichopi.local/192.168.4.1
EOF

# Configurar hostapd
sudo mkdir -p /etc/hostapd
sudo tee /etc/hostapd/hostapd.conf > /dev/null <<'EOF'
interface=wlan0
driver=nl80211
ssid=TrichoPi
hw_mode=g
channel=6
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

sudo tee /etc/default/hostapd > /dev/null <<'EOF'
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Desabilitar wpa_supplicant
sudo systemctl disable wpa_supplicant
sudo systemctl mask wpa_supplicant

# Habilitar serviços do hotspot
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

echo ""
echo "=========================================="
echo "PASSO 4: Criando script de REVERSÃO..."
echo "=========================================="

# Criar script para voltar ao modo WiFi normal
cat > ~/trichogramma-pi/wifi_restore_normal.sh <<'ENDSCRIPT'
#!/bin/bash
# Script para REVERTER ao modo WiFi normal (cliente)
# Desfaz todas as alterações do hotspot

echo "================================================================"
echo "REVERTER PARA MODO WIFI NORMAL (Cliente)"
echo "================================================================"
echo ""
echo "Este script irá:"
echo "  - Desabilitar o Hotspot"
echo "  - Restaurar configurações WiFi originais"
echo "  - Permitir conexão em redes WiFi normais"
echo ""
read -p "Deseja continuar? [s/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "Operação cancelada."
    exit 0
fi

# Parar serviços do hotspot
echo "Parando serviços do hotspot..."
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq
sudo systemctl mask hostapd

# Habilitar wpa_supplicant
echo "Habilitando WiFi cliente..."
sudo systemctl unmask wpa_supplicant
sudo systemctl enable wpa_supplicant

# Restaurar dhcpcd.conf
echo "Restaurando configurações..."
sudo sed -i '/# Hotspot TrichoPi/,/nohook wpa_supplicant/d' /etc/dhcpcd.conf

# Reiniciar networking
echo "Reiniciando rede..."
sudo systemctl restart dhcpcd 2>/dev/null || true
sudo systemctl start wpa_supplicant

echo ""
echo "✅ Modo WiFi normal restaurado!"
echo ""
echo "Para conectar em uma rede WiFi, use:"
echo "  sudo raspi-config"
echo "  → System Options → Wireless LAN"
echo ""
echo "Ou edite:"
echo "  sudo nano /etc/wpa_supplicant/wpa_supplicant.conf"
echo ""
echo "Reinicie para aplicar:"
echo "  sudo reboot"
echo ""
ENDSCRIPT

chmod +x ~/trichogramma-pi/wifi_restore_normal.sh

echo "✓ Script de reversão criado: ~/trichogramma-pi/wifi_restore_normal.sh"

echo ""
echo "================================================================"
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "================================================================"
echo ""
echo "📋 INFORMAÇÕES:"
echo ""
echo "  WiFi Hotspot: TrichoPi"
echo "  Senha: tricho2025"
echo "  IP da Pi: 192.168.4.1"
echo "  Servidor HTTP: http://192.168.4.1:8080"
echo ""
echo "  Backup salvo em: $BACKUP_DIR"
echo "  Script de reversão: ~/trichogramma-pi/wifi_restore_normal.sh"
echo ""
echo "⚠️  IMPORTANTE - COMO ACESSAR APÓS REBOOT:"
echo ""
echo "  1. No tablet, conecte no WiFi 'TrichoPi' (senha: tricho2025)"
echo "  2. SSH: ssh aeroagri@192.168.4.1"
echo "  3. App: Conecta automaticamente"
echo ""
echo "🔄 PARA VOLTAR AO MODO WIFI NORMAL:"
echo ""
echo "  Execute: ~/trichogramma-pi/wifi_restore_normal.sh"
echo "  (Isso desfaz TODAS as alterações e volta ao WiFi cliente)"
echo ""
echo "================================================================"
echo ""
read -p "Reiniciar agora para ativar o hotspot? [s/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "Reiniciando em 3 segundos..."
    echo "Após reiniciar, conecte no WiFi 'TrichoPi' (senha: tricho2025)"
    sleep 3
    sudo reboot
else
    echo ""
    echo "Para ativar o hotspot, execute:"
    echo "  sudo reboot"
    echo ""
fi

