"""
Rail Damage Reporting System - Streamlit Application
ระบบรายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)

Run with:
streamlit run rail_damage_reporting_system_v2.py
"""

from __future__ import annotations

import csv
import json
import os
import random
import re
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

try:
    import pydeck as pdk
except Exception:  # pragma: no cover - fallback for minimal Streamlit installs
    pdk = None


BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DATA_FILE = DATA_DIR / "rail_damage_records.json"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


st.set_page_config(
    page_title="ระบบรายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&display=swap');

:root {
    --navy: #0b2341;
    --navy-2: #123a64;
    --maroon: #7a0019;
    --cream: #f7f1e6;
    --ink: #172033;
    --muted: #667085;
    --line: #e6eaf0;
    --surface: #ffffff;
    --soft: #f5f7fb;
}

html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(122, 0, 25, 0.08), transparent 28rem),
        linear-gradient(180deg, #f8fafc 0%, #eef3f8 100%);
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f6f8fb 100%);
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 10px;
    padding: 8px 10px;
    margin-bottom: 4px;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 24px 28px;
    border-radius: 18px;
    color: #fff;
    background:
        linear-gradient(135deg, rgba(11, 35, 65, 0.98), rgba(18, 58, 100, 0.92)),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.07) 0, rgba(255,255,255,0.07) 1px, transparent 1px, transparent 42px);
    box-shadow: 0 18px 42px rgba(11, 35, 65, 0.22);
    margin-bottom: 22px;
}

.hero:after {
    content: "";
    position: absolute;
    right: -90px;
    top: -90px;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    border: 36px solid rgba(247, 241, 230, 0.12);
}

.hero-kicker {
    font-size: 13px;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #f0d8b6;
    font-weight: 700;
    margin-bottom: 6px;
}

.hero-title {
    font-size: 30px;
    line-height: 1.18;
    font-weight: 800;
    margin: 0 0 4px 0;
}

.hero-subtitle {
    font-size: 15px;
    color: rgba(255,255,255,0.78);
    max-width: 760px;
}

.hero-producer {
    margin-top: 12px;
    display: inline-flex;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(247, 241, 230, 0.12);
    color: #f7f1e6;
    font-size: 13px;
    font-weight: 700;
}

.section-title {
    font-size: 18px;
    font-weight: 800;
    color: var(--navy);
    margin: 18px 0 10px;
    padding-left: 12px;
    border-left: 4px solid var(--maroon);
}

.soft-note {
    color: var(--muted);
    font-size: 13px;
    margin-top: -4px;
    margin-bottom: 12px;
}

[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid rgba(11, 35, 65, 0.08);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 10px 26px rgba(17, 24, 39, 0.07);
}

[data-testid="stMetric"] label {
    color: var(--muted) !important;
}

[data-testid="stMetricValue"] {
    color: var(--navy);
    font-weight: 800;
}

[data-testid="stForm"] {
    background: rgba(255,255,255,0.84);
    border: 1px solid rgba(11, 35, 65, 0.08);
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 12px 34px rgba(17, 24, 39, 0.08);
}

.stButton > button, .stDownloadButton > button {
    border-radius: 10px;
    border: 0;
    font-weight: 700;
    min-height: 42px;
}

.stButton > button[kind="primary"], .stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--maroon), #a31632);
    color: #fff;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    background: #eef2ff;
    color: #193a70;
}

.legend {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 8px 0 12px;
}

