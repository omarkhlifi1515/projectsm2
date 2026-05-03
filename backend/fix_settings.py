"""Run this once to update DB LLM settings to Groq."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import database, models
models.Base.metadata.create_all(bind=database.engine)

db = next(database.get_db())

updates = {
    "llm_base_url": "https://api.groq.com/openai/v1",
    "llm_model":    "llama-3.1-8b-instant",
    "llm_api_key":  "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",
}

for key, value in updates.items():
    row = db.query(models.Setting).filter(models.Setting.key == key).first()
    if row:
        row.value = value
        print(f"Updated  {key} = {value}")
    else:
        db.add(models.Setting(key=key, value=value))
        print(f"Inserted {key} = {value}")

db.commit()
db.close()
print("\n✅ Done! Restart the backend now.")
