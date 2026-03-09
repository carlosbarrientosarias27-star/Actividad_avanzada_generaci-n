# Actividad Avanzada: Generación de Sistemas y Algoritmos 

Este repositorio contiene una colección de soluciones avanzadas desarrolladas en Python, que van desde la implementación de estructuras de datos optimizadas (Caché LRU) y teoría de grafos, hasta un sistema integral de gestión de tareas con arquitectura modular.

# 📁 Contenido del Repositorio 

El proyecto se divide en 5 bloques principales:

## Bloque 1: Optimización de Memoria 

1.1. Analizar: Estudio inicial del sistema de caché LRU (Least Recently Used).

1.2. Implantación Correcto: Implementación optimizada y funcional del sistema de caché.

## Bloque 2: Teoría de Grafos

PASO 1: Implementación manual de estructuras de grafos dirigidos (Mi grafo dirigido.py).

PASO 2: Implementación asistida o avanzada de grafos (IA_grafo dirigido.py).

## Bloque 3: Control de Tráfico 

sistema de rate limiting.py: Implementación de algoritmos para limitar la tasa de peticiones, esencial para la estabilidad de APIs y servicios.

## Bloque 4: Ingeniería Inversa y Análisis 

4.1. Analiza_código: Scripts destinados al análisis de flujos existentes y lógica de ingeniería inversa.

4.2. Completa el código: Ejercicios de reconstrucción de lógica a partir de binarios o código parcial.

## Bloque 5: Sistema de Gestión de Tareas 

Este es el bloque más robusto, simulando una aplicación real con la siguiente estructura:

auth/: Gestión de tokens JWT y seguridad.

handlers/: Lógica de negocio para usuarios y tareas.

middleware/: Auditoría de registros (logs) y limitadores de velocidad.

models/: Definición de las entidades de datos (Tareas).

db.py & task_manager.db: Capa de persistencia utilizando SQLite.

# 🚀 Guía de Ejecución 

Para ejecutar los módulos correctamente, se recomienda situarse en la raíz del repositorio y usar el flag -m de Python para respetar las rutas de los paquetes.

Ejecutar Algoritmos (Bloques 1 al 4)
Bash

## Ejemplo: Sistema de Rate Limiting

python -m "Bloque 3.sistema de rate limiting"

## Ejemplo: Grafo Dirigido

python -m "Bloque 2.PASO 1.Mi grafo dirigido"
Ejecutar Sistema de Gestión (Bloque 5)
Para iniciar el sistema principal, ejecuta el archivo main.py dentro del Bloque 5:

Bash
python -m "Bloque 5 - Sistema de gestión de tareas.main"

# 🛠️ Requisitos Técnicos 

Python 3.12+ (identificado por los archivos .pyc en la caché).

SQLite: Incluido por defecto en Python para la base de datos task_manager.db.