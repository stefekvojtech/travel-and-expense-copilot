from datetime import datetime, timezone
from openai import OpenAI

client = OpenAI()

models = client.models.list()

for model in sorted(models.data, key=lambda m: m.created):
    created_at = datetime.fromtimestamp(model.created, tz=timezone.utc)
    print(f"{created_at:%Y-%m-%d}  {model.id}")