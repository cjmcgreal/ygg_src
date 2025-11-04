PR_NUM=2
PORT=$((8500 + PR_NUM))

docker build -t yggdrasill-preview:$PR_NUM .

docker run -d \
  --name yggdrasill-preview-$PR_NUM \
  -p $PORT:8501 \
  yggdrasill-preview:$PR_NUM

echo "Preview running at http://localhost:$PORT"
