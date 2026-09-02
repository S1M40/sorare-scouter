import os

with open('docker-compose.yml', 'r') as f:
    content = f.read()

frontend_service = """
  frontend:
    build:
      context: "../ScoutLab Analytics lovable frontend"
      dockerfile: Dockerfile
    container_name: scoutlab_frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - api
    networks:
      - scoutlab_network
"""

content = content.replace('volumes:', frontend_service + '\nvolumes:')

with open('docker-compose.yml', 'w') as f:
    f.write(content)

