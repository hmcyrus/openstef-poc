# Docker Development Setup

This directory contains Docker configuration for running the DPDC OpenSTEF FastAPI application in a fully containerized development environment.

## Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (1.29+)

### Running the Application

1. **Build and start the container:**
   ```bash
   docker-compose up --build
   ```

   Or run in detached mode:
   ```bash
   docker-compose up -d --build
   ```

2. **Access the application:**
   Open your browser and navigate to: http://localhost:8080

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

## Development Features

### Hot Reload
The application supports hot reload - any changes you make to the source code will automatically restart the server. The following directories are mounted as volumes:
- Source code (`./` → `/app`)
- Logs (`./logs` → `/app/logs`)
- Trained models (`./trained_models` → `/app/trained_models`)

### Accessing the Container
To access the running container's shell:
```bash
docker-compose exec fastapi-app bash
```

Or if using docker directly:
```bash
docker exec -it dpdc_openstef_dev bash
```

### Installing Additional Packages
If you need to add new Python packages:

1. Add them to `requirements.txt`
2. Rebuild the container:
   ```bash
   docker-compose up --build
   ```

Or install temporarily in the running container:
```bash
docker-compose exec fastapi-app pip install <package-name>
```

## Configuration

### Port Mapping
The application runs on port 8080 inside the container and is mapped to port 8080 on the host. To change the host port, edit `docker-compose.yaml`:
```yaml
ports:
  - "8888:8080"  # Host:Container
```

### Environment Variables
Environment variables can be configured in the `docker-compose.yaml` file under the `environment` section:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=INFO
```

## File Structure

```
dpdc_openstef/
├── Dockerfile              # Docker image definition
├── docker-compose.yaml     # Docker Compose configuration
├── .dockerignore          # Files to exclude from Docker build
└── README.Docker.md       # This file
```

## Troubleshooting

### Container won't start
1. Check if port 8080 is already in use:
   ```bash
   lsof -i :8080  # On Linux/Mac
   netstat -ano | findstr :8080  # On Windows
   ```

2. View container logs:
   ```bash
   docker-compose logs
   ```

### Changes not reflecting
1. Ensure volumes are mounted correctly:
   ```bash
   docker-compose config
   ```

2. Restart the container:
   ```bash
   docker-compose restart
   ```

### Permission issues with logs or trained_models
Create the directories with proper permissions before starting:
```bash
mkdir -p logs trained_models
chmod 777 logs trained_models
```

## Production Considerations

This setup is optimized for **development only**. For production:

1. Remove `--reload` flag from the uvicorn command
2. Use a production-grade WSGI server (e.g., Gunicorn)
3. Don't mount source code as volumes
4. Use environment-specific configuration files
5. Implement proper secrets management
6. Add health checks
7. Use multi-stage builds to reduce image size
8. Run as non-root user

Example production CMD:
```dockerfile
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
```

## Additional Commands

### Rebuild without cache
```bash
docker-compose build --no-cache
docker-compose up
```

### Remove all containers and volumes
```bash
docker-compose down -v
```

### View resource usage
```bash
docker stats dpdc_openstef_dev
```

### Export logs
```bash
docker-compose logs > app_logs.txt
```
