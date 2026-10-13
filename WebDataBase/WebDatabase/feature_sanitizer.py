import hashlib
import re
import unicodedata


_DIRECTION_SYMBOLS = {
    "→": "to",
    "⇒": "to",
    "⟶": "to",
    "➜": "to",
    "←": "from",
    "⇐": "from",
    "⟵": "from",
}
_SEPARATOR_PATTERN = re.compile(r"[-\s]+")


def sanitize_feature_text(value, fallback="feature", max_length=50):
    """Return a stable ASCII identifier safe for GenBank and plot labels."""
    original = "" if value is None else str(value)
    normalized = unicodedata.normalize("NFKC", original).strip()
    safe_parts = []

    for character in normalized:
        if character in _DIRECTION_SYMBOLS:
            safe_parts.append("-" + _DIRECTION_SYMBOLS[character] + "-")
        elif character.isascii() and character.isalnum():
            safe_parts.append(character)
        elif character in ".+-":
            safe_parts.append(character)
        elif character.isspace() or character == "_":
            safe_parts.append("-")
        elif unicodedata.combining(character):
            continue
        elif character.isascii():
            safe_parts.append("-")
        else:
            # Keep non-ASCII text deterministic instead of silently deleting it.
            safe_parts.append("-u{:04x}-".format(ord(character)))

    sanitized = _SEPARATOR_PATTERN.sub("-", "".join(safe_parts)).strip(".-")
    if not sanitized:
        sanitized = fallback

    if len(sanitized) > max_length:
        digest = hashlib.sha1(original.encode("utf-8")).hexdigest()[:8]
        sanitized = sanitized[: max_length - len(digest) - 1].rstrip(".-")
        sanitized = "{}-{}".format(sanitized or fallback, digest)

    return sanitized
