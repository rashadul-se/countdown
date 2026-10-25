"""Moon-time helpers (no Streamlit dependency, so they are easy to test).

Moon clock = lunar solar time at the middle of the Earth-facing side:
one lunar day (new moon to new moon) is split into 24 lunar hours of 60 lunar
minutes of 60 lunar seconds. Full moon is noon there; new moon is midnight.
"""
import math
from datetime import datetime, timezone

UTC = timezone.utc
SYNODIC = 29.530588861                  # Earth days per lunar day
LUNAR_SECOND = SYNODIC                  # Earth seconds per lunar second (86400 per lunar day)
LUNAR_HOUR = SYNODIC * 3600             # Earth seconds per lunar hour (about 29.5 Earth hours)
LUNAR_DAY = SYNODIC * 86400             # Earth seconds per lunar day
NEW_MOON_REF = datetime(2026, 10, 10, 15, 50, tzinfo=UTC)   # new moon, Oct 10 2026
LUNAR_RATE = 1 + 56e-6 / 86400          # relativistic gain of a lunar-surface clock


def lunar_age(now_utc):
    """Earth days since the last new moon."""
    return ((now_utc - NEW_MOON_REF).total_seconds() / 86400) % SYNODIC


def lunar_clock(now_utc):
    """Lunar solar time as (hours, minutes, seconds) in lunar units."""
    lunar_seconds = lunar_age(now_utc) / SYNODIC * 86400
    h, rem = divmod(lunar_seconds, 3600)
    m, s = divmod(rem, 60)
    return int(h), int(m), s


def lunar_duration(earth_seconds):
    """An Earth-seconds interval expressed in lunar days, hours, minutes, seconds."""
    lunar_seconds = earth_seconds / LUNAR_SECOND
    d, rem = divmod(lunar_seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return int(d), int(h), int(m), s


def illumination(age):
    return (1 - math.cos(2 * math.pi * age / SYNODIC)) / 2


def phase_name(age):
    f = age / SYNODIC
    for limit, name in [(0.02, "New Moon"), (0.23, "Waxing Crescent"), (0.27, "First Quarter"),
                        (0.485, "Waxing Gibbous"), (0.515, "Full Moon"), (0.73, "Waning Gibbous"),
                        (0.77, "Last Quarter"), (0.98, "Waning Crescent")]:
        if f < limit:
            return name
    return "New Moon"
