#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente Bluetooth de teste para o Trichogramma Pi Service.
Permite enviar comandos interativamente via terminal.

Uso:
    python3 client_console.py [MAC_ADDRESS]
    
Se MAC_ADDRESS não for fornecido, tentará detectar automaticamente.
"""

import sys
import socket

try:
    import bluetooth
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("ERRO: PyBluez não está instalado.")
    print("Instale com: pip3 install pybluez")
    sys.exit(1)


class BluetoothClient:
    """Cliente simples para conectar ao Trichogramma Pi Service"""
    
    def __init__(self):
        self.sock = None
        self.connected = False
    
    def find_service(self, service_name="TrichoPi"):
        """
        Procura pelo serviço Bluetooth
        
        Args:
            service_name: Nome do serviço a procurar
            
        Returns:
            Tupla (endereço, porta) ou (None, None)
        """
        print(f"Procurando pelo serviço '{service_name}'...")
        
        services = bluetooth.find_service(name=service_name)
        
        if not services:
            print(f"Serviço '{service_name}' não encontrado.")
            print("\nTentando buscar serviços SPP disponíveis...")
            
            # Busca por qualquer serviço Serial Port
            services = bluetooth.find_service(uuid="00001101-0000-1000-8000-00805F9B34FB")
        
        if services:
            for svc in services:
                print(f"\nServiço encontrado:")
                print(f"  Nome: {svc.get('name', 'N/A')}")
                print(f"  Endereço: {svc.get('host', 'N/A')}")
                print(f"  Porta: {svc.get('port', 'N/A')}")
            
            # Usa o primeiro serviço encontrado
            first = services[0]
            return first.get("host"), first.get("port")
        
        return None, None
    
    def connect(self, address=None, port=1):
        """
        Conecta ao servidor Bluetooth
        
        Args:
            address: Endereço MAC do servidor (ou None para buscar)
            port: Porta RFCOMM (padrão: 1)
            
        Returns:
            True se conectado, False caso contrário
        """
        try:
            # Se não forneceu endereço, tenta encontrar automaticamente
            if not address:
                address, port = self.find_service()
                if not address:
                    print("\nNão foi possível encontrar o serviço automaticamente.")
                    print("Uso: python3 client_console.py <MAC_ADDRESS>")
                    return False
            
            print(f"\nConectando a {address} na porta {port}...")
            
            # Cria socket RFCOMM
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.sock.connect((address, port))
            
            self.connected = True
            print("✓ Conectado com sucesso!")
            print("\nDigite comandos (ou 'help' para ajuda, 'quit' para sair):")
            
            return True
            
        except bluetooth.BluetoothError as e:
            print(f"Erro ao conectar: {e}")
            return False
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return False
    
    def send_command(self, command: str) -> str:
        """
        Envia um comando e aguarda a resposta
        
        Args:
            command: Comando a enviar
            
        Returns:
            Resposta do servidor
        """
        if not self.connected or not self.sock:
            return "ERRO: Não conectado"
        
        try:
            # Adiciona newline se não tiver
            if not command.endswith('\n'):
                command += '\n'
            
            # Envia comando
            self.sock.send(command.encode('utf-8'))
            
            # Recebe resposta (até 1024 bytes)
            response = self.sock.recv(1024)
            
            return response.decode('utf-8').strip()
            
        except Exception as e:
            print(f"\nERRO ao enviar comando: {e}")
            self.connected = False
            return ""
    
    def close(self):
        """Fecha a conexão"""
        if self.sock:
            try:
                self.sock.close()
                print("\nConexão fechada.")
            except:
                pass
            finally:
                self.sock = None
                self.connected = False
    
    def interactive_mode(self):
        """Modo interativo: lê comandos do usuário"""
        if not self.connected:
            print("Não conectado.")
            return
        
        print("\n" + "="*60)
        self.print_help()
        print("="*60 + "\n")
        
        try:
            while self.connected:
                # Lê comando do usuário
                try:
                    command = input("> ").strip()
                except EOFError:
                    print()
                    break
                
                if not command:
                    continue
                
                # Comandos especiais do cliente
                if command.lower() == 'quit' or command.lower() == 'exit':
                    break
                
                elif command.lower() == 'help':
                    self.print_help()
                    continue
                
                elif command.lower() == 'clear':
                    print("\033[2J\033[H")  # Limpa a tela (Unix)
                    continue
                
                # Envia comando ao servidor
                response = self.send_command(command)
                
                if response:
                    print(f"< {response}")
        
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário.")
        
        finally:
            self.close()
    
    def print_help(self):
        """Exibe ajuda sobre os comandos"""
        print("\nComandos do Servidor:")
        print("  PING              - Testa conectividade")
        print("  STATUS            - Retorna status do sistema (JSON)")
        print("  CALIBRAR          - Executa calibração do servo (sweep)")
        print("  SET_ANGLE:NN      - Move servo para ângulo NN (0-180)")
        print("  GET_ANGLE         - Retorna ângulo atual do servo")
        print("  STOP              - Para qualquer sweep em andamento")
        print("  LIST              - Lista arquivos de voo (futuro)")
        print("\nComandos do Cliente:")
        print("  help              - Exibe esta ajuda")
        print("  clear             - Limpa a tela")
        print("  quit / exit       - Encerra o cliente")


def main():
    """Função principal"""
    print("=" * 60)
    print("Trichogramma Pi Service - Cliente de Teste Bluetooth")
    print("=" * 60)
    
    if not BLUETOOTH_AVAILABLE:
        return
    
    # Obtém endereço MAC dos argumentos (se fornecido)
    address = sys.argv[1] if len(sys.argv) > 1 else None
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    # Cria cliente e conecta
    client = BluetoothClient()
    
    if address:
        success = client.connect(address, port)
    else:
        success = client.connect()
    
    if not success:
        print("\nDicas:")
        print("1. Certifique-se de que o serviço Trichogramma está rodando na Pi")
        print("2. Verifique se o dispositivo está pareado")
        print("3. Forneça o endereço MAC manualmente:")
        print("   python3 client_console.py AA:BB:CC:DD:EE:FF")
        return
    
    # Entra em modo interativo
    client.interactive_mode()


if __name__ == "__main__":
    main()

