"""Election Night: live countdown to November 3, 2026 (New York time).

Run locally:  streamlit run app.py
"""
from datetime import datetime, time as dtime, timedelta, timezone
from zoneinfo import ZoneInfo

import streamlit as st

st.set_page_config(page_title="Election Night", page_icon="🗳️", layout="centered")

# A lunar clock gains ~56 microseconds per Earth day (see the Moon-clock caption).
LUNAR_RATE = 1 + 56e-6 / 86400

st.markdown(
    """
    <style>
      .block-container {max-width: 760px; padding-top: 2.5rem;}
      .title {text-align:center; font-size:3rem; font-weight:800; letter-spacing:.04em;}
      .sub {text-align:center; opacity:.7; margin-bottom:1.5rem;}
      .row {display:flex; gap:12px; justify-content:center; margin:1rem 0;}
      .box {flex:1; text-align:center; padding:18px 6px; border-radius:14px;
            background:rgba(128,128,128,.12); border:1px solid rgba(128,128,128,.25);}
      .num {font-size:3rem; font-weight:800; font-variant-numeric:tabular-nums; line-height:1.1;}
      .lbl {font-size:.8rem; opacity:.7; text-transform:uppercase; letter-spacing:.12em;}
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


@st.fragment(run_every=1)  # re-runs just this block every second
def countdown():
    now = datetime.now(timezone.utc)          # always measured from "now"
    left = (TARGET - now).total_seconds()

    if left <= 0:
        st.success("Polls are open. The countdown has reached zero.")
        return

    d, rem = divmod(int(left), 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)

    st.markdown(
        '<div class="row">'
        + box(d, "days") + box(f"{h:02d}", "hours")
        + box(f"{m:02d}", "minutes") + box(f"{s:02d}", "seconds")
        + "</div>",
        unsafe_allow_html=True,
    )

    moon_left = left * LUNAR_RATE
    gain_ms = (moon_left - left) * 1000
    st.markdown(
        f'<div class="small">Now (New York): {now.astimezone(ZoneInfo("America/New_York")):%b %-d, %-I:%M:%S %p %Z}'
        f"<br>A clock on the Moon would be ahead by {gain_ms:.3f} ms over this interval.</div>",
        unsafe_allow_html=True,
    )


countdown()
