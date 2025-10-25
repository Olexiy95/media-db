import re
from nanoid import generate
import pandas as pd


def _norm_base(name: str) -> str:
    # normalize for uniqueness: collapse whitespace, lower-case
    return " ".join(name.strip().split()).lower()


# returns (base_name, pseudonym) where base_name has no trailing parenthetical
_PSEUDORE = re.compile(r"^(?P<base>.*?)\s*\((?P<pseudo>[^)]+)\)\s*$")


def _parse_actor(raw: str) -> tuple[str, str | None]:
    s = " ".join(str(raw).strip().split())
    if len(s) < 3:
        return "", None
    m = _PSEUDORE.match(s)
    if m:
        base = m.group("base").strip()
        pseudo = m.group("pseudo").strip()
        if len(base) >= 3:
            return base, pseudo or None
    return s, None


def _get_or_create_actor_id(__self, name: str):
    base, pseudo = _parse_actor(name)
    if not base:
        return ""

    # 1) lookup by BASE NAME only
    row = __self.cursor.execute(
        "SELECT id, pseudonym FROM actors WHERE name = ? COLLATE NOCASE",
        (base,),
    ).fetchone()

    if row:
        actor_id, existing_pseudo = row
        # upgrade pseudonym if we just learned it
        if (existing_pseudo is None or existing_pseudo == "") and pseudo:
            __self.cursor.execute(
                "UPDATE actors SET pseudonym = ? WHERE id = ?",
                (pseudo, actor_id),
            )
        return actor_id


def _parse_years(val: str | float | int) -> tuple[int | None, int | None]:
    """
    Parse year values which might be single years ('2015'),
    ranges ('2015-2022'), open-ended ('2015-'), or junk.
    Returns (start_year, end_year).
    """
    if pd.isna(val):
        return None, None

    s = str(val).strip()
    if not s:
        return None, None

    # Range like '2015-2022' or '2015 - 2022'
    m = re.match(r"^(\d{4})(?:\s*-\s*(\d{4})?)?$", s)
    if m:
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else None
        return start, end

    # Just a single year
    if s.isdigit() and len(s) == 4:
        return int(s), None

    return None, None
