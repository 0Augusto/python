# IP Camera Portal Manager

## 📋 Descrição

O IP Camera Portal Manager é uma solução automatizada para gerenciamento de câmeras IP em redes locais, com integração a um portal web e suporte a múltiplas plataformas. O sistema descobre câmeras automaticamente, cria IPs virtuais e gerencia streams RTSP provenientes da AWS.

## 🚀 Funcionalidades

- 🔍 **Descoberta Automática** de câmeras IP na rede local
- 🌐 **Integração com Portal Web** para ativação remota
- 🖥️ **Criação de IPs Virtuais** para câmeras ativadas
- 🔄 **Redirecionamento RTSP** de streams AWS para IPs locais
- 📊 **Monitoramento em Tempo Real** do status das câmeras
- 🛡️ **Configuração Segura** com autenticação via API
- 📝 **Logs Detalhados** para troubleshooting
- 🔧 **Instalação Automática** como serviço de sistema

---

## 🍎 MacBook Apple Silicon (macOS)

### Pré-requisitos

1. **macOS 12+** (Monterey ou superior)
2. **Python 3.9+** (recomendado 3.11)
3. **Homebrew** instalado
4. **Acesso administrativo** (sudo)

### Instalação Passo a Passo

#### 1. Configurar Ambiente Python
```bash
# Instalar Python via Homebrew
brew install python@3.11

# Verificar instalação
python3 --version
pip3 --version
```

#### 2. Instalar Dependências do Sistema
```bash
# Instalar ferramentas de rede
brew install arp-scan nmap iproute2mac

# Instalar dependências Python
pip3 install requests netifaces psutil
```

#### 3. Configurar Permissões de Rede
```bash
# Adicionar permissões para arp-scan
sudo chmod +s /usr/local/sbin/arp-scan

# Habilitar encaminhamento IP
sudo sysctl -w net.inet.ip.forwarding=1
```

#### 4. Clonar e Configurar o Projeto
```bash
# Clonar repositório
git clone https://github.com/seuusuario/ip-camera-portal.git
cd ip-camera-portal

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install -r requirements-macos.txt
```

#### 5. Configurar Arquivo de Configuração
```bash
# Criar diretório de configuração
sudo mkdir -p /etc/camera_portal

# Copiar configuração padrão
sudo cp config/macos-config.json /etc/camera_portal/config.json

# Editar configuração
sudo nano /etc/camera_portal/config.json
```

Exemplo de configuração para macOS:
```json
{
    "portal_api_url": "https://seu-portal.com/api",
    "portal_api_key": "sua-chave-api",
    "virtual_ip_base": "192.168.1.200",
    "network_interface": "en0",
    "macos_specific": {
        "use_pfctl": true,
        "pf_config_path": "/etc/pf.conf",
        "launchd_service": "com.camera.portal"
    }
}
```

#### 6. Instalar como Serviço LaunchDaemon
```bash
# Copiar script de instalação
chmod +x scripts/install-macos.sh
sudo ./scripts/install-macos.sh

# OU manualmente:

# Criar serviço LaunchDaemon
sudo cp launchd/com.camera.portal.plist /Library/LaunchDaemons/

# Carregar serviço
sudo launchctl load /Library/LaunchDaemons/com.camera.portal.plist
sudo launchctl start com.camera.portal
```

#### 7. Configurar Firewall (PF)
```bash
# Backup do arquivo pf.conf
sudo cp /etc/pf.conf /etc/pf.conf.backup

# Adicionar regras para port forwarding
echo "
# Regras para Camera Portal
rdr pass on en0 inet proto tcp from any to 192.168.1.200/29 port 554 -> 127.0.0.1 port 8080
pass in quick on en0 inet proto tcp from any to 192.168.1.200/29 port 554
" | sudo tee -a /etc/pf.conf

# Recarregar regras PF
sudo pfctl -f /etc/pf.conf
sudo pfctl -e
```

#### 8. Executar Manualmente (Teste)
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar com permissões de administrador
sudo python3 camera_portal_manager.py --config /etc/camera_portal/config.json
```

### Comandos Úteis macOS

```bash
# Verificar status do serviço
sudo launchctl list | grep camera.portal

# Visualizar logs
sudo tail -f /var/log/camera_portal.log

