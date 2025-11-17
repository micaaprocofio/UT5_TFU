# E-Commerce API - Microservicios

## Descripción de la Arquitectura

Este proyecto se migro de una arquitectura **monolítica** a una arquitectura de **microservicios**.

Cada servicio tiene su propia base de datos PostgreSQL.

## Uso Local (Docker Compose)

```bash
# Iniciar servicios
docker compose -f docker-compose.microservices.yml up --build

# Acceder
http://localhost:8080/docs

# Detener
docker compose -f docker-compose.microservices.yml down
```

## Despliegue en Kubernetes

**Prerequisito:** Asegúrate de que tu cluster de Kubernetes esté corriendo:
- Docker Desktop: Habilita Kubernetes en Preferencias
- minikube: `minikube start`
- kind: `kind create cluster`

```bash
# Verificar cluster
kubectl cluster-info

# Desplegar todo
./deploy-k8s.sh

# Ver estado
kubectl get pods
kubectl get svc

# Acceder a la API
# En minikube (recomendado):
minikube service gateway-service --url
# Te dará una URL tipo: http://127.0.0.1:XXXXX

# En Docker Desktop Kubernetes:
http://localhost:30080/docs

# O usar port-forward al puerto 8080 (más fácil)
./port-forward.sh
# Ahora acceder: http://localhost:8080/docs

# Ver logs
kubectl logs -l app=gateway -f

# Limpiar
./cleanup-k8s.sh
```

## Pruebas

**Nota:** 
- Docker Compose: `http://localhost:8080`
- Kubernetes: `http://localhost:30080`

### Crear producto
```bash
curl -X POST http://localhost:8080/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":1200.50,"stock":5}'
```

### Listar productos
```bash
curl http://localhost:8080/products/
```

### Crear cliente
```bash
curl -X POST http://localhost:8080/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Juan Pérez","email":"juan@example.com"}'
```

### Crear orden
```bash
curl -X POST http://localhost:8080/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"total":1200.50}'
```

### SOAP/XML
```bash
# Listar productos en XML
curl http://localhost:8080/products/soap/list

# Obtener producto específico
curl http://localhost:8080/products/soap/1
```
