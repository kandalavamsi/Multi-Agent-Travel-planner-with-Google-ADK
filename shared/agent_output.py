import json
from typing import Any


def parse_agent_output(
    response_text: str,
    required_fields: set[str],
) -> dict[str, Any]:
    # Some model responses incorrectly escape apostrophes as \'.
    cleaned_text = response_text.replace("\\'", "'")
    decoder = json.JSONDecoder()
    result = None

    # Find a JSON object even if the model adds text before or after it.
    for start, character in enumerate(cleaned_text):
        if character != "{":
            continue

        try:
            candidate, _ = decoder.raw_decode(cleaned_text[start:])
        except json.JSONDecodeError:
            continue

        if (
            isinstance(candidate, dict)
            and "options" in candidate
            and "note" in candidate
        ):
            result = candidate
            break

    if result is None:
        raise ValueError("Agent response did not contain a valid options/note JSON object.")

    options = result["options"]
    note = result["note"]

    if not isinstance(options, list):
        raise ValueError("Agent response must contain an options list.")

    if not isinstance(note, str):
        raise ValueError("Agent response must contain a note string.")

    for index, option in enumerate(options):
        if not isinstance(option, dict):
            raise ValueError(f"Option {index + 1} must be a JSON object.")

        missing = required_fields - option.keys()
        if missing:
            raise ValueError(
                f"Option {index + 1} is missing fields: {', '.join(sorted(missing))}."
            )

        for field in required_fields:
            value = option[field]
            if field in {"estimated_price", "price_per_night", "estimated_total", "duration_hours"}:
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    raise ValueError(
                        f"Option {index + 1} field '{field}' must be a number."
                    )
            elif not isinstance(value, str):
                raise ValueError(
                    f"Option {index + 1} field '{field}' must be a string."
                )

    return {"options": options, "note": note}