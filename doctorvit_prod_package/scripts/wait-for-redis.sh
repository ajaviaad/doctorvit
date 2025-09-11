
#!/usr/bin/env bash
set -e
until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q PONG; do
  echo "Waiting for Redis at $REDIS_HOST:$REDIS_PORT..."
  sleep 1
done
echo "Redis is ready."
