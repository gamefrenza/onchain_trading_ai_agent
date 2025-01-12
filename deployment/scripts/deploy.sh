#!/bin/bash

# Build and deploy the application
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Initialize the database
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -d trading_db -f /docker-entrypoint-initdb.d/init.sql

# Set up SSL certificates
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot -w /var/www/certbot -d your-domain.com

# Reload nginx to apply SSL certificates
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload 