#!/bin/bash
set -e

HASH_INPUT_FILES="Dockerfile _src/frontend/environment.yml"

GIT_EVENT="${EVENT_NAME:-manual}"
GIT_REF="${REF_NAME:-dev}"
PR_NUM="${PR_NUMBER:-}"

FORCE_REBUILD=false
CONTAINER_NAME=""
IMAGE_TAG=""
PORT=0

if [[ "$GIT_EVENT" == "manual" ]]; then
  CONTAINER_NAME="yggdrasill-local-dev"
  IMAGE_TAG="yggdrasill:local-dev"
  PORT=8502

elif [[ "$GIT_REF" == "master" && ( "$GIT_EVENT" == "push" || "$GIT_EVENT" == "workflow_dispatch" ) ]]; then
  CONTAINER_NAME="yggdrasill-prod"
  IMAGE_TAG="yggdrasill:prod"
  PORT=8501
  FORCE_REBUILD=true

elif [[ "$GIT_EVENT" == "pull_request" && -n "$PR_NUM" ]]; then
  CONTAINER_NAME="yggdrasill-pr-$PR_NUM"
  IMAGE_TAG="yggdrasill:pr-$PR_NUM"
  PORT=$((8503 + PR_NUM % 31))

else
  SAFE_BRANCH_NAME=$(echo "$GIT_REF" | tr '/' '-' | tr -cd '[:alnum:]-')
  CONTAINER_NAME="yggdrasill-branch-$SAFE_BRANCH_NAME"
  IMAGE_TAG="yggdrasill:branch-$SAFE_BRANCH_NAME"
  HASH_PORT_OFFSET=$(echo -n "$SAFE_BRANCH_NAME" | sha256sum | tr -dc '0-9' | cut -c1-2)
  PORT=$((8533 + HASH_PORT_OFFSET % 67))
fi

CURRENT_HASH=$(cat $HASH_INPUT_FILES | sha256sum | awk '{ print $1 }')
HASH_FILE=".last_image_hash_${CONTAINER_NAME}"

NEEDS_REBUILD=true
if [ -f "$HASH_FILE" ]; then
  LAST_HASH=$(cat "$HASH_FILE")
  if [ "$CURRENT_HASH" = "$LAST_HASH" ] && [ "$FORCE_REBUILD" = false ]; then
    NEEDS_REBUILD=false
  fi
fi

if [ "$NEEDS_REBUILD" = true ]; then
  echo "🛠 Building Docker image: $IMAGE_TAG"
  docker build -t $IMAGE_TAG .
  echo "$CURRENT_HASH" > "$HASH_FILE"
else
  echo "✅ Image unchanged. Skipping rebuild."
fi

docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:8501 \
  -v "$HOME/git/yggdrasill/prod_tree:/vault" \
  $IMAGE_TAG

echo "🚀 Container [$CONTAINER_NAME] running at http://localhost:$PORT"
