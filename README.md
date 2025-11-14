# E-Commerce API - Microservicios

## Descripción de la Arquitectura

Este proyecto se migro de una arquitectura **monolítica** a una arquitectura de **microservicios**.

## Requisitos

- Docker Desktop

## Uso

**Levantar servicios:**
```bash
docker compose -f docker-compose.microservices.yml up --build
```

**Verificar que todo esté funcionando**
```bash
curl http://localhost:8080/health
```

**API Docs:**
```
http://localhost:8080/docs
```

**Detener servicios:**
```bash
docker compose -f docker-compose.microservices.yml down
```
