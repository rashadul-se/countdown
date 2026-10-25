"""Moon-time helpers (no Streamlit dependency, so they are easy to test)."""
import math
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
LUNAR_RATE = 1 + 56e-6 / 86400          # lunar seconds per Earth second (~56 µs/day gain)
SYNODIC = 29.530588861                  # days from new moon to new moon
NEW_MOON_REF = datetime(2026, 10, 10, 15, 50, tzinfo=UTC)   # new moon, Oct 10 2026
SYNC_EPOCH = datetime(2026, 1, 1, tzinfo=UTC)               # assumed moment both clocks agreed


def moon_clock_now(now_utc):
    """What a Moon clock reads now, if it matched UTC at SYNC_EPOCH and gains 56 µs/day."""
    return now_utc + (now_utc - SYNC_EPOCH) * (LUNAR_RATE - 1)


def moon_remaining(earth_seconds_left):
    """The same interval measured on the Moon's clock."""
    return earth_seconds_left * LUNAR_RATE


def lunar_age(now_utc):
    return ((now_utc - NEW_MOON_REF).total_seconds() / 86400) % SYNODIC


def lunar_local_time(age):
    """Local solar time at the middle of the Earth-facing side (full moon = noon)."""
    hours = age / SYNODIC * 24
    return int(hours), int((hours % 1) * 60)


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