# Reiniciar serviço
sudo launchctl stop com.camera.portal
sudo launchctl start com.camera.portal

# Desinstalar serviço
sudo launchctl unload /Library/LaunchDaemons/com.camera.portal.plist
sudo rm /Library/LaunchDaemons/com.camera.portal.plist
```

---

## 🐧 Linux (Ubuntu/Debian/CentOS)

### Pré-requisitos

1. **Linux Kernel 4.4+**
2. **Python 3.8+**
3. **Acesso root** ou sudo

### Instalação Passo a Passo

#### 1. Atualizar Sistema
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 2. Instalar Dependências
```bash
# Ubuntu/Debian
sudo apt install -y python3-pip python3-venv arp-scan net-tools iproute2 iptables-persistent

# CentOS/RHEL 8+
sudo dnf install -y python3-pip python3-devel nmap-ncat iptables-services
sudo dnf group install -y "Development Tools"
```

#### 3. Configurar Python
```bash
# Criar usuário dedicado (opcional)
sudo useradd -r -s /bin/false cameraportal

# Criar diretórios necessários
sudo mkdir -p /opt/camera_portal /etc/camera_portal /var/log/camera_portal
```

#### 4. Clonar Repositório
```bash
# Clonar projeto
git clone https://github.com/seuusuario/ip-camera-portal.git
cd ip-camera-portal

# Copiar arquivos
sudo cp -r . /opt/camera_portal/
sudo chown -R cameraportal:cameraportal /opt/camera_portal
sudo chmod +x /opt/camera_portal/camera_portal_manager.py
```

#### 5. Configurar Ambiente Python
```bash
cd /opt/camera_portal

# Criar ambiente virtual
sudo python3 -m venv venv
sudo /opt/camera_portal/venv/bin/pip install -r requirements.txt

# Instalar dependências adicionais
sudo /opt/camera_portal/venv/bin/pip install requests netifaces psutil
```

#### 6. Configurar Arquivos
```bash
# Configuração principal
sudo cp config/linux-config.json /etc/camera_portal/config.json

# Editar configuração
sudo nano /etc/camera_portal/config.json
```

Exemplo de configuração Linux:
```json
{
    "portal_api_url": "https://seu-portal.com/api",
    "portal_api_key": "sua-chave-api",
    "virtual_ip_base": "192.168.1.200",
    "network_interface": "eth0",
    "rtsp_port": 554,
    "scan_interval": 30,
    "log_level": "INFO",
    "iptables_persistent": true
}
```

#### 7. Configurar Serviço Systemd
```bash
# Copiar unit file do systemd
sudo cp systemd/camera-portal.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar serviço
sudo systemctl enable camera-portal.service
sudo systemctl start camera-portal.service
```

#### 8. Configurar IP Forwarding
```bash
# Habilitar permanentemente
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Configurar iptables persistentes
sudo apt install iptables-persistent  # Ubuntu/Debian
# ou
sudo systemctl enable iptables         # CentOS/RHEL
```

#### 9. Testar Instalação
```bash
# Verificar status
sudo systemctl status camera-portal

# Verificar logs
sudo journalctl -u camera-portal -f

# Testar descoberta manual
sudo /opt/camera_portal/venv/bin/python /opt/camera_portal/test_discovery.py
```

### Script de Instalação Automática Linux
```bash
#!/bin/bash
# install-linux.sh

set -e

echo "Instalando IP Camera Portal Manager no Linux..."

# Detectar distribuição
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Não foi possível detectar a distribuição Linux"
    exit 1
fi

# Instalar dependências base
case $OS in
    ubuntu|debian)
        sudo apt update
        sudo apt install -y git python3-pip python3-venv arp-scan net-tools
        ;;
    centos|rhel|fedora)
        sudo yum install -y git python3-pip python3-devel nmap-ncat
        ;;
    *)
        echo "Distribuição não suportada: $OS"
        exit 1
        ;;
esac

# Resto da instalação...
# (Incluir os passos acima em formato de script)
```

---

## 🪟 Windows 10/11

### Opção 1: Usando WSL2 (Recomendado)

#### 1. Instalar WSL2
```powershell
# Executar como Administrador no PowerShell
wsl --install

