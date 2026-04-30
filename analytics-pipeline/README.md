# Pipeline de Analítica

## Resumen de la arquitectura
Esta es una canalización de analítica robusta diseñada para ingerir, procesar y reportar eventos de forma eficiente. La arquitectura se divide en varios microservicios para manejar la escala y separar responsabilidades. Una API de ingestión recibe eventos y los encola, mientras que trabajadores en segundo plano procesan esos eventos, gestionan la deduplicación y los persisten en una base de datos PostgreSQL.

Se proporciona una API de reporting para consultar los datos procesados y los agregados, permitiendo una integración sencilla con dashboards o herramientas externas. Redis se utiliza como una cola de mensajería rápida y fiable entre las capas de ingestión y procesamiento, garantizando alto rendimiento.

## Ejecución local
1. Clona el repositorio.
2. Copia `.env.example` a `.env` y ajusta los valores si es necesario.
3. Ejecuta `docker compose up --build -d` para iniciar todos los servicios (PostgreSQL, Redis, API, Worker, Reporting).
4. Ejecuta las migraciones de base de datos (las instrucciones se añadirán más adelante cuando las herramientas estén configuradas).
5. La API estará disponible en `http://localhost:8000` y Reporting en `http://localhost:8001`.

## Interacción de componentes
- **API**: Recibe eventos de los clientes, los valida y los envía a una cola en Redis.
- **Worker**: Consulta la cola de Redis, deduplica los eventos y escribe lotes en la base de datos PostgreSQL.
- **Reporting**: Se conecta exclusivamente a PostgreSQL para servir consultas para dashboards o análisis.
- **PostgreSQL**: Persiste los datos de eventos estructurados, sesiones y agregados diarios pre-calculados.
- **Redis**: Actúa como una cola intermedia que amortigua la carga de ingestión y provee almacenamiento temporal para el estado de deduplicación.

## ¿Por qué Redis para la cola?
Redis se selecciona por su rendimiento en memoria, lo que permite operaciones de push y pop extremadamente rápidas. Esto es crucial para manejar picos de eventos entrantes en la API de ingestión sin descartarlos. Sus estructuras de datos, como Listas o Streams, proporcionan una base sólida para construir una cola sencilla y de alto rendimiento.

## Garantizando entrega al menos una vez
La entrega al menos una vez se asegura haciendo que los workers sean robustos frente a fallos. Cuando un worker obtiene un elemento de Redis, no debería eliminarlo completamente hasta que el lote al que pertenece se haya comprometido con éxito en PostgreSQL (por ejemplo, usando Redis Streams y grupos de consumidores con ACKs explícitos). Si un worker se cae antes de ACKear, otro worker volverá a procesar el mensaje.

## Ejecución de pruebas de carga

Para ejecutar el script de pruebas de carga, ejecuta dentro del directorio `analytics` (o `analytics-pipeline`) los siguientes comandos:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 load_test_example.py http://localhost:8000 --duration 300 --target-rps 20
```