.legend-item {
    display: inline-flex;
    gap: 8px;
    align-items: center;
    font-size: 13px;
    color: var(--muted);
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

.empty-panel {
    border: 1px dashed #bcc7d6;
    border-radius: 16px;
    padding: 24px;
    background: rgba(255,255,255,0.72);
    color: var(--muted);
    text-align: center;
}
</style>
""",
    unsafe_allow_html=True,
)


LINES = [
    "สายเหนือ",
    "สายตะวันออกเฉียงเหนือ",
    "สายตะวันออก",
    "สายใต้",
    "สายแม่กลอง",
    "ทางคู่/ทางแยก",
]

TRACK_CLASS = ["ชั้น 1", "ชั้น 2", "ชั้น 3", "ทางหลีก", "ทางประธาน", "ทางแยก"]
TRACK_DIRECTION = ["ทางขึ้น", "ทางล่อง", "ทางเดี่ยว", "ทางคู่", "ทางหลีก"]
TRAFFIC_TYPE = ["โดยสาร/สินค้า", "โดยสาร", "สินค้า", "รถบำรุงทาง", "อื่นๆ"]
ALIGNMENT_OPTIONS = ["ทางตรง", "ทางโค้ง", "ย่านสถานี", "บนสะพาน", "บริเวณประแจ", "อื่นๆ"]
SLOPE_OPTIONS = ["ระดับ", "ลาดขึ้น", "ลาดลง"]
WET_OPTIONS = ["แห้ง", "เปียก", "มีน้ำขัง", "โคลน/ดินอ่อน", "อื่นๆ"]
RAIL_KIND = ["รางธรรมดา", "รางลิ้น", "รางสับประแจ", "รางแม่คู่", "รางปีก", "รางเชื่อมยาว", "อื่นๆ"]
YES_NO = ["ไม่ระบุ", "ใช่", "ไม่ใช่"]

DAMAGE_GROUPS = ["รางหัก", "รางชำรุด", "รางแตกร้าว"]
DAMAGE_TYPES = [
    "Spalling (รอยหลุดร่อน)",
    "Squat (รอยหมอน)",
    "Corrugation (คลื่นรางเป็นลอน)",
    "Flaking / Gauge Corner Cracking (การแตกมุมรางด้านใน)",
    "Wheel Burn (ล้อกัด)",
    "Belgrospi (ขุมสนิม)",
    "Shelling (การแตกมุมรางด้านใน)",
    "Head Check (การแตกเป็นเส้น)",
    "Transverse crack (รอยแตกขวาง)",
    "Longitudinal crack (รอยแตกตามยาว)",
    "Defective weld (รอยเชื่อมชำรุด)",
    "Rail break (รางหัก)",
    "อื่นๆ",
]
DAMAGE_LOCATION = ["หัวราง", "เอวราง", "ฐานราง", "รอยเชื่อม", "ปลายราง", "ประแจ", "อื่นๆ"]
REPAIR_ACTIONS = [
    "จำกัดความเร็ว",
    "ตีปะคับ/ใส่แคล้มป์",
    "ตัดต่อราง",
    "เปลี่ยนราง",
    "เชื่อมซ่อม",
    "อัดหิน/ปรับระดับทาง",
    "ติดตามเฝ้าระวัง",
    "อื่นๆ",
]

SEVERITY_MAP = {
    "low": "ต่ำ - เฝ้าระวัง",
    "medium": "ปานกลาง - ซ่อมตามแผน",
    "high": "สูง - เร่งซ่อม",
    "critical": "วิกฤต - ต้องควบคุมการเดินรถทันที",
}
STATUS_MAP = {
    "pending": "รอตรวจสอบ",
    "in_progress": "กำลังซ่อมแซม",
    "monitoring": "ซ่อมชั่วคราว/เฝ้าระวัง",
    "done": "ซ่อมแซมแล้ว",
}

COLOR_BY_DAMAGE = {
    "รางหัก": [122, 0, 25, 205],
    "รางชำรุด": [224, 130, 0, 200],
    "รางแตกร้าว": [15, 76, 129, 200],
}


def load_records() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_records(records: list[dict[str, Any]]) -> None:
    DATA_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_id(records: list[dict[str, Any]]) -> str:
    year = datetime.now().year
    num = len(records) + 1
    suffix = "".join(chr(random.randint(65, 90)) for _ in range(3))
    return f"RPT-{year}-{num:04d}-{suffix}"


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        text = str(value).strip().replace(",", ".")
        if text == "":
            return None
        return float(text)
    except ValueError:
        return None


def compact_station(record: dict[str, Any]) -> str:
    if record.get("station_from") and record.get("station_to"):
        return f"{record.get('station_from')} - {record.get('station_to')}"
    return record.get("station") or record.get("station_from") or "ไม่ระบุ"


def damage_label(record: dict[str, Any]) -> str:
    return record.get("damage_group") or record.get("type") or "ไม่ระบุ"


def defect_label(record: dict[str, Any]) -> str:
    defects = record.get("defect_types")
    if isinstance(defects, list) and defects:
        return ", ".join(defects)
    return record.get("type") or "ไม่ระบุ"


def save_uploaded_files(report_id: str, uploaded_files: list[Any]) -> list[str]:
    if not uploaded_files:
        return []

    target_dir = UPLOAD_DIR / report_id
    target_dir.mkdir(parents=True, exist_ok=True)
    saved_names: list[str] = []

    for file in uploaded_files:
        safe_name = re.sub(r"[^0-9A-Za-zก-๙._ -]", "_", file.name).strip()
        file_path = target_dir / safe_name
        file_path.write_bytes(file.getbuffer())
        saved_names.append(str(file_path.relative_to(BASE_DIR)))

    return saved_names


def records_to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()

    rows = []
    for record in records:
        rows.append(
            {
                "รหัสรายงาน": record.get("id", ""),
                "วันที่พบเหตุ": record.get("date", ""),
                "เวลา": record.get("time", ""),
                "สาย": record.get("line", ""),
                "ช่วงสถานี": compact_station(record),
                "กม.": record.get("km", ""),
                "ประเภทหลัก": damage_label(record),
                "ลักษณะความเสียหาย": defect_label(record),
                "ตำแหน่งรอยชำรุด": record.get("damage_location", ""),
                "ความรุนแรง": SEVERITY_MAP.get(record.get("severity"), record.get("severity", "")),
                "สถานะ": STATUS_MAP.get(record.get("status"), record.get("status", "")),
                "มาตรการ": record.get("action", ""),
                "หน่วยงาน/เขต": record.get("dept", ""),
                "ผู้รายงาน": record.get("reporter", ""),
                "ละติจูด": record.get("lat", ""),
                "ลองจิจูด": record.get("lng", ""),
            }
        )
    return pd.DataFrame(rows)


def count_series(df: pd.DataFrame, column: str, top: int | None = None) -> pd.DataFrame:
    if df.empty or column not in df.columns:
        return pd.DataFrame(columns=[column, "จำนวน"])
    data = df[column].fillna("ไม่ระบุ").replace("", "ไม่ระบุ").value_counts().reset_index()
    data.columns = [column, "จำนวน"]
    return data.head(top) if top else data


def render_hero() -> None:
    st.markdown(
        """
<div class="hero">
  <div class="hero-kicker">SRT Permanent Way</div>
  <div class="hero-title">ระบบรายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)</div>
  <div class="hero-subtitle">
    บันทึกเหตุจากแบบฟอร์มภาคสนาม ติดตามสถานะการซ่อม และดูพื้นที่เสี่ยงจากสถิติและแผนที่ในหน้าเดียว
  </div>
  <div class="hero-producer">จัดทำโดย กองทางถาวร และกองเทคนิคทางถาวร</div>
