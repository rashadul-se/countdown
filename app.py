"""Election Night: live countdown to November 3, 2026 (New York time).

Run locally:  streamlit run app.py
"""
from datetime import datetime, time as dtime, timedelta, timezone
from zoneinfo import ZoneInfo

import streamlit as st

import moon

st.set_page_config(page_title="Election Night", page_icon="🗳️", layout="centered")

st.markdown(
    """
    <style>
      .block-container {max-width: 760px; padding-top: 2.5rem;}
      .title {text-align:center; font-size:3rem; font-weight:800; letter-spacing:.04em;}
      .sub {text-align:center; opacity:.7; margin-bottom:1.5rem;}
      .row {display:flex; gap:12px; justify-content:center; margin:1rem 0;}
      .box {flex:1; text-align:center; padding:12px 4px; border-radius:14px;
            background:rgba(128,128,128,.12); border:1px solid rgba(128,128,128,.25);}
      .num {font-size:2rem; font-weight:800; font-variant-numeric:tabular-nums; line-height:1.1;}
      .lbl {font-size:.8rem; opacity:.7; text-transform:uppercase; letter-spacing:.12em;}
      .card {padding:14px; border-radius:16px; margin-top:.5rem;
             border:2px solid var(--c); background:rgba(128,128,128,.08);}
      .head {text-align:center; font-weight:800; letter-spacing:.08em; color:var(--c);}
      .clock {text-align:center; font-size:1.5rem; font-weight:700; margin:.4rem 0 .2rem;
              font-variant-numeric:tabular-nums;}
      .small {text-align:center; opacity:.65; font-size:.85rem; margin-top:.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">🗳️ ELECTION NIGHT</div>', unsafe_allow_html=True)

# ---- Settings -------------------------------------------------------------
with st.sidebar:
    st.header("Settings")
    fixed_edt = st.toggle(
        "Force fixed EDT (UTC-4)",
        value=False,
        help="US daylight time ends Nov 1, 2026, so Nov 3 in New York is EST (UTC-5). "
        "Turn this on to count to UTC-4 anyway.",
    )
    target_time = st.time_input("Target time on Nov 3", value=dtime(0, 0))

tz = timezone(timedelta(hours=-4), "EDT") if fixed_edt else ZoneInfo("America/New_York")
TARGET = datetime(2026, 11, 3, target_time.hour, target_time.minute, tzinfo=tz)

st.markdown(
    f'<div class="sub">Counting down to {TARGET:%A, %B %-d, %Y, %-I:%M %p} {TARGET.tzname()}'
    f" ({TARGET.astimezone(timezone.utc):%H:%M} UTC)</div>",
    unsafe_allow_html=True,
)


def box(value, label):
    return f'<div class="box"><div class="num">{value}</div><div class="lbl">{label}</div></div>'


def split(seconds):
    d, rem = divmod(int(seconds), 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    return d, h, m, s


def card(color, title, clock_text, clock_note, seconds_left, precise):
    d, h, m, s = split(seconds_left)
    boxes = box(d, "days") + box(f"{h:02d}", "hrs") + box(f"{m:02d}", "min") + box(f"{s:02d}", "sec")
    return (
        f'<div class="card" style="--c:{color}"><div class="head">{title}</div>'
        f'<div class="clock">{clock_text}</div><div class="small">{clock_note}</div>'
        f'<div class="row">{boxes}</div>'
        f'<div class="small">remaining: {precise}</div></div>'
    )


def precise(seconds):
    d, h, m, s = split(seconds)
    return f"{d}d {h:02d}:{m:02d}:{seconds % 60:07.4f}"


@st.fragment(run_every=1)  # re-runs just this block every second
def countdown():
    now = datetime.now(timezone.utc)          # always measured from "now"
    left = (TARGET - now).total_seconds()

    if left <= 0:
        st.success("Polls are open. The countdown has reached zero.")
        return

    moon_left = moon.moon_remaining(left)
    moon_now = moon.moon_clock_now(now)
    age = moon.lunar_age(now)
    lh, lm = moon.lunar_local_time(age)
    ny_now = now.astimezone(ZoneInfo("America/New_York"))

    earth_col, moon_col = st.columns(2)
    with earth_col:
        st.markdown(
            card("#4aa8ff", "EARTH TIME", f"{ny_now:%-I:%M:%S %p %Z}",
                 f"{ny_now:%a %b %-d, %Y}", left, precise(left)),
            unsafe_allow_html=True,
        )
    with moon_col:
        st.markdown(
            card("#ffc857", "MOON TIME", f"{moon_now:%H:%M:%S.%f}"[:-3] + " UTC",
                 f"Moon clock · lunar solar time {lh:02d}:{lm:02d}", moon_left, precise(moon_left)),
            unsafe_allow_html=True,
        )

    gain_ms = (moon_left - left) * 1000
    drift_ms = (moon_now - now).total_seconds() * 1000
    st.markdown(
        f'<div class="small">Moon: {moon.phase_name(age)}, {moon.illumination(age) * 100:.0f}% lit<br>'
        f"Countdown gap: Moon clock is {gain_ms:.3f} ms ahead over this interval · "
        f"drift since Jan 1, 2026 (assumed sync): {drift_ms:.1f} ms</div>",
        unsafe_allow_html=True,
    )


countdown()
