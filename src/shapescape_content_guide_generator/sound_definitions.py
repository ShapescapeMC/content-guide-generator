from sqlite_bedrock_packs import Database, EasyQuery
from .globals import get_db
RP_PATH = 'packs/RP'


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
    q = EasyQuery.build(db, 'SoundDefinition')
    for sound_definition, in q.yield_wrappers():
        nice_name = _nice_sound_name(sound_definition.identifier)
        full = f"{nice_name} ({sound_definition.identifier})"
        result.append(f"- {full}")
    return "\n".join(result)


if __name__ == "__main__":
    main()
