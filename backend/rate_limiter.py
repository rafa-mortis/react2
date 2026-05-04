# Sistema de rate limiting para prevenir ataques de força bruta
from collections import defaultdict
import time

class RateLimiter:
    # Classe para implementar rate limiting por IP
    
    def __init__(self, max_requests=5, window_seconds=60):
        self.max_requests = max_requests  # Máximo de requisições
        self.window_seconds = window_seconds  # Janela de tempo em segundos
        self.requests = defaultdict(list)  # Armazenar timestamps das requisições
    
    def is_allowed(self, ip_address: str) -> tuple[bool, int]:
        # Verificar se o IP pode fazer requisições
        now = time.time()
        request_times = self.requests[ip_address]
        
        # Remover requisições antigas (fora da janela)
        request_times[:] = [req_time for req_time in request_times if now - req_time < self.window_seconds]
        
        # Verificar se excedeu o limite
        if len(request_times) >= self.max_requests:
            # Calcular tempo de espera
            oldest_request = min(request_times)
            wait_time = int(self.window_seconds - (now - oldest_request))
            return False, wait_time
        
        # Adicionar requisição atual
        request_times.append(now)
        return True, 0

# Rate limiter global
login_rate_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 requisições em 5 minutos
register_rate_limiter = RateLimiter(max_requests=3, window_seconds=600)  # 3 requisições em 10 minutos
