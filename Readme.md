Celery-Prometheus Exporter

## Usage Example

**Prometheus configuration**

```
- job_name: 'celery_exporter'
    metrics_path: /
    dns_sd_configs:
    - names:
      - 'tasks.celery_exporter' # Replace celery_exporter with your exporter container name
      type: 'A'
      port: 8100
```

**Docker-compose** 

```
  rc_celery_exporter:
    image:  *YOUR_REPO*/celery_exporter:latest
    deploy:
      mode: replicated
      replicas: 1
    environment:
      - BROKER_USERNAME=django
      - BROKER_PASSWORD=django
      - BROKER_HOST=rc_rabbit
      - BROKER_PORT=5672
```
