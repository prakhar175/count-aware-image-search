from pathlib import Path
import json
def ensure_processed_images(raw_path) -> Path:
    raw_path=Path(raw_path)
    processed_path = raw_path.parent.parent / "processed" / raw_path.name
    processed_path.mkdir(parents=True, exist_ok=True)
    return processed_path
def save_metadata(metadata, raw_path) -> Path:
    processed_path=ensure_processed_images(raw_path)
    output_path=processed_path / "metadata.json"
    with open (output_path, 'w') as F:
        json.dump(metadata,F)
    return output_path