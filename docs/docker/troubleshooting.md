# Troubleshooting Docker

## Propósito

Este guia ajuda a resolver:
- Issues de build e runtime do Docker
- Problemas de networking e conectividade
- Issues de performance e recursos
- Problemas de segurança e permissões

# Issues Comuns

## 1. Issues de Build

### Docker Build Falha
```bash
# Erro: Build falhou
# Solução: Verificar sintaxe do Dockerfile e contexto de build
docker build -t test-image ./backend

# Limpar cache de build
docker builder prune -a

# Rebuild sem cache
docker-compose build --no-cache
```

### Sem Espaço Durante o Build
```bash
# Erro: Sem espaço no dispositivo
# Solução: Limpar recursos Docker
docker system prune -a

# Verificar uso de disco
docker system df

# Remover imagens não usadas
docker image prune -a
```

### Permissão Negada Durante o Build
```bash
# Erro: Permissão negada
# Solução: Verificar permissões de ficheiros
sudo chown -R $USER:$USER .

# Verificar permissões do daemon Docker
sudo usermod -aG docker $USER
newgrp docker
```

## 2. Issues de Runtime

### Contentor Não Inicia
```bash
# Verificar status do contentor
docker-compose ps

# Ver logs do contentor
docker-compose logs backend

# Verificar conflitos de porta
netstat -tulpn | grep :5000

# Matar processos conflituantes
sudo kill -9 <PID>
```

### Contentor Cai Imediatamente
```bash
# Ver logs detalhados
docker-compose logs -f backend

# Executar contentor em primeiro plano
docker-compose run --rm backend bash

# Verificar configuração
docker-compose config
```

### Falhas de Health Check
```bash
# Verificar status de saúde
docker-compose ps

# Testar health check manualmente
docker-compose exec backend curl -f http://localhost:5000/health

# Ajustar configuração de health check
# Editar secão healthcheck do docker-compose.yml
```

## 3. Issues de Networking

### Contentor Não Alcança Outros Contentores
```bash
# Verificar configuração de rede
docker network ls

# Testar conectividade
docker-compose exec frontend ping backend

# Verificar resolução DNS
docker-compose exec frontend nslookup backend

# Recriar rede
docker network prune
docker-compose up -d
```

### Issues de Acesso à Rede Externa
```bash
# Testar conectividade externa
docker-compose exec backend ping google.com

# Verificar configurações DNS
docker-compose exec backend cat /etc/resolv.conf

# Configurar DNS no docker-compose.yml
dns:
  - 8.8.8.8
  - 8.8.4.4
```

### Issues de Mapeamento de Portas
```bash
# Verificar bindings de porta
docker port <container_name>

# Testar acessibilidade da porta
telnet localhost 5000

# Verificar configurações de firewall
sudo ufw status
```

## 4. Issues de Volume

### Falha de Montagem de Volume
```bash
# Verificar montagens de volume
docker-compose config

# Verificar permissões de ficheiros
ls -la ./backend

# Corrigir permissões
sudo chown -R $USER:$USER ./backend

# Verificar existência de volume
docker volume ls
```

### Issues de Persistência de Dados
```bash
# Verificar conteúdo do volume
docker-compose exec db ls -la /var/lib/postgresql/data

# Backup de dados do volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restaurar dados do volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 5. Issues de Performance

### Inicialização Lenta de Contentor
```bash
# Verificar tamanho da imagem
docker images

# Otimizar Dockerfile
# Usar builds multi-stage
# Minimizar layers

# Verificar uso de recursos
docker stats
```

### Alto Uso de Memória
```bash
# Monitorizar uso de memória
docker stats --no-stream

# Definir limites de memória
# No docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

### Alto Uso de CPU
```bash
# Monitorizar uso de CPU
docker stats --no-stream

# Definir limites de CPU
# No docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '0.5'
    reservations:
      cpus: '0.25'
```

# Ferramentas de Debugging

## 1. Inspeção de Contentores

### Informações do Contentor
```bash
# Obter detalhes do contentor
docker inspect <container_name>

# Verificar processos do contentor
docker-compose exec backend ps aux

# Verificar variáveis de ambiente
docker-compose exec backend env

# Verificar portas expostas
docker-compose exec backend netstat -tulpn
```

### Inspeção do Sistema de Ficheiros
```bash
# Navegar pelo sistema de ficheiros do contentor
docker-compose exec backend ls -la /

# Copiar ficheiros do contentor
docker cp <container_name>:/app/app.py ./app.py

# Copiar ficheiros para o contentor
docker cp ./app.py <container_name>:/app/app.py
```

## 2. Debugging de Rede

### Análise de Rede
```bash
# Listar redes
docker network ls

# Inspecionar rede
docker network inspect <network_name>

# Testar conectividade
docker-compose exec frontend nc -zv backend 5000

# Capturar tráfego de rede
docker-compose exec backend tcpdump -i eth0
```

### Debugging de DNS
```bash
# Verificar resolução DNS
docker-compose exec backend nslookup google.com

# Testar servidores DNS
docker-compose exec backend nslookup google.com 8.8.8.8

# Verificar ficheiro hosts
docker-compose exec backend cat /etc/hosts
```

## 3. Análise de Performance

### Monitorização de Recursos
```bash
# Monitorização em tempo real
docker stats

# Uso detalhado de recursos
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Uso histórico de recursos
docker system events --since 1h
```

# Procedimentos de Emergência

## 1. Recuperação do Sistema

### Reset Completo do Sistema
```bash
# Parar todos os contentores
docker-compose down

# Remover todos os contentores
docker container rm -f $(docker container ls -aq)

# Remover todas as imagens
docker image rm -f $(docker image ls -aq)

# Limpar sistema
docker system prune -a --volumes

# Reiniciar serviços
docker-compose up -d
```

### Recuperação de Dados
```bash
# Backup de todos os volumes
docker run --rm -v $(docker volume ls -q):/volumes -v $(pwd):/backup alpine tar czf /backup/volumes_backup.tar.gz -C /volumes .

# Restaurar volumes
docker run --rm -v $(docker volume ls -q):/volumes -v $(pwd):/backup alpine tar xzf /backup/volumes_backup.tar.gz -C /volumes
```

# Boas Práticas

## 1. Prevenção

1. **Atualizações Regulares**: Manter Docker e imagens atualizadas
2. **Monitorização de Recursos**: Monitorizar uso de recursos regularmente
3. **Estratégia de Backup**: Backups regulares de dados e configuração
4. **Scanning de Segurança**: Scans de segurança regulares
5. **Documentação**: Documentar todas as configurações e procedimentos

## 2. Manutenção

1. **Limpeza**: Limpeza regular de recursos não usados
2. **Monitorização**: Monitorização contínua da saúde do sistema
3. **Testes**: Testes regulares de procedimentos de backup e recuperação
4. **Atualizações**: Atualizações regulares de dependências
5. **Revisão**: Revisão regular de configurações

---

*Para informação de deploy, ver [production-deployment.md](production-deployment.md).*
