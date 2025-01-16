import os
import json

from config import DATA_TEMPLATE_PATH

# Load templates
templates = {}
for file in os.listdir(DATA_TEMPLATE_PATH):
    if not file.endswith(".json"):
        continue
    filename = file[:-5]
    with open(f"{DATA_TEMPLATE_PATH}/{file}", "r") as f:
        templates[filename] = json.load(f)
