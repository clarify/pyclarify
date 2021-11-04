from datetime import timedelta


def timedelta_isoformat(td: timedelta) -> str:
    """
    ISO 8601 encoding for timedeltas.
    """
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    result = "P"
    if td.days > 0:
        result += f"{td.days}D"
    result += "T" + "".join(
        [
            f"{n:d}{l}"
            for l, n in zip(["H", "M", "S"], [hours, minutes, seconds])
            if n > 0
        ]
    )
    return result
