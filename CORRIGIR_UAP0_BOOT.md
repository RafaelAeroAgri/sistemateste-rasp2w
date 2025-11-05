# 🔧 Corrigir uap0 no Boot - COMANDOS NA PI

## ⚠️ PROBLEMA
A interface `uap0` não está sendo criada/configurada antes do `hostapd` iniciar, causando erro no boot.

## ✅ SOLUÇÃO RÁPIDA

**Execute estes comandos NA RASPBERRY PI:**

```bash
# 1. Criar serviço que configura uap0 automaticamente
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
sudo mkdir -p /etc/systemd/system/hostapd.service.d
sudo tee /etc/systemd/system/hostapd.service.d/wait-uap0.conf > /dev/null <<'EOF'
[Unit]
After=uap0-setup.service
Wants=uap0-setup.service

[Service]
ExecStartPre=/bin/bash -c 'for i in {1..60}; do if ip link show uap0 2>/dev/null | grep -q "state UP\|state UNKNOWN"; then exit 0; fi; sleep 1; done; echo "Timeout: uap0 not found"; exit 1'
EOF

# 3. Recarregar systemd
sudo systemctl daemon-reload

# 4. Habilitar serviço
sudo systemctl enable uap0-setup
sudo systemctl start uap0-setup

# 5. Verificar status
sleep 5
ip addr show uap0

# Se mostrar 10.3.141.1, faça reboot:
sudo reboot
```

## 🎯 O QUE FAZ

1. **Cria serviço `uap0-setup`** que:
   - Fica em loop verificando se `uap0` existe
   - Quando encontra, configura IP `10.3.141.1/24`
   - Reinicia `dnsmasq` para aplicar DHCP

2. **Modifica `hostapd`** para:
   - Aguardar até `uap0` existir antes de iniciar
   - Timeout de 60 segundos

3. **Funciona automaticamente no boot** ✨

## 📋 VERIFICAÇÃO APÓS REBOOT

```bash
# Verificar interface
ip addr show uap0

# Deve mostrar:
# inet 10.3.141.1/24 scope global uap0

# Verificar hostapd
sudo systemctl status hostapd

# Deve estar "active (running)" sem erros

# Verificar hotspot
sudo systemctl status hostapd | grep -i "error\|fail"
# Não deve mostrar nada
```

## 🐛 SE AINDA NÃO FUNCIONAR

```bash
# Verificar se uap0 está sendo criada
ip link show

# Ver logs do hostapd
sudo journalctl -u hostapd -n 50

# Ver logs do uap0-setup
sudo journalctl -u uap0-setup -n 50

# Forçar criação manual (teste)
sudo ip link set wlan0 down
sudo iw dev wlan0 interface add uap0 type __ap
sudo ip link set uap0 up
sudo ip addr add 10.3.141.1/24 dev uap0
```

## ✅ RESULTADO ESPERADO

Após reboot, o hotspot **TrichoPi** deve:
- ✅ Aparecer automaticamente
- ✅ Ter IP `10.3.141.1` configurado
- ✅ Funcionar sem erros
- ✅ Cliente conecta e recebe IP via DHCP
- ✅ App Flutter conecta em `http://10.3.141.1:8080`

