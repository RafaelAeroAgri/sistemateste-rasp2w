# ⚡ Guia de Acesso Rápido - TrichoPi

## 🏠 MODO WIFI NORMAL (Casa/Desenvolvimento)

### SSH:
```bash
ssh aeroagri@raspberrypi.local
# OU
ssh aeroagri@192.168.1.X  # (verificar IP no roteador)
```

### Alternar para Modo Hotspot:
```bash
cd ~/trichogramma-pi
sudo ./wifi_backup_and_hotspot.sh
```

---

## 🌾 MODO HOTSPOT (Campo)

### Conectar:
1. **Tablet** → Configurações → WiFi
2. **Rede**: TrichoPi
3. **Senha**: tricho2025

### SSH:
```bash
ssh aeroagri@192.168.4.1
```

### App:
Abre automaticamente, conecta em `http://192.168.4.1:8080`

### Voltar ao WiFi Normal:
```bash
ssh aeroagri@192.168.4.1
cd ~/trichogramma-pi
./wifi_restore_normal.sh
sudo reboot
```

---

## 🔧 Comandos Úteis

### Ver logs do serviço:
```bash
sudo journalctl -u trichogramma-http -f
```

### Reiniciar serviço:
```bash
sudo systemctl restart trichogramma-http
```

### Ver status:
```bash
sudo systemctl status trichogramma-http
```

### Testar servidor HTTP:
```bash
curl http://192.168.4.1:8080/ping
# Resposta: {"status":"ok","message":"PONG"}
```

---

## 🆘 Perdi Acesso? (Emergência)

### Opção 1: Monitor + Teclado
```bash
cd ~/trichogramma-pi
./wifi_restore_normal.sh
sudo reboot
```

### Opção 2: Cartão SD no PC
1. Retire o SD
2. Coloque no PC
3. Na partição boot, crie arquivo `wpa_supplicant.conf`:

```
country=BR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="SUA_REDE"
    psk="SUA_SENHA"
}
```

4. Coloque o SD de volta
5. Ligue a Pi

---

**Guarde este arquivo! É sua referência rápida.** 📌

