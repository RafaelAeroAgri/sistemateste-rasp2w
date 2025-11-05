#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controle de servo motor via PWM usando pigpio (PWM via hardware).
Suporta movimentação precisa e sweep automático thread-safe.
Usa pigpio para PWM estável sem jitter/flickering.
"""

import threading
import time
from typing import Optional

try:
    import pigpio
    PIGPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    # Permite importar o módulo mesmo fora da Raspberry Pi (para testes)
    PIGPIO_AVAILABLE = False
    print("AVISO: pigpio não disponível. Modo simulação ativado.")


class ServoControl:
    """
    Classe para controlar um servo motor via PWM.
    Usa BCM numbering para os pinos GPIO.
    """
    
    def __init__(self, pin: int, frequency: int = 50, min_duty: float = 2.5, 
                 max_duty: float = 12.5, logger=None):
        """
        Inicializa o controle do servo usando pigpio.
        
        Args:
            pin: Número do pino GPIO (BCM numbering)
            frequency: Frequência PWM em Hz (padrão 50Hz para servos)
            min_duty: Duty cycle mínimo em % (ângulo 0°)
            max_duty: Duty cycle máximo em % (ângulo 180°)
            logger: Instância do logger (opcional)
        """
        self.pin = pin
        self.frequency = frequency
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.logger = logger
        self.current_angle = 90  # Posição inicial padrão
        self.pi = None  # Conexão pigpio
        self.is_initialized = False
        self.sweep_thread = None
        self.stop_sweep_event = threading.Event()
        self.lock = threading.Lock()  # Lock para operações thread-safe
        
        if PIGPIO_AVAILABLE:
            try:
                # Conecta ao daemon pigpiod
                self.pi = pigpio.pi()
                
                if not self.pi.connected:
                    raise RuntimeError("Não foi possível conectar ao pigpiod. Certifique-se que o daemon está rodando.")
                
                # Configura o pino como saída PWM
                self.pi.set_mode(self.pin, pigpio.OUTPUT)
                
                # Define a frequência PWM
                self.pi.set_PWM_frequency(self.pin, self.frequency)
                
                # Move para posição inicial (90°)
                self.set_angle(90)
                
                self.is_initialized = True
                self._log_info(f"Servo inicializado no pino GPIO {self.pin} (BCM) via pigpio")
                
            except Exception as e:
                self._log_error(f"Erro ao inicializar pigpio: {e}", exc_info=True)
                self.is_initialized = False
                if self.pi:
                    self.pi.stop()
                    self.pi = None
        else:
            self._log_warning("pigpio não disponível. Servo em modo simulação.")
    
    def _log_info(self, message: str):
        """Helper para log de info"""
        if self.logger:
            self.logger.info(message)
        else:
            print(f"INFO: {message}")
    
    def _log_warning(self, message: str):
        """Helper para log de warning"""
        if self.logger:
            self.logger.warning(message)
        else:
            print(f"WARNING: {message}")
    
    def _log_error(self, message: str, exc_info=False):
        """Helper para log de erro"""
        if self.logger:
            self.logger.error(message, exc_info=exc_info)
        else:
            print(f"ERROR: {message}")
    
    def angle_to_pulsewidth(self, angle: float) -> int:
        """
        Converte ângulo (0-180°) para pulsewidth em microsegundos.
        pigpio usa pulsewidth (500-2500us) ao invés de duty cycle.
        
        Args:
            angle: Ângulo entre 0 e 180 graus
            
        Returns:
            Pulsewidth correspondente em microsegundos (us)
        """
        # Garante que o ângulo está no range válido
        angle = max(0, min(180, angle))
        
        # Conversão de duty cycle (%) para pulsewidth (us)
        # Para 50Hz (20ms período):
        # min_duty (2.5%) = 500us
        # max_duty (12.5%) = 2500us
        periodo_us = 1000000 / self.frequency  # 20000us para 50Hz
        min_pw = (self.min_duty / 100.0) * periodo_us
        max_pw = (self.max_duty / 100.0) * periodo_us
        
        # Interpolação linear entre min_pw e max_pw
        pulsewidth = int(min_pw + (angle / 180.0) * (max_pw - min_pw))
        return pulsewidth
    
    def set_angle(self, angle: float) -> bool:
        """
        Move o servo para o ângulo especificado usando pigpio.
        
        Args:
            angle: Ângulo desejado (0-180°)
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        if not self.is_initialized:
            self._log_error("Servo não inicializado. Não é possível mover.")
            return False
        
        with self.lock:
            try:
                # Garante que o ângulo está no range válido
                angle = max(0, min(180, angle))
                
                # Calcula o pulsewidth correspondente
                pulsewidth = self.angle_to_pulsewidth(angle)
                
                # Aplica o PWM via pigpio (PWM via hardware - sem jitter)
                if self.pi:
                    self.pi.set_servo_pulsewidth(self.pin, pulsewidth)
                    self.current_angle = angle
                    self._log_info(f"Servo movido para {angle}° (pulsewidth: {pulsewidth}us)")
                    
                    # Pequeno delay para o servo se posicionar
                    time.sleep(0.1)
                    
                    return True
                else:
                    self._log_error("pigpio não conectado")
                    return False
                    
            except Exception as e:
                self._log_error(f"Erro ao mover servo: {e}", exc_info=True)
                return False
    
    def get_angle(self) -> float:
        """
        Retorna o ângulo atual do servo.
        
        Returns:
            Ângulo atual em graus
        """
        return self.current_angle
    
    def sweep(self, from_angle: float, to_angle: float, delay_s: float = 0.5, 
              step: float = 10.0, stop_event: Optional[threading.Event] = None):
        """
        Realiza um sweep (varredura) entre dois ângulos.
        Executa em thread separada para não bloquear.
        
        Args:
            from_angle: Ângulo inicial
            to_angle: Ângulo final
            delay_s: Delay entre cada passo em segundos
            step: Tamanho do passo em graus
            stop_event: Event para parar o sweep (opcional)
        """
        if not self.is_initialized:
            self._log_error("Servo não inicializado. Não é possível fazer sweep.")
            return
        
        # Para qualquer sweep em andamento
        self.stop_sweep()
        
        # Reseta o evento de parada
        self.stop_sweep_event.clear()
        
        # Event a ser usado (externo ou interno)
        event_to_use = stop_event if stop_event else self.stop_sweep_event
        
        def sweep_worker():
            """Worker thread que executa o sweep"""
            try:
                self._log_info(f"Iniciando sweep de {from_angle}° até {to_angle}°")
                
                # Determina a direção do sweep
                if from_angle < to_angle:
                    # Sweep crescente
                    current = from_angle
                    while current <= to_angle and not event_to_use.is_set():
                        self.set_angle(current)
                        time.sleep(delay_s)
                        current += step
                    
                    # Garante que termina exatamente no ângulo final
                    if not event_to_use.is_set():
                        self.set_angle(to_angle)
                else:
                    # Sweep decrescente
                    current = from_angle
                    while current >= to_angle and not event_to_use.is_set():
                        self.set_angle(current)
                        time.sleep(delay_s)
                        current -= step
                    
                    # Garante que termina exatamente no ângulo final
                    if not event_to_use.is_set():
                        self.set_angle(to_angle)
                
                if event_to_use.is_set():
                    self._log_info("Sweep interrompido")
                else:
                    self._log_info("Sweep concluído")
                    
            except Exception as e:
                self._log_error(f"Erro durante sweep: {e}", exc_info=True)
        
        # Inicia o sweep em thread separada
        self.sweep_thread = threading.Thread(target=sweep_worker, daemon=True)
        self.sweep_thread.start()
    
    def stop_sweep(self):
        """
        Para qualquer sweep em andamento.
        """
        if self.sweep_thread and self.sweep_thread.is_alive():
            self._log_info("Parando sweep em andamento...")
            self.stop_sweep_event.set()
            self.sweep_thread.join(timeout=2.0)  # Aguarda até 2 segundos
    
    def is_sweeping(self) -> bool:
        """
        Verifica se há um sweep em andamento.
        
        Returns:
            True se há sweep ativo, False caso contrário
        """
        return self.sweep_thread is not None and self.sweep_thread.is_alive()
    
    def cleanup(self):
        """
        Libera os recursos do pigpio e para o PWM.
        Deve ser chamado antes de encerrar o programa.
        """
        self._log_info("Limpando recursos do servo...")
        
        # Para qualquer sweep em andamento
        self.stop_sweep()
        
        if self.pi and PIGPIO_AVAILABLE:
            try:
                # Para o PWM no pino (define pulsewidth para 0)
                self.pi.set_servo_pulsewidth(self.pin, 0)
                # Fecha a conexão com pigpiod
                self.pi.stop()
                self._log_info("pigpio desconectado com sucesso")
            except Exception as e:
                self._log_error(f"Erro ao limpar pigpio: {e}", exc_info=True)
        
        self.is_initialized = False
    
    def __del__(self):
        """Destrutor: garante limpeza dos recursos"""
        self.cleanup()

