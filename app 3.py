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


def card(color, title, clock_text, clock_note, boxes, precise_text):
    return (
        f'<div class="card" style="--c:{color}"><div class="head">{title}</div>'
        f'<div class="clock">{clock_text}</div><div class="small">{clock_note}</div>'
        f'<div class="row">{boxes}</div>'
        f'<div class="small">remaining: {precise_text}</div></div>'
    )


@st.fragment(run_every=1)  # re-runs just this block every second
def countdown():
    now = datetime.now(timezone.utc)          # always measured from "now"
    left = (TARGET - now).total_seconds()

    if left <= 0:
        st.success("Polls are open. The countdown has reached zero.")
        return

    # Earth: standard days / hours / minutes / seconds
    d, rem = divmod(int(left), 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    earth_boxes = box(d, "days") + box(f"{h:02d}", "hrs") + box(f"{m:02d}", "min") + box(f"{s:02d}", "sec")
    ny_now = now.astimezone(ZoneInfo("America/New_York"))

    # Moon: lunar solar time, and the same countdown in lunar units
    age = moon.lunar_age(now)
    ch, cm, cs = moon.lunar_clock(now)
    md, mh, mm, ms = moon.lunar_duration(left)
    moon_boxes = (box(md, "lunar days") + box(f"{mh:02d}", "lunar hrs")
                  + box(f"{mm:02d}", "lunar min") + box(f"{int(ms):02d}", "lunar sec"))

    earth_col, moon_col = st.columns(2)
    with earth_col:
        st.markdown(
            card("#4aa8ff", "EARTH TIME", f"{ny_now:%-I:%M:%S %p %Z}", f"{ny_now:%a %b %-d, %Y}",
                 earth_boxes, f"{d}d {h:02d}:{m:02d}:{s:02d}"),
            unsafe_allow_html=True,
        )
    with moon_col:
        st.markdown(
            card("#ffc857", "MOON TIME", f"{ch:02d}:{cm:02d}:{cs:05.2f}",
                 "lunar solar time · full moon = noon",
                 moon_boxes, f"{md}d {mh:02d}:{mm:02d}:{ms:05.2f} (lunar units)"),
            unsafe_allow_html=True,
        )

    relativistic_ms = left * (moon.LUNAR_RATE - 1) * 1000
    st.markdown(
        f'<div class="small">Moon: {moon.phase_name(age)}, {moon.illumination(age) * 100:.0f}% lit<br>'
        f"1 lunar second = {moon.LUNAR_SECOND:.2f} Earth seconds · 1 lunar hour = "
        f"{moon.LUNAR_HOUR / 3600:.1f} Earth hours<br>"
        f"(A lunar-surface atomic clock would also run {relativistic_ms:.3f} ms fast over this interval, not shown.)</div>",
        unsafe_allow_html=True,
    )


countdown()