</div>
""",
        unsafe_allow_html=True,
    )


def section(title: str, note: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if note:
        st.markdown(f'<div class="soft-note">{note}</div>', unsafe_allow_html=True)


def render_damage_map(records: list[dict[str, Any]]) -> None:
    rows = []
    for record in records:
        lat = as_float(record.get("lat"))
        lon = as_float(record.get("lng") or record.get("lon"))
        if lat is None or lon is None:
            continue
        group = record.get("damage_group") or "รางชำรุด"
        rows.append(
            {
                "lat": lat,
                "lon": lon,
                "id": record.get("id", ""),
                "damage_group": group,
                "station": compact_station(record),
                "km": record.get("km", ""),
                "severity": SEVERITY_MAP.get(record.get("severity"), record.get("severity", "")),
                "status": STATUS_MAP.get(record.get("status"), record.get("status", "")),
                "color": COLOR_BY_DAMAGE.get(group, [80, 90, 110, 190]),
            }
        )

    st.markdown(
        """
<div class="legend">
  <span class="legend-item"><span class="dot" style="background:#7a0019"></span>รางหัก</span>
  <span class="legend-item"><span class="dot" style="background:#e08200"></span>รางชำรุด</span>
  <span class="legend-item"><span class="dot" style="background:#0f4c81"></span>รางแตกร้าว</span>
