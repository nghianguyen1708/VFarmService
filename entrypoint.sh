#!/bin/bash
# entrypoint.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for the PostgreSQL service to be available
until pg_isready -h db -p 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run database migrations
alembic upgrade head

# Execute the CMD from the Dockerfile
exec "$@"