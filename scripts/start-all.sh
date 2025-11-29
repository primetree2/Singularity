#!/usr/bin/env sh
set -e

echo "==> Starting Singularity (API + Web)"

# Kill background jobs on exit
trap "echo 'Shutting down...'; kill 0" EXIT

echo "Starting API..."
(
  cd apps/api
  pnpm dev &
)

API_PID=$!

echo "Starting Web..."
(
  cd apps/web
  pnpm dev &
)

WEB_PID=$!

echo ""
echo "====================================="
echo " Singularity is now running locally 🚀"
echo "-------------------------------------"
echo " API:    http://localhost:4000"
echo " Web:    http://localhost:3000"
echo "====================================="
echo ""

# Wait indefinitely so trap can catch exit
wait
