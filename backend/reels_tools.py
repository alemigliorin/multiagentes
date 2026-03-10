import json
from pathlib import Path


def get_creator_transcripts(creator_name: str) -> str:
    """Gets all video transcripts from a specific creator and returns them in Markdown format.

    Args:
        creator_name: The name of the creator (e.g., 'jeffnippard', 'kallaway', 'rourkeheath')

    Returns:
        A Markdown formatted string containing all transcripts for the creator,
        or an error message if the creator is not found.
    """
    json_path = Path("transcricoes.json")

    if not json_path.exists():
        return f"Error: The file {json_path.absolute()} does not exist."

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        # Normalize the creator name to lowercase to match the JSON keys
        creator_key = creator_name.lower().strip()

        if creator_key not in data:
            available = ", ".join(data.keys())
            return f"Error: Creator '{creator_name}' not found. Available creators are: {available}"

        transcripts = data[creator_key]

        if not transcripts:
            return f"No transcripts found for creator '{creator_name}'."

        output = []
        for index, item in enumerate(transcripts, 1):
            transcript_text = item.get("transcricao", "").strip()

            # Format according to the requested markdown structure
            output.append(f"Transcript {index}")
            output.append(f"{transcript_text}")
            output.append("###\n")

        return "\n".join(output)

    except json.JSONDecodeError:
        return "Error: The JSON file is malformed and could not be read."
    except Exception as e:
        return f"Error reading transcripts: {str(e)}"


def list_available_creators() -> str:
    """Lists the names of all creators available in the database.

    Returns:
        A comma-separated string of creator names.
    """
    json_path = Path("transcricoes.json")

    if not json_path.exists():
        return f"Error: The file {json_path.absolute()} does not exist."

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            return "No creators found."

        return "Available creators: " + ", ".join(data.keys())

    except json.JSONDecodeError:
        return "Error: The JSON file is malformed and could not be read."
    except Exception as e:
        return f"Error reading database: {str(e)}"