# Ou manualmente:
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

# Reiniciar computador
```

#### 2. Instalar Distribuição Ubuntu
```powershell
# Listar distribuições disponíveis
wsl --list --online

# Instalar Ubuntu
wsl --install -d Ubuntu-22.04
```

#### 3. Configurar WSL2
```bash
# Acessar terminal WSL
wsl

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Seguir instruções de instalação Linux acima dentro do WSL
```

#### 4. Configurar Integração Windows-WSL
```powershell
# Permitir tráfego entre Windows e WSL
New-NetFirewallRule -DisplayName "WSL2 Camera Portal" -Direction Inbound -InterfaceAlias "vEthernet (WSL)" -Action Allow
```

### Opção 2: Instalação Nativa Windows

#### 1. Instalar Python para Windows
1. Baixar Python 3.11+ de [python.org](https://python.org)
2. Instalar marcando "Add Python to PATH"
3. Verificar instalação:
```cmd
python --version
pip --version
```

#### 2. Instalar Dependências
```cmd
# Instalar ferramentas de build
choco install visualstudio2019buildtools -y
choco install windows-sdk-10.1 -y

# Instalar dependências Python
pip install requests netifaces psutil pywin32

# Instalar Nmap para Windows (para substituir arp-scan)
# Baixar de https://nmap.org/download.html
```

#### 3. Clonar e Configurar Projeto
```cmd
# Clonar repositório
git clone https://github.com/seuusuario/ip-camera-portal.git
cd ip-camera-portal

# Configurar para Windows
copy config\windows-config.json config.json

# Editar configuração
notepad config.json
```

Exemplo de configuração Windows:
```json
{
    "portal_api_url": "https://seu-portal.com/api",
    "portal_api_key": "sua-chave-api",
    "virtual_ip_base": "192.168.1.200",
    "network_interface": "Ethernet",
    "windows_specific": {
        "use_netsh": true,
        "use_windows_firewall": true,
        "run_as_service": true
    }
}
```

#### 4. Instalar como Serviço Windows
```powershell
# Executar como Administrador
.\scripts\install-windows.ps1

# OU manualmente:

# Instalar NSSM (Non-Sucking Service Manager)
choco install nssm -y

# Criar serviço
nssm install CameraPortal "C:\Python311\python.exe" "C:\camera_portal\camera_portal_manager.py"

# Configurar serviço
nssm set CameraPortal AppDirectory "C:\camera_portal"
nssm set CameraPortal AppStdout "C:\camera_portal\portal.log"
nssm set CameraPortal AppStderr "C:\camera_portal\portal-error.log"
nssm set CameraPortal Start SERVICE_AUTO_START

# Iniciar serviço
nssm start CameraPortal
```

#### 5. Configurar Firewall Windows
```powershell
# Permitir tráfego RTSP (porta 554)
New-NetFirewallRule -DisplayName "Camera Portal RTSP" -Direction Inbound -Protocol TCP -LocalPort 554 -Action Allow

# Permitir portas de administração
New-NetFirewallRule -DisplayName "Camera Portal Admin" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### Script de Instalação Windows
```powershell
# install-windows.ps1
param([switch]$Elevated)

function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
    $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

if ((Test-Admin) -eq $false) {
    Start-Process powershell.exe -Verb RunAs -ArgumentList ("-File `"{0}`"" -f $MyInvocation.MyCommand.Path)
    exit
}

Write-Host "Instalando IP Camera Portal Manager no Windows..." -ForegroundColor Green

# Instalar Chocolatey (se não existir)
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

# Instalar dependências
choco install python -y
choco install git -y
choco install nmap -y

# Clonar repositório
git clone https://github.com/seuusuario/ip-camera-portal.git C:\CameraPortal
cd C:\CameraPortal

# Instalar dependências Python
pip install -r requirements-windows.txt

# Criar diretórios
New-Item -ItemType Directory -Force -Path "C:\ProgramData\CameraPortal"
New-Item -ItemType Directory -Force -Path "C:\ProgramData\CameraPortal\Logs"

