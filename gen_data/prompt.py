import re
import json
import random
import pandas as pd
from typing import Dict, Any, List
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

def clean_and_parse_llm_output(text: str):
    # Step 1: Basic cleaning
    text = text.replace('```python', '').replace('```', '').strip()
    text = text.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")

    # Remove non-printable characters except newline/tab
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t')

    # Step 2: Convert tuples to JSON-style lists using regex
    # Convert (123, 456, "LABEL") → [123, 456, "LABEL"]
    text = re.sub(r'\((\d+),\s*(\d+),\s*"([^"]+)"\)', r'[\1, \2, "\3"]', text)

    # Step 3: Ensure entire structure is valid JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model output as JSON.\n\nCleaned text:\n{text}\n\nError: {e}")

def generate_ner_ds(label2id: Dict[str, int], num_row: int, model_name: str) -> pd.DataFrame:
    if not label2id:
        raise ValueError("label2id dictionary cannot be empty")

    extended_labels = {
        **label2id,
        "IP-Address": len(label2id),
        "Token keys": len(label2id) + 1
    }

    entity_list = list(extended_labels.keys())
    random.shuffle(entity_list)

    prompt = PromptTemplate(
        input_variables=["entity_list", "num_row"],
        template="""
You are an expert in Named Entity Recognition (NER).

Generate {num_row} realistic training examples in the following JSON-safe format:
["Sentence with entities", {{"entities": [[start_char, end_char, "LABEL"], ...]}}]

Rules:
- Each sentence must include random value entities to avoid replication.
- The sentence should be natural and realistic, resembling real-world contexts (e.g., server logs, emails, IT reports, network configurations).
- Use entity labels from this list: {entity_list}
- Each sentence must include:
  - One entity labeled "Token keys" — a long, random alphanumeric string.
  - One entity labeled "IP-Address" — use either IPv4 or IPv6 format.
  - Some entities from the list : {entity_list}
- Return accurate character offsets for each entity.
- Output must be valid JSON — use [ ] instead of ( ) for entities and no extra explanation.
Return a list of examples in this exact format:
[
  ["Sentence1", {{ "entities": [[start, end, "LABEL"], ...] }}],
  ...
]
"""
    )

    model = ChatOpenAI(model_name=model_name)
    chain = prompt | model

    data_dict: List[Dict[str, Any]] = []

    try:
        print("Fetching model response...", flush=True)
        response = chain.invoke({"entity_list": entity_list, "num_row": num_row}).content
        print("Model response received, parsing...", flush=True)
        parsed = clean_and_parse_llm_output(response)

        with open("log.txt", "a", encoding="utf-8") as log_file:
            for i, item in enumerate(parsed, 1):
                if isinstance(item, list) and len(item) == 2:
                    sentence, metadata = item
                    entities = metadata["entities"]
         
                    log_file.write(f"Item {i} Sentence: {sentence}\n")
                    log_file.write(f"Item {i} Entities: {entities}\n")
                    log_file.write("\n")  # Add blank line for readability
                    log_file.flush()  # Ensure immediate write to file
                    data_dict.append({
                        "sentence": sentence,
                        "entities": entities
                    })
                else:
                    raise ValueError(f"Invalid format for item {i}: {item}")

    except Exception as e:
        raise RuntimeError(f"Failed to generate NER examples: {e}")

    return pd.DataFrame(data_dict)