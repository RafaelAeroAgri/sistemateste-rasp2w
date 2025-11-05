#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor HTTP para controle do servo via WiFi
Substitui a solução Bluetooth por HTTP REST API
"""

import sys
import os
import signal
import yaml
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Importa módulos do serviço
from logger import create_logger
from servo_control import ServoControl


class ServoHTTPHandler(BaseHTTPRequestHandler):
    """Handler para requisições HTTP"""
    
    servo = None
    logger = None
    
    def do_GET(self):
        """Processa requisições GET"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        try:
            # PING - Teste de conectividade
            if path == '/ping':
                self.send_json({'status': 'ok', 'message': 'PONG'})
            
            # STATUS - Informações do sistema
            elif path == '/status':
                response = {
                    'status': 'ok',
                    'servo_initialized': self.servo.is_initialized if self.servo else False,
                    'servo_angle': int(self.servo.get_angle()) if self.servo else 0,
                    'gpio_pin': 4
                }
                self.send_json(response)
            
            # GET_ANGLE - Ângulo atual
            elif path == '/angle':
                if not self.servo or not self.servo.is_initialized:
                    self.send_json({'status': 'error', 'message': 'Servo não inicializado'}, 500)
                    return
                
                angle = int(self.servo.get_angle())
                self.send_json({'status': 'ok', 'angle': angle})
            
            # ROOT - Informações da API
            elif path == '/':
                self.send_json({
                    'service': 'Trichogramma Pi HTTP Server',
                    'version': '1.0.0',
                    'endpoints': {
                        'GET /ping': 'Testa conectividade',
                        'GET /status': 'Status do sistema',
                        'GET /angle': 'Ângulo atual do servo',
                        'POST /calibrate': 'Executa calibração',
                        'POST /angle': 'Define ângulo (body: {"angle": NN})',
                        'POST /stop': 'Para movimento'
                    }
                })
            
            else:
                self.send_json({'status': 'error', 'message': 'Endpoint não encontrado'}, 404)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro no GET: {e}", exc_info=True)
            self.send_json({'status': 'error', 'message': str(e)}, 500)
    
    def do_POST(self):
        """Processa requisições POST"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            # Lê body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            data = json.loads(body) if body else {}
            
            # CALIBRAR - Executa calibração
            if path == '/calibrate':
                if not self.servo or not self.servo.is_initialized:
                    self.send_json({'status': 'error', 'message': 'Servo não inicializado'}, 500)
                    return
                
                self.servo.stop_sweep()
                self.servo.sweep(0, 180, 0.5, step=10.0)
                
                # Aguarda sweep terminar
                import time
                while self.servo.is_sweeping():
                    time.sleep(0.1)
                
                # Volta para 90°
                self.servo.set_angle(90)
                
                self.send_json({'status': 'ok', 'message': 'Calibração concluída'})
            
            # SET_ANGLE - Define ângulo
            elif path == '/angle':
                if not self.servo or not self.servo.is_initialized:
                    self.send_json({'status': 'error', 'message': 'Servo não inicializado'}, 500)
                    return
                
                angle = data.get('angle')
                if angle is None:
                    self.send_json({'status': 'error', 'message': 'Parâmetro "angle" obrigatório'}, 400)
                    return
                
                try:
                    angle = int(angle)
                    if angle < 0 or angle > 180:
                        self.send_json({'status': 'error', 'message': 'Ângulo deve estar entre 0 e 180'}, 400)
                        return
                    
                    success = self.servo.set_angle(angle)
                    if success:
                        self.send_json({'status': 'ok', 'angle': angle})
                    else:
                        self.send_json({'status': 'error', 'message': 'Falha ao mover servo'}, 500)
                        
                except ValueError:
                    self.send_json({'status': 'error', 'message': 'Ângulo inválido'}, 400)
            
            # STOP - Para movimento
            elif path == '/stop':
                if not self.servo:
                    self.send_json({'status': 'error', 'message': 'Servo não inicializado'}, 500)
                    return
                
                self.servo.stop_sweep()
                self.send_json({'status': 'ok', 'message': 'Movimento parado'})
            
            else:
                self.send_json({'status': 'error', 'message': 'Endpoint não encontrado'}, 404)
                
        except json.JSONDecodeError:
            self.send_json({'status': 'error', 'message': 'JSON inválido'}, 400)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro no POST: {e}", exc_info=True)
            self.send_json({'status': 'error', 'message': str(e)}, 500)
    
    def send_json(self, data, status_code=200):
        """Envia resposta JSON"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override para usar nosso logger"""
        if self.logger:
            self.logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Função principal"""
    print("Trichogramma Pi HTTP Server")
    print("=" * 60)
    
    # Carrega configuração
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Inicializa logger
    log_config = config.get('logging', {})
    logger = create_logger(
        log_config.get('logfile', '/var/log/trichogramma-service.log'),
        log_config.get('level', 'INFO')
    )
    
    logger.info("=" * 60)
    logger.info("Trichogramma Pi HTTP Server iniciando...")
    logger.info("=" * 60)
    
    # Inicializa servo
    servo_config = config.get('servo', {})
    servo = ServoControl(
        pin=servo_config.get('pwm_pin', 4),
        frequency=servo_config.get('frequency', 50),
        min_duty=servo_config.get('min_duty', 2.5),
        max_duty=servo_config.get('max_duty', 12.5),
        logger=logger
    )
    
    # Configura handler
    ServoHTTPHandler.servo = servo
    ServoHTTPHandler.logger = logger
    
    # Inicia servidor HTTP
    host = '0.0.0.0'  # Escuta em todas as interfaces
    port = 8080
    
    server = HTTPServer((host, port), ServoHTTPHandler)
    
    logger.info(f"Servidor HTTP rodando em {host}:{port}")
    logger.info("Endpoints disponíveis:")
    logger.info("  GET  /ping")
    logger.info("  GET  /status")
    logger.info("  GET  /angle")
    logger.info("  POST /calibrate")
    logger.info("  POST /angle (body: {\"angle\": NN})")
    logger.info("  POST /stop")
    
    # Handler de sinais
    def signal_handler(signum, frame):
        logger.info("Encerrando servidor...")
        servo.cleanup()
        server.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido")
    finally:
        servo.cleanup()


if __name__ == "__main__":
    main()