</div>
""",
        unsafe_allow_html=True,
    )

    if not rows:
        st.markdown(
            '<div class="empty-panel">ยังไม่มีรายการที่ระบุพิกัดละติจูดและลองจิจูดสำหรับแสดงบนแผนที่</div>',
            unsafe_allow_html=True,
        )
        return

    map_df = pd.DataFrame(rows)
    center_lat = float(map_df["lat"].mean())
    center_lon = float(map_df["lon"].mean())

    if pdk is None:
        st.map(map_df.rename(columns={"lon": "longitude", "lat": "latitude"}))
        return

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius=95,
        pickable=True,
        radius_min_pixels=7,
        radius_max_pixels=18,
    )
    tooltip = {
        "html": "<b>{id}</b><br>{damage_group}<br>ช่วงสถานี: {station}<br>กม.: {km}<br>ระดับ: {severity}<br>สถานะ: {status}",
        "style": {"backgroundColor": "#0b2341", "color": "white", "fontFamily": "Sarabun"},
    }
    deck = pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=6, pitch=0),
        layers=[layer],
        tooltip=tooltip,
    )
    st.pydeck_chart(deck, use_container_width=True)


records = load_records()

render_hero()

with st.sidebar:
    st.markdown("### เมนูหลัก")
    menu = st.radio(
        "เลือกหน้าต่างการทำงาน",
        ["แจ้งความเสียหาย", "รายการแจ้งเหตุ", "แดชบอร์ดสถิติ"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Rail Damage Reporting System v2.0")
    st.caption("จัดทำโดย กองทางถาวร และกองเทคนิคทางถาวร")


if menu == "แจ้งความเสียหาย":
    st.markdown("### ส่งรายงานความเสียหายของราง")

    with st.form("new_report_form", clear_on_submit=False):
        section("1. รายการทั่วไป", "ข้อมูลตำแหน่งทางและสภาพทางตามแบบรายงานภาคสนาม")
        col1, col2, col3 = st.columns(3)
        with col1:
            date_input = st.date_input("วันที่ตรวจพบ *")
            line_input = st.selectbox("ทางประธานหรือทางแยก / สาย *", options=LINES)
            track_class_input = st.selectbox("ชั้นของทาง", options=TRACK_CLASS)
            station_from = st.text_input("ระหว่างสถานี จาก *")
        with col2:
            time_input = st.time_input("เวลา *")
            track_direction = st.selectbox("ชนิดของทาง", options=TRACK_DIRECTION)
            traffic_type = st.selectbox("ประเภทการใช้งานทาง", options=TRAFFIC_TYPE)
            station_to = st.text_input("ถึงสถานี *")
        with col3:
            km_input = st.text_input("กม.ที่ *", placeholder="เช่น 145+912")
            telegraph_input = st.text_input("เสาโทรเลข / หลักเขต")
            speed_limit = st.number_input("ความเร็วสูงสุดที่อนุญาต (กม./ชม.)", min_value=0, max_value=200, value=0)
            train_count = st.number_input("จำนวนขบวนรถใน 24 ชม. (รวม)", min_value=0, step=1)

        col4, col5, col6 = st.columns(3)
        with col4:
            alignment = st.selectbox("ลักษณะของทาง", options=ALIGNMENT_OPTIONS)
            curve_radius = st.text_input("รัศมีโค้ง (ม.)")
        with col5:
            slope = st.selectbox("ระดับความลาดชันของทาง", options=SLOPE_OPTIONS)
            wet_condition = st.selectbox("สภาพทางขณะพบเหตุ", options=WET_OPTIONS)
        with col6:
            joint_position = st.text_input("ตำแหน่งรอยต่อ/จุดกึ่งกลางหมอน")
            passenger_freight_count = st.text_input("จำนวนรถโดยสาร/สินค้า (ถ้ามี)")

        section("2. รายละเอียดเกี่ยวกับราง", "ข้อมูลชนิดราง ประวัติการใช้งาน และงานเชื่อม")
        r1, r2, r3 = st.columns(3)
        with r1:
            rail_size = st.text_input("น้ำหนัก/ขนาดของราง", placeholder="เช่น 50N, 54E1, BS80A")
            rail_length = st.text_input("ความยาวราง (ม.)")
            rail_kind = st.selectbox("ชนิดของรางที่พบความเสียหาย", options=RAIL_KIND)
        with r2:
            rail_mark = st.text_input("เครื่องหมาย/ยี่ห้อ/ปี พ.ศ. ของราง")
            rail_laid_date = st.text_input("รางวางเมื่อ")
            prior_turn_or_replace = st.selectbox("เคยกลับหรือเปลี่ยนข้างของรางหรือไม่", options=YES_NO)
        with r3:
            weld_nearby = st.selectbox("จุดหักอยู่ภายใน 10 ซม. จากรอยเชื่อมหรือไม่", options=YES_NO)
            weld_method = st.text_input("วิธีการเชื่อม")
            last_weld_date = st.text_input("เชื่อมครั้งสุดท้ายเมื่อ")

        r4, r5, r6 = st.columns(3)
        with r4:
            ballast_cycle = st.text_input("วาระการอัดหิน", placeholder="เช่น นานๆ ครั้ง / ปานกลาง / บ่อยๆ")
        with r5:
            sleeper_condition = st.text_input("สภาพหมอนรองราง/เครื่องยึดเหนี่ยว")
        with r6:
            rail_weight_loss = st.text_input("น้ำหนักรางเมื่อหัก/น้ำหนักที่หายไป")

        section("3. รายละเอียดเกี่ยวกับรางกันและทาง", "กรณีเกิดในบริเวณรางกัน สะพาน ประแจ หรือทางพิเศษ")
        g1, g2, g3 = st.columns(3)
        with g1:
            guard_area = st.selectbox("ถ้ารางหักอยู่ภายในเหล็กประกับราง", options=YES_NO)
            guard_action = st.text_input("การดำเนินการกับรางกัน/เหล็กประกับ")
        with g2:
            guard_condition = st.text_input("สภาพราง/เหล็กประกับราง")
            tie_plate_condition = st.text_input("แป้นรองราง/เครื่องยึดเหนี่ยว")
        with g3:
            nearby_history = st.text_input("เคยมีรางหักบริเวณใกล้เคียงหรือไม่")
            nearby_km_date = st.text_input("ถ้ามี ระบุ กม. และวันที่")

        section("4. รายละเอียดความเสียหาย", "เลือกประเภทหลักและลักษณะความเสียหายตามรายการในแบบฟอร์ม")
        d1, d2, d3 = st.columns(3)
        with d1:
            damage_group = st.selectbox("ประเภทเหตุหลัก *", options=DAMAGE_GROUPS)
            defect_types = st.multiselect("ลักษณะความเสียหายบริเวณหัวราง/ราง", options=DAMAGE_TYPES)
            other_defect = st.text_input("อื่นๆ ระบุ")
        with d2:
            damage_location = st.selectbox("จุดที่ชำรุด", options=DAMAGE_LOCATION)
            crack_length = st.text_input("ความยาว/ขนาดรอยแตกหรือรอยชำรุด (มม.)")
            temperature = st.text_input("อุณหภูมิขณะพบเหตุ", placeholder="เช่น ร้อน / ปานกลาง / หนาว / 38°C")
        with d3:
            severity_input = st.selectbox(
                "ระดับความรุนแรง *",
                options=list(SEVERITY_MAP.keys()),
                format_func=lambda key: SEVERITY_MAP[key],
                index=1,
            )
            action_input = st.selectbox("มาตรการแก้ไขเบื้องต้น *", options=REPAIR_ACTIONS)
            status_input = st.selectbox(
                "สถานะการซ่อมแซม",
                options=list(STATUS_MAP.keys()),
                format_func=lambda key: STATUS_MAP[key],
            )

        d4, d5 = st.columns(2)
        with d4:
            found_by = st.text_input("ตรวจพบโดย")
            found_context = st.text_area("ขณะตรวจพบ / เหตุการณ์ประกอบ", height=90)
        with d5:
            replacement_rail = st.text_input("รางที่นำมาเปลี่ยนใหม่")
            damage_notes = st.text_area("หมายเหตุ / รายละเอียดเพิ่มเติม", height=90)

        section("5. พิกัดและรูปประกอบ", "กรอกพิกัดเพื่อให้แดชบอร์ดแสดงจุดเกิดเหตุบนแผนที่")
        p1, p2, p3 = st.columns(3)
        with p1:
            lat_input = st.text_input("ละติจูด", placeholder="เช่น 13.7563")
        with p2:
            lng_input = st.text_input("ลองจิจูด", placeholder="เช่น 100.5018")
        with p3:
            drawing_ref = st.text_input("เลขที่รูป/อ้างอิงภาพร่าง")
        uploaded_files = st.file_uploader(
            "แนบภาพถ่ายหรือรูปด้านบน/ด้านข้าง/รูปตัด",
            accept_multiple_files=True,
            type=["png", "jpg", "jpeg", "pdf"],
        )

        section("6. ข้อมูลผู้รายงาน", "กรอกหน่วยงาน/เขตตามหน่วยงานต้นสังกัดหรือพื้นที่รับผิดชอบ")
        u1, u2, u3 = st.columns(3)
        with u1:
            reporter_input = st.text_input("ผู้รายงาน *")
            position_input = st.text_input("ตำแหน่ง")
        with u2:
            dept_input = st.text_input("หน่วยงาน/เขต *", placeholder="เช่น แขวงบำรุงทาง... / นตท....")
            phone_input = st.text_input("เบอร์โทรศัพท์")
        with u3:
            approved_by = st.text_input("ผู้ตรวจ/ผู้รับรอง")
            approved_position = st.text_input("ตำแหน่งผู้ตรวจ/ผู้รับรอง")

        st.markdown("ช่องที่มีเครื่องหมาย * เป็นข้อมูลจำเป็น")
        submit_btn = st.form_submit_button("บันทึกข้อมูลรายงาน", use_container_width=True)

        if submit_btn:
            required_values = {
                "ระหว่างสถานี จาก": station_from,
                "ถึงสถานี": station_to,
                "กม.ที่": km_input,
                "ผู้รายงาน": reporter_input,
            }
            missing = [label for label, value in required_values.items() if not str(value).strip()]
            if missing:
                st.error("กรุณากรอกข้อมูลจำเป็นให้ครบถ้วน: " + ", ".join(missing))
            else:
                report_id = generate_id(records)
                defects = defect_types.copy()
                if other_defect.strip():
                    defects.append(other_defect.strip())
                saved_files = save_uploaded_files(report_id, uploaded_files)

                new_record = {
                    "id": report_id,
                    "date": str(date_input),
                    "time": str(time_input),
                    "line": line_input,
                    "track_class": track_class_input,
                    "track_direction": track_direction,
                    "traffic_type": traffic_type,
                    "station_from": station_from.strip(),
                    "station_to": station_to.strip(),
                    "km": km_input.strip(),
                    "telegraph": telegraph_input.strip(),
                    "speed_limit": speed_limit,
                    "train_count": train_count,
                    "passenger_freight_count": passenger_freight_count.strip(),
                    "alignment": alignment,
                    "curve_radius": curve_radius.strip(),
                    "slope": slope,
                    "wet_condition": wet_condition,
                    "joint_position": joint_position.strip(),
                    "rail_size": rail_size.strip(),
                    "rail_length": rail_length.strip(),
                    "rail_kind": rail_kind,
                    "rail_mark": rail_mark.strip(),
                    "rail_laid_date": rail_laid_date.strip(),
                    "prior_turn_or_replace": prior_turn_or_replace,
                    "weld_nearby": weld_nearby,
                    "weld_method": weld_method.strip(),
                    "last_weld_date": last_weld_date.strip(),
                    "ballast_cycle": ballast_cycle.strip(),
                    "sleeper_condition": sleeper_condition.strip(),
                    "rail_weight_loss": rail_weight_loss.strip(),
                    "guard_area": guard_area,
                    "guard_action": guard_action.strip(),
                    "guard_condition": guard_condition.strip(),
                    "tie_plate_condition": tie_plate_condition.strip(),
                    "nearby_history": nearby_history.strip(),
                    "nearby_km_date": nearby_km_date.strip(),
                    "damage_group": damage_group,
                    "defect_types": defects,
                    "type": defects[0] if defects else damage_group,
                    "damage_location": damage_location,
                    "crack_length": crack_length.strip(),
                    "length_mm": crack_length.strip(),
                    "temperature": temperature.strip(),
                    "severity": severity_input,
                    "action": action_input,
                    "status": status_input,
                    "found_by": found_by.strip(),
                    "found_context": found_context.strip(),
                    "replacement_rail": replacement_rail.strip(),
                    "detail": damage_notes.strip(),
                    "lat": lat_input.strip(),
                    "lng": lng_input.strip(),
                    "drawing_ref": drawing_ref.strip(),
                    "images": saved_files,
                    "reporter": reporter_input.strip(),
                    "position": position_input.strip(),
                    "dept": dept_input,
                    "phone": phone_input.strip(),
                    "approved_by": approved_by.strip(),
                    "approved_position": approved_position.strip(),
                    "createdAt": datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                }
                records.append(new_record)
                save_records(records)
                st.success(f"บันทึกรายงานสำเร็จ รหัสรายงาน: {report_id}")
                st.info("ไปที่หน้าแดชบอร์ดสถิติเพื่อตรวจสอบจำนวนเหตุการณ์ แผนที่ และสถานะซ่อมแซม")


elif menu == "รายการแจ้งเหตุ":
    st.markdown("### รายการรายงานความเสียหายทั้งหมด")

    if not records:
        st.markdown('<div class="empty-panel">ยังไม่มีข้อมูลรายงานในระบบ</div>', unsafe_allow_html=True)
    else:
        df = records_to_dataframe(records)
        output = StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(df.columns.tolist())
        writer.writerows(df.fillna("").values.tolist())

        st.download_button(
            label="ส่งออกข้อมูลทั้งหมดเป็น CSV",
            data=output.getvalue().encode("utf-8-sig"),
            file_name="rail_damage_records.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("#### รายละเอียดและการอัปเดตสถานะ")
        for idx, record in enumerate(records):
            status = STATUS_MAP.get(record.get("status"), "รอตรวจสอบ")
            severity = SEVERITY_MAP.get(record.get("severity"), "ไม่ระบุ")
            title = f"{record.get('id')} | {damage_label(record)} | {compact_station(record)} | กม. {record.get('km', '-')}"

            with st.expander(title):
                a, b, c = st.columns([1.2, 1, 1])
                with a:
                    st.write(f"วันที่พบเหตุ: {record.get('date')} เวลา {record.get('time')}")
                    st.write(f"สาย: {record.get('line')} | ชนิดทาง: {record.get('track_direction', '-')}")
                    st.write(f"ลักษณะความเสียหาย: {defect_label(record)}")
                    st.write(f"ตำแหน่งรอยชำรุด: {record.get('damage_location', '-')}")
                    st.write(f"รายละเอียด: {record.get('detail', '-')}")
                with b:
                    st.write(f"ระดับความรุนแรง: {severity}")
                    st.write(f"สถานะ: {status}")
                    st.write(f"มาตรการ: {record.get('action', '-')}")
                    st.write(f"พิกัด: {record.get('lat', '-')}, {record.get('lng', '-')}")
                    st.write(f"ไฟล์แนบ: {len(record.get('images', []))} ไฟล์")
                with c:
                    st.write(f"ผู้รายงาน: {record.get('reporter', '-')}")
                    st.write(f"ตำแหน่ง: {record.get('position', '-')}")
                    st.write(f"หน่วยงาน/เขต: {record.get('dept', '-')}")
                    st.write(f"โทร: {record.get('phone', '-')}")

                s1, s2 = st.columns([2, 1])
                with s1:
                    current_status = record.get("status", "pending")
                    if current_status not in STATUS_MAP:
                        current_status = "pending"
                    new_status = st.selectbox(
                        "อัปเดตสถานะการซ่อมแซม",
                        options=list(STATUS_MAP.keys()),
                        index=list(STATUS_MAP.keys()).index(current_status),
                        format_func=lambda key: STATUS_MAP[key],
                        key=f"status_{record.get('id')}",
                    )
                with s2:
                    st.write("")
                    st.write("")
                    if st.button("อัปเดตสถานะ", key=f"update_{record.get('id')}", use_container_width=True):
                        records[idx]["status"] = new_status
                        records[idx]["updatedAt"] = datetime.now().isoformat()
                        save_records(records)
                        st.success("อัปเดตสถานะแล้ว")
                        st.rerun()


elif menu == "แดชบอร์ดสถิติ":
    st.markdown("### แดชบอร์ดสถิติและพื้นที่เสี่ยง")

    total = len(records)
    rail_break = sum(1 for r in records if r.get("damage_group") == "รางหัก")
    rail_damage = sum(1 for r in records if r.get("damage_group") == "รางชำรุด")
    rail_crack = sum(1 for r in records if r.get("damage_group") == "รางแตกร้าว")
    urgent = sum(1 for r in records if r.get("severity") in {"high", "critical"})

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("จำนวนเหตุการณ์", f"{total:,}")
    k2.metric("รางหัก", f"{rail_break:,}")
    k3.metric("รางชำรุด", f"{rail_damage:,}")
    k4.metric("รางแตกร้าว", f"{rail_crack:,}")
    k5.metric("เร่งด่วน/วิกฤต", f"{urgent:,}")

    if not records:
        st.markdown('<div class="empty-panel">ยังไม่มีข้อมูลสำหรับสร้างแดชบอร์ด</div>', unsafe_allow_html=True)
    else:
        df = records_to_dataframe(records)

        section("แผนที่จุดเกิดเหตุ", "แสดงตำแหน่งรางหัก รางชำรุด และรางแตกร้าวจากพิกัดที่บันทึก")
        render_damage_map(records)

        section("สถิติพื้นที่เกิดบ่อยและประเภทความเสียหาย")
        left, right = st.columns(2)
        with left:
            st.markdown("#### พื้นที่/หน่วยงานที่เกิดบ่อย")
            area_df = count_series(df, "หน่วยงาน/เขต", top=10).set_index("หน่วยงาน/เขต")
            st.bar_chart(area_df)
        with right:
            st.markdown("#### ประเภทความเสียหาย")
            type_df = count_series(df, "ประเภทหลัก").set_index("ประเภทหลัก")
            st.bar_chart(type_df)

        section("สถานะการซ่อมแซมและระดับความรุนแรง")
        left2, right2 = st.columns(2)
        with left2:
            st.markdown("#### สถานะการซ่อมแซม")
            status_df = count_series(df, "สถานะ").set_index("สถานะ")
            st.bar_chart(status_df)
        with right2:
            st.markdown("#### ระดับความรุนแรง")
            sev_df = count_series(df, "ความรุนแรง").set_index("ความรุนแรง")
            st.bar_chart(sev_df)

        section("ตารางข้อมูลสำหรับติดตามงาน")
        st.dataframe(df, use_container_width=True, hide_index=True)
