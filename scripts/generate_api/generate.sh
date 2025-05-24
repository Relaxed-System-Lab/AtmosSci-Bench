PROJECT_ROOT=$(dirname "$(dirname "$(dirname "$0")")")
cd "$PROJECT_ROOT"

BASE=openai
MODEL=gpt4o
TOKEN=8000

python3 -m src.generate.generate --base $BASE --model $MODEL --max-tokens $TOKEN --data oeq --type OEQ --retries 1 --parallel 4 --log-level DEBUG
python3 -m src.generate.generate --base $BASE --model $MODEL --max-tokens $TOKEN --data extra_1-10 --type MCQ --retries 1 --parallel 4 --log-level DEBUG
python3 -m src.generate.generate --base $BASE --model $MODEL --max-tokens $TOKEN --data main_1-10 --type MCQ --retries 1 --parallel 4 --log-level DEBUG