Write-Host "Instalação completa!" -ForegroundColor Green
Write-Host "Configure o arquivo C:\CameraPortal\config.json e execute:"
Write-Host "python camera_portal_manager.py" -ForegroundColor Yellow
```

---

## 🔧 Configuração Avançada

### Configuração do Portal Web

1. **Obter API Key** do portal web
2. **Configurar endpoint** no arquivo de configuração
3. **Testar conexão**:
```bash
python3 test_connection.py --portal https://seu-portal.com --key sua-chave
```

### Configuração de Rede

#### Para redes complexas:
```json
{
    "network": {
        "main_interface": "eth0",
        "vlan_interfaces": ["eth0.100", "eth0.200"],
        "subnet_masks": ["255.255.255.0", "255.255.254.0"],
        "gateway": "192.168.1.1",
        "dns_servers": ["8.8.8.8", "8.8.4.4"]
    }
}
```

#### Configuração de Câmeras Específicas
```json
{
    "cameras": {
        "camera_01": {
            "manufacturer": "Hikvision",
            "model": "DS-2CD2143G0-I",
            "rtsp_template": "rtsp://{username}:{password}@{ip}:554/Streaming/Channels/101",
            "credentials": {
                "username": "admin",
                "password": "camera123"
            }
        }
    }
}
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. ARP-Scan não funciona (macOS)
```bash
# Solução:
sudo chmod +s /usr/local/sbin/arp-scan
sudo /usr/local/sbin/arp-scan --interface=en0 --localnet
```

#### 2. Permissões de IP Forwarding (Linux)
```bash
# Verificar:
cat /proc/sys/net/ipv4/ip_forward

# Habilitar:
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

#### 3. Firewall bloqueando tráfego
```bash
# Linux - Verificar iptables:
sudo iptables -L -n -v

# macOS - Verificar PF:
sudo pfctl -s rules

# Windows - Verificar firewall:
netsh advfirewall firewall show rule name=all
```

#### 4. Serviço não inicia
```bash
# Verificar logs:
# Linux
sudo journalctl -u camera-portal -n 50

# macOS
sudo log show --predicate 'subsystem == "com.camera.portal"' --last 10m

# Windows
Get-EventLog -LogName Application -Source "CameraPortal" -Newest 20
```

## 📊 Monitoramento

### Scripts de Monitoramento
```bash
# Verificar status das câmeras
python3 monitor_cameras.py --status

# Testar streams RTSP
python3 test_rtsp_streams.py --camera all

# Verificar uso de recursos
python3 resource_monitor.py --interval 5
```

### Dashboard Web (Opcional)
```bash
# Instalar dashboard
pip install flask flask-socketio

# Executar
python3 dashboard/app.py

# Acessar: http://localhost:5000
```

## 🔄 Atualização

### Atualizar para Nova Versão
```bash
# Todas as plataformas:
git pull origin main

# Linux/macOS:
sudo ./scripts/update.sh

# Windows:
.\scripts\update.ps1
```

## 🗑️ Desinstalação

### Linux
```bash
sudo systemctl stop camera-portal
sudo systemctl disable camera-portal
sudo rm /etc/systemd/system/camera-portal.service
sudo rm -rf /opt/camera_portal /etc/camera_portal
```

### macOS
```bash
sudo launchctl unload /Library/LaunchDaemons/com.camera.portal.plist
sudo rm /Library/LaunchDaemons/com.camera.portal.plist
brew uninstall arp-scan
```

### Windows
```powershell
# Desinstalar serviço
nssm stop CameraPortal
nssm remove CameraPortal confirm

# Remover diretórios
Remove-Item -Recurse -Force C:\CameraPortal
Remove-Item -Recurse -Force C:\ProgramData\CameraPortal
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Crie um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Aviso de Segurança

- Nunca exponha o portal publicamente sem autenticação
- Use HTTPS para comunicação com APIs
- Altere senhas padrão das câmeras
- Mantenha o sistema atualizado
- Use VLANs para isolar câmeras quando possível

---

## 📞 Suporte

- **Issues**: [GitHub Issues]\
- **Documentação**: [Wiki do Projeto]
- **Email**: 

## 🔗 Links Úteis

- [Documentação RTSP](https://www.rtsp.org/)
- [Guia de Segurança de Câmeras IP](https://www.security.org/camera-security/)
- [Documentação Python Socket](https://docs.python.org/3/library/socket.html)

---

