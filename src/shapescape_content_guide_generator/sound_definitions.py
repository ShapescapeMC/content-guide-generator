from sqlite_bedrock_packs import yield_from_easy_query, SoundDefinition
from .globals import get_db

def _nice_sound_name(sound: str):
    parts = sound.split(".")
    if len(parts) == 1:
        return parts[0].replace("_", " ").capitalize()
    nice_parts: list[str] = []
    for part in parts:
        nice_parts.append(part.replace("_", " ").capitalize())
    return nice_parts[0] + " - " + " ".join(nice_parts[1:])


def sound_definitions() -> str:
    db = get_db()
    result: list[str] = []
    for sound_definition, in yield_from_easy_query(db, SoundDefinition):
        nice_name = _nice_sound_name(sound_definition.identifier)
        full = f"{nice_name} ({sound_definition.identifier})"
        result.append(f"- {full}")
    return "\n".join(result)
