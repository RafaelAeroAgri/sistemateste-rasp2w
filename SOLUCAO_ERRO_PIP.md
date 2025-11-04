# 🔧 Solução: Erro "externally-managed-environment"

## ❌ O Erro

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz...
```

Este erro aparece no **Raspberry Pi OS Bookworm** (e versões posteriores) devido ao PEP 668, que protege o Python do sistema.

---

## ✅ Solução Rápida

Na sua Raspberry Pi, execute:

```bash
cd ~/trichogramma-pi

# 1. Instalar pybluez via apt (método recomendado)
sudo apt install -y python3-bluez python3-pybluez

# 2. Instalar outros pacotes Python
pip3 install --break-system-packages RPi.GPIO==0.7.1 PyYAML==6.0.1 psutil==5.9.5
```

**Pronto!** ✅

---

## 🧪 Verificar Instalação

Teste se os pacotes foram instalados:

```bash
python3 -c "import bluetooth; print('✓ bluetooth OK')"
python3 -c "import RPi.GPIO; print('✓ RPi.GPIO OK')"
python3 -c "import yaml; print('✓ yaml OK')"
python3 -c "import psutil; print('✓ psutil OK')"
```

Todos devem imprimir "OK".

---

## 🚀 Continuar Instalação

Após instalar os pacotes, continue:

```bash
# Se estava usando o script de instalação, não precisa fazer nada mais
# Os pacotes já estão instalados!

# Teste o serviço manualmente:
cd ~/trichogramma-pi/service
python3 main.py
```

Se aparecer:
```
INFO: Servidor Bluetooth aguardando conexões...
```

**Está funcionando!** 🎉

---

## 📝 Scripts Atualizados

Os scripts `install.sh` e `setup_from_git.sh` foram atualizados para:
- ✅ Instalar `pybluez` via apt automaticamente
- ✅ Usar `--break-system-packages` para outros pacotes
- ✅ Evitar esse erro

Se baixar o código atualizado do Git, não terá mais esse problema.

---

## 🤔 Por Que Este Erro Acontece?

O **Raspberry Pi OS Bookworm** (versão de 2023+) usa **PEP 668**, que impede instalações diretas de pacotes Python via `pip` para evitar conflitos com pacotes do sistema.

**Soluções possíveis:**
1. **Usar apt** quando o pacote está disponível (nosso caso com pybluez) ✅
2. **Usar `--break-system-packages`** (aceitável para Pi dedicada)
3. **Usar ambiente virtual** (melhor prática geral, mas mais complexo)

Para este projeto, usamos **opção 1 + 2** por ser mais simples e prático.

---

## 🔄 Se Já Baixou o Código Antigo

Atualize do Git:

```bash
cd ~/trichogramma-pi
git pull origin main
```

Ou baixe novamente:

```bash
rm -rf ~/trichogramma-pi
bash <(curl -sL https://raw.githubusercontent.com/RafaelAeroAgri/sistemateste-rasp2w/main/setup_from_git.sh)
```

---

## ⚠️ Alternativa: Ambiente Virtual (Avançado)

Se preferir usar ambiente virtual (não necessário para este projeto):

```bash
cd ~/trichogramma-pi

# Criar ambiente virtual
python3 -m venv venv

# Ativar
source venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt

# Atualizar o systemd service para usar o venv:
# ExecStart=/home/aeroagri/trichogramma-pi/venv/bin/python3 /home/aeroagri/trichogramma-pi/service/main.py
```

**Mas a solução recomendada é a do início deste documento!** ✅

---

## 📞 Suporte

Se ainda tiver problemas:

1. Verifique a versão do Python: `python3 --version` (deve ser 3.9+)
2. Verifique a versão do OS: `cat /etc/os-release`
3. Veja os logs de instalação
4. Consulte o `README.md` para mais detalhes

---

**Problema resolvido!** Continue com a instalação seguindo os próximos passos. 🚀

