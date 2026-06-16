"""
Rail Damage Reporting System - Streamlit Application (Enhanced v2.1)
ระบบรายงานรางชำรุดหักแตกร้าว
"""

import streamlit as st
from datetime import datetime
import json
import os
from pathlib import Path
import random
import csv
import base64
import html
import urllib.error
import urllib.parse
import urllib.request
from io import StringIO
import pandas as pd

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ModuleNotFoundError:
    px = None
    go = None
    PLOTLY_AVAILABLE = False

# ----------------- 1. Page Config -----------------
st.set_page_config(
    page_title="ระบบรายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)",
    page_icon="🛤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- 2. Custom CSS -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif !important;
    }
    .stApp {
        background: linear-gradient(135deg, #e8edf5 0%, #f0f4f8 100%);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a3a6b 0%, #1e4d9e 100%);
        border-right: none;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
        font-size: 15px;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2);
    }
    .topbar-header {
        background: linear-gradient(135deg, #1a3a6b 0%, #2563eb 100%);
        color: white;
        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 18px;
        box-shadow: 0 8px 24px rgba(26,58,107,0.25);
    }
    .topbar-title {
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
        letter-spacing: 0.3px;
    }
    .topbar-sub {
        font-size: 13px;
        opacity: 0.75;
        font-weight: 400;
        margin-top: 3px;
    }
    .topbar-icon {
        font-size: 36px;
        background: rgba(255,255,255,0.15);
        padding: 12px;
        border-radius: 12px;
    }
    .section-header {
        background: white;
        border-left: 5px solid #2563eb;
        padding: 12px 18px;
        border-radius: 0 10px 10px 0;
        margin: 20px 0 16px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .section-header h4 {
        margin: 0;
        color: #1a3a6b;
        font-weight: 700;
        font-size: 16px;
    }
    [data-testid="stMetric"] {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border-top: 4px solid #2563eb;
        transition: transform 0.2s;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #64748b !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        color: #1a3a6b !important;
        font-weight: 800 !important;
    }
    [data-testid="stForm"] {
        background: white;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.07);
        border: 1px solid #e2e8f0;
    }
    [data-testid="stExpander"] {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-family: 'Sarabun', sans-serif !important;
        padding: 8px 18px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #1a3a6b, #2563eb);
        color: white;
        border: none;
        width: 100%;
        padding: 12px;
        font-size: 16px;
        border-radius: 10px;
    }
    .sidebar-logo {
        text-align: center;
        padding: 10px 0 16px 0;
    }
    .sidebar-brand {
        font-size: 14px;
        font-weight: 700;
        color: white;
        margin-top: 8px;
        opacity: 0.9;
    }
    .sidebar-credit {
        font-size: 12px;
        line-height: 1.6;
        opacity: 0.72;
        text-align: center;
        margin-top: 12px;
    }
    .required-note {
        color: #64748b;
        font-size: 13px;
        margin-top: -4px;
        margin-bottom: 14px;
    }
    .form-banner {
        background: linear-gradient(135deg, #0f2f5f 0%, #1d4ed8 100%);
        color: white;
        border-radius: 14px;
        padding: 18px 22px;
        margin: 6px 0 18px 0;
        box-shadow: 0 10px 24px rgba(15, 47, 95, 0.20);
    }
    .form-banner-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .form-banner-sub {
        font-size: 13px;
        opacity: 0.82;
    }
    .form-chip-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin: 0 0 16px 0;
    }
    .form-chip {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e3a8a;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }
    .subtle-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }
    .sync-pill {
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 10px;
        padding: 9px 10px;
        font-size: 12px;
        line-height: 1.45;
        margin: 10px 0;
        text-align: center;
    }
    div[data-testid="stExpander"] details summary p {
        font-weight: 800 !important;
        color: #0f2f5f !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 3. Data / Constants -----------------
APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / 'data' / 'rail_damage_records.json'
DATA_FILE.parent.mkdir(exist_ok=True)

def get_secret_value(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.environ.get(key, default)

GITHUB_REPO = get_secret_value("GITHUB_REPO")
GITHUB_TOKEN = get_secret_value("GITHUB_TOKEN")
GITHUB_BRANCH = get_secret_value("GITHUB_BRANCH", "main")
GITHUB_DATA_PATH = get_secret_value("GITHUB_DATA_PATH", "data/rail_damage_records.json")

def github_storage_enabled():
    return bool(GITHUB_REPO and GITHUB_TOKEN and GITHUB_DATA_PATH)

def github_api_request(url, method="GET", payload=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "User-Agent": "rail-damage-reporting-system",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))

def load_records_from_github():
    if not github_storage_enabled():
        return None

    path = urllib.parse.quote(str(GITHUB_DATA_PATH).strip("/"))
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    try:
        data = github_api_request(url)
        content = base64.b64decode(data.get("content", "")).decode("utf-8")
        return json.loads(content) if content.strip() else []
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        st.warning("ไม่สามารถอ่านข้อมูลกลางได้ชั่วคราว ระบบจะแสดงข้อมูลจากเครื่องนี้ก่อน")
        return None
    except Exception:
        st.warning("ไม่สามารถเชื่อมต่อข้อมูลกลางได้ชั่วคราว ระบบจะแสดงข้อมูลจากเครื่องนี้ก่อน")
        return None

def save_records_to_github(records):
    if not github_storage_enabled():
        return False

    path = urllib.parse.quote(str(GITHUB_DATA_PATH).strip("/"))
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    sha = None

    try:
        current = github_api_request(f"{url}?ref={GITHUB_BRANCH}")
        sha = current.get("sha")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise

    payload = {
        "message": "Update rail damage records",
        "content": base64.b64encode(
            json.dumps(records, ensure_ascii=False, indent=2).encode("utf-8")
        ).decode("ascii"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    github_api_request(url, method="PUT", payload=payload)
    return True

def load_records():
    remote_records = load_records_from_github()
    if remote_records is not None:
        return remote_records

    if DATA_FILE.exists():
        with DATA_FILE.open('r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_records(records):
    DATA_FILE.parent.mkdir(exist_ok=True)
    with DATA_FILE.open('w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    if github_storage_enabled():
        try:
            save_records_to_github(records)
        except Exception:
            st.warning("บันทึกในเครื่องนี้แล้ว แต่ยังส่งข้อมูลไปแหล่งข้อมูลกลางไม่สำเร็จ กรุณาลองอัปเดตอีกครั้ง")

def generate_id():
    recs = load_records()
    year = datetime.now().year
    existing_nums = []
    for rec in recs:
        parts = str(rec.get('id', '')).split('-')
        if len(parts) >= 3 and parts[0] == 'RPT' and parts[1] == str(year):
            try:
                existing_nums.append(int(parts[2]))
            except ValueError:
                pass
    num = (max(existing_nums) + 1) if existing_nums else 1
    suffix = ''.join([chr(random.randint(65, 90)) for _ in range(3)])
    return f'RPT-{year}-{num:04d}-{suffix}'

def save_uploaded_files(uploaded_files, record_id):
    if not uploaded_files:
        return []

    upload_dir = APP_DIR / 'data' / 'uploads' / record_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        raw_name = Path(uploaded_file.name).name
        safe_name = ''.join(
            ch if ch.isalnum() or ch in ('-', '_', '.') else '_'
            for ch in raw_name
        ).strip('_') or f'attachment_{idx}'
        target = upload_dir / f"{idx:02d}_{safe_name}"
        target.write_bytes(uploaded_file.getbuffer())
        saved_files.append(str(target.relative_to(APP_DIR)))

    return saved_files

def option_index(options, value, default=0):
    try:
        return options.index(value)
    except ValueError:
        return default

def parse_date_value(value):
    try:
        return datetime.fromisoformat(str(value)).date()
    except Exception:
        return datetime.today().date()

def parse_time_value(value):
    try:
        return datetime.strptime(str(value).split('.')[0], "%H:%M:%S").time()
    except Exception:
        try:
            return datetime.strptime(str(value), "%H:%M").time()
        except Exception:
            return datetime.now().time()

def build_bt27_report_text(record):
    fd = record.get('formDetails', {})
    head_damage = ', '.join(fd.get('headDamage', [])) if fd.get('headDamage') else '-'
    attachments = fd.get('attachments', [])

    lines = [
        "รายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)",
        "=" * 58,
        f"เลขที่รายงาน: {fd.get('reportNo') or record.get('id', '-')}",
        f"เลขที่ระบบ: {record.get('id', '-')}",
        f"วันที่/เวลา: {record.get('date', '-')} เวลา {record.get('time', '-')}",
        f"สถานะรายงาน: {fd.get('reportStatus', '-')}",
        f"ได้เปลี่ยนแล้วเสร็จเมื่อ: {fd.get('completedReplaceAt', '-')}",
        "",
        "1-10 รายการทั่วไป",
        f"สายทาง: {record.get('line', '-')}",
        f"ประเภททาง: {fd.get('mainBranch', '-')}",
        f"ชั้นของทาง: {fd.get('trackClass', '-')}",
        f"ชนิดของทาง: {fd.get('trackDirection', '-')}",
        f"ลักษณะการเดินรถ: {fd.get('serviceTrack', '-')}",
        f"ชนิดแรงขับ: {fd.get('traction', '-')}",
        f"ระหว่างสถานี: {fd.get('stationFrom', '-')} - {fd.get('stationTo', '-')}",
        f"สถานีใกล้เคียง/ช่วงสถานี: {record.get('station', '-')}",
        f"กม.: {record.get('km', '-')}",
        f"ลักษณะทาง: {fd.get('alignment', '-')} | รัศมี/รายละเอียด: {fd.get('curveRadius', '-')}",
        f"สภาพทาง: {fd.get('wetDry', '-')}",
        f"ระดับความลาดชัน: {fd.get('grade', '-')}",
        f"จุดรถล้อหล่อ/เคลื่อนขบวน: {fd.get('wheelFlatRemark', '-')}",
        f"จำนวนขบวน/24 ชม.: ผู้โดยสาร {fd.get('trainPassenger24h', 0)} | สินค้า {fd.get('trainFreight24h', 0)} | รวม {fd.get('trainTotal24h', 0)}",
        f"ความเร็วสูงสุดที่อนุญาต: {fd.get('speedLimit', '-')}",
        "",
        "11-19 รายละเอียดเกี่ยวกับราง",
        f"ขนาด/น้ำหนักราง: {fd.get('railSize', '-')}",
        f"ความยาวราง: {fd.get('railLength', '-')}",
        f"รางเชื่อมยาว: {fd.get('cwrLength', '-')}",
        f"ชนิดของรางที่หัก: {fd.get('brokenRailType', '-')}",
        f"เคยกลับ/เปลี่ยนข้างราง: {fd.get('railSideHistory', '-')}",
        f"น้ำหนักรางเมื่อหัก: {fd.get('railWeightAtBreak', '-')}",
        f"น้ำหนักที่หายไป: {fd.get('railWeightLoss', '-')}",
        f"เครื่องหมายราง: {fd.get('railMark', record.get('railId', '-'))}",
        f"วางรางเมื่อ: {fd.get('railLaidDate', '-')}",
        f"สภาพรางเดิม: {fd.get('railCondition', '-')}",
        f"วิธีเชื่อมใกล้จุดหัก: {fd.get('weldMethod', '-')}",
        f"เชื่อมครั้งสุดท้าย: {fd.get('weldLastDate', '-')}",
        f"จำนวนครั้งที่ซ่อม: {fd.get('weldRepairCount', '-')}",
        f"หินโรยทาง: {fd.get('ballast', '-')}",
        f"วาระการอัดหิน: {fd.get('tampingFrequency', '-')}",
        "",
        "20-22 รายละเอียดเกี่ยวกับทางและเหล็กประกบราง",
        f"การตัด/เปลี่ยนราง: {fd.get('jointCutMethod', '-')}",
        f"สภาพผิวสัมผัสเหล็กประกบ: {fd.get('jointContactCondition', '-')}",
        f"รูสลักเกลียวต่อราง: {fd.get('boltHole', '-')}",
        f"ชนิดเหล็กประกบราง: {fd.get('fishplateType', '-')}",
        f"สภาพเหล็กประกบราง: {fd.get('fishplateCondition', '-')}",
        f"ชนิดและสภาพหมอน: {fd.get('sleeperCondition', '-')}",
        f"ประวัติรางหักในระยะใกล้เคียง: {fd.get('nearbyBreakRecord', '-')}",
        "",
        "23-28 รายละเอียดเกี่ยวกับรางชำรุด หัก แตกร้าว",
        f"ประเภทเหตุ: {record.get('type', '-')}",
        f"ระดับความรุนแรง: {SEVERITY_MAP.get(record.get('severity'), record.get('severity', '-'))}",
        f"ความยาว/ขนาดชำรุด: {record.get('length', '-')}",
        f"ตรวจพบโดย: {fd.get('foundBy', '-')}",
        f"ตำแหน่งที่พบ: {fd.get('foundPosition', '-')}",
        f"ขณะตรวจพบ: {fd.get('foundContext', '-')}",
        f"อุณหภูมิขณะพบ: {fd.get('railTemperature', '-')}",
        f"ลักษณะรอยร้าว: {fd.get('crackAge', '-')}",
        f"มีรอยล้อกระแทก: {fd.get('wheelImpact', '-')}",
        f"รางที่นำมาเปลี่ยน: ขนาด {fd.get('replacementRailSize', '-')} | ยาว {fd.get('replacementRailLength', '-')} | ประเภท {fd.get('replacementRailType', '-')}",
        f"การชำรุดเสียหายบริเวณหัวราง: {head_damage}",
        f"อื่นๆ: {fd.get('headDamageOther', '-')}",
        "",
        "พิกัด/หมายเหตุ/การดำเนินการ",
        f"พิกัด: {record.get('lat', '-')} , {record.get('lon', '-')}",
        f"หมายเหตุ: {fd.get('note', '-')}",
        f"การดำเนินการเบื้องต้น: {record.get('action', '-')}",
        f"ไฟล์แนบ: {len(attachments)} ไฟล์",
        "",
        "ข้อมูลผู้รายงาน",
        f"ผู้รายงาน: {record.get('reporter', '-')}",
        f"ตำแหน่ง: {record.get('position', '-')}",
        f"หน่วยงาน/เขต: {record.get('dept', '-')}",
        f"เบอร์โทรศัพท์: {record.get('phone', '-')}",
        f"วิศวกร/ผู้รับรอง: {fd.get('certifier', '-')}",
        "",
        f"สร้างรายงานเมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    return "\n".join(lines)

def build_bt27_report_html(record):
    report_text = build_bt27_report_text(record)
    escaped = html.escape(report_text)
    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <title>รายงาน บท.27 {html.escape(record.get('id', ''))}</title>
  <style>
    body {{ font-family: Tahoma, Arial, sans-serif; margin: 32px; color: #111827; }}
    .sheet {{ max-width: 960px; margin: auto; }}
    h1 {{ font-size: 22px; text-align: center; margin-bottom: 4px; }}
    .meta {{ text-align: center; color: #4b5563; margin-bottom: 24px; }}
    pre {{ white-space: pre-wrap; font-family: Tahoma, Arial, sans-serif; line-height: 1.65; font-size: 14px; }}
    @media print {{ body {{ margin: 12mm; }} }}
  </style>
</head>
<body>
  <div class="sheet">
    <h1>รายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)</h1>
    <div class="meta">เลขที่ระบบ {html.escape(record.get('id', '-'))}</div>
    <pre>{escaped}</pre>
  </div>
</body>
</html>"""

def save_report_files(record):
    report_dir = APP_DIR / 'data' / 'reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in record.get('id', 'report'))
    txt_content = build_bt27_report_text(record)
    html_content = build_bt27_report_html(record)
    json_content = json.dumps(record, ensure_ascii=False, indent=2)

    (report_dir / f"{stem}.txt").write_text(txt_content, encoding='utf-8')
    (report_dir / f"{stem}.html").write_text(html_content, encoding='utf-8')
    (report_dir / f"{stem}.json").write_text(json_content, encoding='utf-8')

    return {
        'id': record.get('id', ''),
        'txt': txt_content,
        'html': html_content,
        'json': json_content,
        'stem': stem,
    }

def render_report_downloads(report_data, show_message=True):
    if not report_data:
        return
    if show_message:
        st.success(f"สร้างไฟล์รายงาน บท.27 เรียบร้อย: {report_data.get('id', '')}")
    d1, d2, d3 = st.columns(3)
    d1.download_button(
        "ดาวน์โหลดรายงาน TXT",
        data=report_data['txt'].encode('utf-8-sig'),
        file_name=f"{report_data['stem']}_BT27.txt",
        mime="text/plain",
        use_container_width=True,
    )
    d2.download_button(
        "ดาวน์โหลดรายงาน HTML",
        data=report_data['html'].encode('utf-8'),
        file_name=f"{report_data['stem']}_BT27.html",
        mime="text/html",
        use_container_width=True,
    )
    d3.download_button(
        "ดาวน์โหลดข้อมูล JSON",
        data=report_data['json'].encode('utf-8'),
        file_name=f"{report_data['stem']}_BT27.json",
        mime="application/json",
        use_container_width=True,
    )

# ---- หน่วยงานจากไฟล์ Excel ----
DEPARTMENTS = [
    "ศูนย์อาคารและสถานที่",
    "กองบำรุงอาคารสถานที่เขตกรุงเทพ",
    "พสถ.กรุงเทพ", "พสถ.มักกะสัน", "พสถ.หัวตะเข้",
    "งานสถานที่บางซื่อ", "พสถ.บางซื่อ", "พสถ.ธนบุรี", "พสถ.กม.๑๑",
    "ศูนย์บำรุงทางภาคกลาง",
    "งานเครื่องกลบำรุงทางหนักกรุงเทพ",
    "กองบำรุงทางเขตกรุงเทพ",
    "แขวงบำรุงทางกรุงเทพ",
    "นตท.กรุงเทพ", "นตท.มักกะสัน", "นตท.หัวหมาก", "นตท.ลาดกระบัง",
    "นตท.หัวตะเข้", "นตท.สมุทรสาคร",
    "แขวงบำรุงทางบางซื่อ",
    "นตท.บางซื่อ", "นตท.กรุงเทพอภิวัฒน์", "นตท.ธนบุรี",
    "นตท.ศาลายา", "นตท.ย่านพหลโยธิน",
    "แขวงบำรุงทางนครปฐม",
    "นตท.นครชัยศรี", "นตท.นครปฐม", "นตท.บ้านโป่ง",
    "นตท.ยางประสาท", "นตท.สุพรรณบุรี", "พสถ.นครปฐม",
    "กองบำรุงทางเขตฉะเชิงเทรา",
    "แขวงบำรุงทางฉะเชิงเทรา",
    "นตท.เปรง", "นตท.ฉะเชิงเทรา", "นตท.ดอนสีนนท์", "นตท.ชลบุรี",
    "พสถ.ฉะเชิงเทรา",
    "แขวงบำรุงทางปราจีนบุรี",
    "นตท.คลองสิบเก้า", "นตท.ปราจีนบุรี", "นตท.องครักษ์",
    "นตท.วิหารแดง", "นตท.บ้านไผ่นาบุญ", "พสถ.ปราจีนบุรี",
    "แขวงบำรุงทางวัฒนานคร",
    "นตท.ประจันตคาม", "นตท.กบินทร์บุรี", "นตท.สระแก้ว",
    "นตท.วัฒนานคร", "นตท.อรัญประเทศ", "พสถ.อรัญประเทศ",
    "แขวงบำรุงทางศรีราชา",
    "นตท.บางพระ", "นตท.ศรีราชา", "นตท.พัทยา", "นตท.บ้านพลูตาหลวง",
    "พสถ.ศรีราชา",
    "กองบำรุงทางเขตหัวหิน",
    "แขวงบำรุงทางกาญจนบุรี",
    "นตท.ท่าเรือน้อย", "นตท.กาญจนบุรี", "นตท.ท่ากิเลน",
    "นตท.วังโพ", "พสถ.กาญจนบุรี",
    "แขวงบำรุงทางเพชรบุรี",
    "นตท.ราชบุรี", "นตท.ปากท่อ", "นตท.เพชรบุรี",
    "นตท.บ้านชะอำ", "นตท.สมุทรสงคราม", "พสถ.เพชรบุรี",
    "แขวงบำรุงทางวังก์พง",
    "นตท.หัวหิน", "นตท.ปราณบุรี", "นตท.สามร้อยยอด",
    "นตท.กุยบุรี", "นตท.ประจวบคีรีขันธ์", "พสถ.หัวหิน",
    "ศูนย์บำรุงทางภาคเหนือ",
    "งานเครื่องกลบำรุงทางหนักตะพานหิน",
    "กองบำรุงทางเขตนครสวรรค์",
    "แขวงบำรุงทางอยุธยา",
    "นตท.ดอนเมือง", "นตท.เชียงราก", "นตท.เชียงรากน้อย",
    "นตท.บางปะอิน", "นตท.อยุธยา", "พสถ.อยุธยา",
    "แขวงบำรุงทางลพบุรี",
    "นตท.ท่าเรือ", "นตท.หนองโดน", "นตท.ลพบุรี",
    "นตท.โคกกะเทียม", "พสถ.ลพบุรี",
    "แขวงบำรุงทางนครสวรรค์",
    "นตท.บ้านหมี่", "นตท.บ้านตาคลี", "นตท.เนินมะกอก",
    "นตท.นครสวรรค์", "นตท.ชุมแสง", "พสถ.นครสวรรค์",
    "แขวงบำรุงทางพิษณุโลก",
    "นตท.บางมูลนาก", "นตท.ตะพานหิน", "นตท.ท่าฬ่อ",
    "นตท.พิษณุโลก", "นตท.แควน้อย", "พสถ.พิษณุโลก",
    "กองบำรุงทางเขตลำปาง",
    "แขวงบำรุงทางอุตรดิตถ์",
    "นตท.หนองตม", "นตท.ตรอน", "นตท.สวรรคโลกที่บ้านดารา",
    "นตท.ศิลาอาสน์", "พสถ.ศิลาอาสน์",
    "แขวงบำรุงทางเด่นชัย",
    "นตท.ปางต้นผึ้ง", "นตท.เด่นชัย", "นตท.บ้านปิน",
    "นตท.ผาคัน", "พสถ.เด่นชัย",
    "แขวงบำรุงทางลำปาง",
    "นตท.แม่จาง", "นตท.แม่เมาะ", "นตท.ลำปาง",
    "นตท.ห้างฉัตร", "พสถ.ลำปาง",
    "แขวงบำรุงทางลำพูน",
    "นตท.ขุนตาน", "นตท.ศาลาแม่ทา", "นตท.ลำพูน",
    "นตท.เชียงใหม่", "พสถ.เชียงใหม่",
    "ศูนย์บำรุงทางภาคตะวันออกเฉียงเหนือ",
    "งานเครื่องกลบำรุงทางหนักแก่งคอย",
    "งานเครื่องกลบำรุงทางหนักนครราชสีมา",
    "กองบำรุงทางเขตสุรินทร์",
    "แขวงบำรุงทางแก่งคอย",
    "นตท.หนองแซง", "นตท.สระบุรี", "นตท.แก่งคอย",
    "นตท.มวกเหล็ก", "นตท.ปางอโศก", "พสถ.แก่งคอย",
    "แขวงบำรุงทางนครราชสีมา",
    "นตท.ปากช่อง", "นตท.สีคิ้ว", "นตท.กุดจิก",
    "นตท.นครราชสีมา", "นตท.โนนสูง", "พสถ.นครราชสีมา",
    "แขวงบำรุงทางลำปลายมาศ",
    "นตท.จักราช", "นตท.ห้วยแถลง", "นตท.ลำปลายมาศ",
    "นตท.บุรีรัมย์", "นตท.สุรินทร์", "พสถ.ลำชี",
    "แขวงบำรุงทางศรีสะเกษ",
    "นตท.ศรีขรภูมิ", "นตท.สำโรงทาบ", "นตท.ศรีสะเกษ",
    "นตท.กันทรารมย์", "นตท.อุบลราชธานี", "พสถ.ศรีสะเกษ",
    "กองบำรุงทางเขตขอนแก่น",
    "แขวงบำรุงทางลำนารายณ์",
    "นตท.หินซ้อน", "นตท.โคกสลุง", "นตท.ลำนารายณ์",
    "นตท.โคกคลี", "นตท.บ้านวะตะแบก", "พสถ.ลำนารายณ์",
    "แขวงบำรุงทางบัวใหญ่",
    "นตท.บำเหน็จณรงค์", "นตท.จัตุรัส", "นตท.บ้านเหลื่อม",
    "นตท.บัวใหญ่", "นตท.เมืองคง", "พสถ.บัวใหญ่",
    "แขวงบำรุงทางขอนแก่น",
    "นตท.หนองบัวลายที่เมืองพล", "นตท.บ้านหัน", "นตท.บ้านไผ่",
    "นตท.ขอนแก่น", "นตท.โนนพยอม", "พสถ.ขอนแก่น",
    "แขวงบำรุงทางอุดรธานี",
    "นตท.น้ำพอง", "นตท.โนนสะอาด", "นตท.หนองตะไก้",
    "นตท.อุดรธานี", "นตท.นาทา", "พสถ.อุดรธานี",
    "ศูนย์บำรุงทางภาคใต้",
    "งานเครื่องกลบำรุงทางหนักชุมพร",
    "งานเครื่องกลบำรุงทางหนักหาดใหญ่",
    "กองบำรุงทางเขตทุ่งสง",
    "แขวงบำรุงทางบ้านกรูด",
    "นตท.ทับสะแก", "นตท.บางสะพานใหญ่", "นตท.บางสะพานน้อย",
    "นตท.มาบอำมฤต", "นตท.ปะทิว", "พสถ.บ้านกรูด",
    "แขวงบำรุงทางชุมพร",
    "นตท.ชุมพร", "นตท.สวี", "นตท.หลังสวน",
    "นตท.ท่าชนะ", "นตท.ไชยา", "พสถ.ชุมพร",
    "แขวงบำรุงทางบ้านส้อง",
    "นตท.ท่าฉาง", "นตท.คีรีรัฐนิคม", "นตท.สุราษฎร์ธานี",
    "นตท.บ้านนา", "นตท.บ้านส้อง", "พสถ.บ้านส้อง",
    "แขวงบำรุงทางทุ่งสง",
    "นตท.ทานพอ", "นตท.ทุ่งสง", "นตท.ที่วัง",
    "นตท.ห้วยยอด", "นตท.ตรัง", "พสถ.ทุ่งสง",
    "กองบำรุงทางเขตหาดใหญ่",
    "แขวงบำรุงทางเขาชุมทอง",
    "นตท.ร่อนพิบูลย์", "นตท.เขาชุมทอง", "นตท.นครศรีธรรมราช",
    "นตท.ชะอวด", "นตท.พัทลุง", "พสถ.เขาชุมทอง",
    "แขวงบำรุงทางหาดใหญ่",
    "นตท.บางแก้ว", "นตท.ควนเนียง", "นตท.หาดใหญ่",
    "นตท.คลองแงะ", "พสถ.หาดใหญ่",
    "แขวงบำรุงทางเทพา",
    "นตท.นาม่วง", "นตท.จะนะ", "นตท.ปัตตานี",
    "นตท.ยะลา", "พสถ.เทพา",
    "แขวงบำรุงทางตันหยงมัส",
    "นตท.บาลอ", "นตท.ลาโละ", "นตท.ตันหยงมัส",
    "นตท.สุไหงโก", "พสถ.ตันหยงมัส",
]

RAILWAY_LINES = [
    "สายเหนือ (กรุงเทพ-เชียงใหม่)",
    "สายตะวันออกเฉียงเหนือ (กรุงเทพ-อุบลราชธานี)",
    "สายตะวันออกเฉียงเหนือ (กรุงเทพ-หนองคาย)",
    "สายใต้ (กรุงเทพ-สุไหงโก-ลก)",
    "สายตะวันออก (กรุงเทพ-อรัญประเทศ)",
    "สายแม่กลอง",
    "สายวงเวียนใหญ่-มหาชัย",
    "สายนครปฐม-กาญจนบุรี",
    "สายตะวันออก (มาบตาพุด)",
    "อื่นๆ",
]

DAMAGE_TYPES = [
    "รางหัก",
    "รางแตกร้าว",
    "รางชำรุด",
    "รางหักบริเวณรอยเชื่อม",
    "รางหักในเหล็กประกบราง",
    "การชำรุดเสียหายบริเวณหัวราง",
    "อื่นๆ",
]

SEVERITY_MAP = {'low': 'ต่ำ', 'med': 'ปานกลาง', 'high': 'สูง'}
STATUS_MAP   = {'pending': 'รอดำเนินการ', 'inprog': 'กำลังซ่อมแซม', 'done': 'ซ่อมแซมแล้ว'}

# สีบนแผนที่ตามประเภท
TYPE_MAP_COLORS = {
    "รางหัก":                          "#dc2626",
    "รางแตกร้าว":                      "#ea580c",
    "รางชำรุด":                        "#2563eb",
    "รางหักบริเวณรอยเชื่อม":           "#b91c1c",
    "รางหักในเหล็กประกบราง":           "#7f1d1d",
    "การชำรุดเสียหายบริเวณหัวราง":     "#7c3aed",
    "รางหัก (Rail Break)":              "#dc2626",
    "รางแตกร้าว (Rail Crack)":          "#ea580c",
    "รางชำรุด (Rail Defect)":           "#2563eb",
    "รางบิดเบี้ยว (Rail Twist)":        "#7c3aed",
    "รางสึกกร่อน (Rail Wear)":          "#64748b",
    "รอยเชื่อมแตก (Weld Fracture)":    "#b91c1c",
    "หมอนรถไฟชำรุด (Sleeper Defect)":  "#0891b2",
    "หินโรยทางทรุด (Ballast Settlement)": "#a16207",
    "สลักยึดรางชำรุด (Fastener Defect)":"#1d4ed8",
    "อื่นๆ":                             "#6b7280",
}

STATION_COORDS = {
    "กรุงเทพ":         (13.7437, 100.5316),
    "ดอนเมือง":        (13.9135, 100.6066),
    "อยุธยา":          (14.3567, 100.5706),
    "ลพบุรี":          (14.7994, 100.6536),
    "นครสวรรค์":       (15.7030, 100.1373),
    "พิษณุโลก":        (16.8239, 100.2659),
    "ลำปาง":           (18.2855,  99.4931),
    "เชียงใหม่":       (18.7967,  98.9665),
    "แก่งคอย":         (14.5882, 101.1516),
    "นครราชสีมา":      (14.9799, 102.0978),
    "ขอนแก่น":         (16.4419, 102.8360),
    "อุดรธานี":        (17.4138, 102.7876),
    "สุรินทร์":        (14.8827, 103.4956),
    "ศรีสะเกษ":        (15.1186, 104.3220),
    "อุบลราชธานี":     (15.2448, 104.8473),
    "ชุมพร":           (10.4930,  99.1800),
    "สุราษฎร์ธานี":    ( 9.1400,  99.3308),
    "ทุ่งสง":          ( 8.1617,  99.6756),
    "หาดใหญ่":         ( 7.0086, 100.4747),
    "ยะลา":            ( 6.5425, 101.2800),
    "ฉะเชิงเทรา":      (13.6909, 101.0724),
    "ปราจีนบุรี":      (14.0511, 101.3661),
    "สระแก้ว":         (13.8240, 102.0643),
    "ชลบุรี":          (13.3611, 100.9847),
    "ศรีราชา":         (13.1282, 100.9235),
    "กาญจนบุรี":       (14.0227,  99.5328),
    "เพชรบุรี":        (13.1119,  99.9392),
    "หัวหิน":          (12.5706,  99.9578),
    "ประจวบคีรีขันธ์": (11.8131,  99.7967),
    "บางซื่อ":         (13.8036, 100.5295),
    "ธนบุรี":          (13.7269, 100.4836),
    "มักกะสัน":        (13.7500, 100.5611),
    "ราชบุรี":         (13.5282,  99.8178),
    "นครปฐม":          (13.8199, 100.0638),
    "สระบุรี":         (14.5289, 100.9107),
}

records = load_records()

def render_basic_dashboard(records):
    st.warning(
        "ระบบยังไม่พบแพ็กเกจ Plotly จึงแสดงแดชบอร์ดแบบพื้นฐานชั่วคราว "
        "กรุณาตรวจสอบว่าไฟล์ requirements.txt มี plotly และอยู่ใน root ของโปรเจกต์"
    )

    map_records = [r for r in records if r.get('lat') and r.get('lon')]
    st.markdown('<div class="section-header"><h4>🗺️ แผนที่จุดเกิดเหตุ</h4></div>',
                unsafe_allow_html=True)
    if map_records:
        map_df = pd.DataFrame([{
            'lat': r.get('lat'),
            'lon': r.get('lon'),
            'รหัส': r.get('id', '–'),
            'ประเภท': r.get('type', '–'),
            'สถานี': r.get('station', '–'),
            'KM': r.get('km', '–'),
        } for r in map_records])
        st.map(map_df[['lat', 'lon']])
        st.dataframe(map_df, use_container_width=True, hide_index=True)
    else:
        st.info("⚠️ ยังไม่มีพิกัด — กรอกละติจูด/ลองจิจูด หรือชื่อสถานี ตอนแจ้งเหตุ")

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown('<div class="section-header"><h4>💥 สถิติประเภทความเสียหาย</h4></div>',
                    unsafe_allow_html=True)
        type_df = pd.DataFrame(
            [{'ประเภท': k, 'จำนวน': v} for k, v in pd.Series(
                [r.get('type', 'ไม่ระบุ') for r in records]
            ).value_counts().items()]
        )
        st.bar_chart(type_df.set_index('ประเภท'))

    with ch2:
        st.markdown('<div class="section-header"><h4>📍 พื้นที่/สถานีที่เกิดบ่อย</h4></div>',
                    unsafe_allow_html=True)
        station_df = pd.DataFrame(
            [{'สถานี': k, 'จำนวน': v} for k, v in pd.Series(
                [r.get('station') or r.get('line', 'ไม่ระบุ') or 'ไม่ระบุ' for r in records]
            ).value_counts().head(10).items()]
        )
        st.bar_chart(station_df.set_index('สถานี'))

    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown('<div class="section-header"><h4>🔧 สถานะการซ่อมแซม</h4></div>',
                    unsafe_allow_html=True)
        status_df = pd.DataFrame({
            'สถานะ': [STATUS_MAP[k] for k in STATUS_MAP],
            'จำนวน': [len([r for r in records if r.get('status') == k]) for k in STATUS_MAP]
        })
        st.bar_chart(status_df.set_index('สถานะ'))

    with ch4:
        st.markdown('<div class="section-header"><h4>⚠️ ระดับความรุนแรง</h4></div>',
                    unsafe_allow_html=True)
        severity_df = pd.DataFrame({
            'ความรุนแรง': [SEVERITY_MAP[k] for k in SEVERITY_MAP],
            'จำนวน': [len([r for r in records if r.get('severity') == k]) for k in SEVERITY_MAP]
        })
        st.bar_chart(severity_df.set_index('ความรุนแรง'))

    date_counts = {}
    for r in records:
        d = r.get('date', '')
        if d:
            date_counts[d] = date_counts.get(d, 0) + 1
    if date_counts:
        st.markdown('<div class="section-header"><h4>📈 แนวโน้มการรายงานตามวัน</h4></div>',
                    unsafe_allow_html=True)
        date_df = pd.DataFrame({
            'วันที่': list(date_counts.keys()),
            'จำนวน': list(date_counts.values())
        })
        date_df['วันที่'] = pd.to_datetime(date_df['วันที่'])
        date_df = date_df.sort_values('วันที่')
        st.line_chart(date_df.set_index('วันที่'))

    latest = sorted(records, key=lambda x: x.get('createdAt', ''), reverse=True)[:10]
    st.markdown('<div class="section-header"><h4>📋 สรุปรายการล่าสุด 10 รายการ</h4></div>',
                unsafe_allow_html=True)
    summary_df = pd.DataFrame([{
        'รหัส': r.get('id'),
        'วันที่': r.get('date'),
        'สาย': r.get('line', '–'),
        'สถานี': r.get('station', '–'),
        'ประเภท': r.get('type', '–'),
        'ความรุนแรง': SEVERITY_MAP.get(r.get('severity'), '–'),
        'สถานะ': STATUS_MAP.get(r.get('status'), '–'),
        'ผู้รายงาน': r.get('reporter', '–'),
    } for r in latest])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ----------------- 4. Sidebar -----------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <img src="https://upload.wikimedia.org/wikipedia/th/thumb/d/d5/State_Railway_of_Thailand_Logo.svg/1200px-State_Railway_of_Thailand_Logo.svg.png"
             width="72" style="filter: brightness(0) invert(1);">
        <div class="sidebar-brand">การรถไฟแห่งประเทศไทย</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### เมนูหลัก")
    menu = st.radio(
        "เลือกเมนู",
        ["📝 แจ้งความเสียหาย", "📋 รายการแจ้งเหตุ", "📊 แดชบอร์ดสถิติ"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:12px; opacity:0.6; text-align:center;'>
        เวอร์ชัน 2.5.0<br>
        อัปเดต: {datetime.now().strftime('%d/%m/%Y')}
        <div class="sidebar-credit">
            จัดทำโดย<br>
            กองทางถาวร และกองเทคนิคทางถาวร
        </div>
    </div>
    """, unsafe_allow_html=True)
    sync_label = "ข้อมูลกลางเปิดใช้งาน" if github_storage_enabled() else "ข้อมูลเก็บในเครื่องนี้"
    sync_note = "ทุกอุปกรณ์ที่ใช้ backend เดียวกันจะเห็นข้อมูลล่าสุด" if github_storage_enabled() else "ตั้งค่า GITHUB_* ใน Secrets เพื่อแชร์หลายอุปกรณ์"
    st.markdown(f"""
    <div class="sync-pill">
        <strong>{sync_label}</strong><br>
        {sync_note}
    </div>
    """, unsafe_allow_html=True)
    if not github_storage_enabled():
        with st.expander("ตั้งค่า GITHUB_REPO"):
            st.code(
                'GITHUB_REPO = "your-user/your-repo"\n'
                'GITHUB_TOKEN = "github_pat_xxxxxxxxx"\n'
                'GITHUB_BRANCH = "main"\n'
                'GITHUB_DATA_PATH = "data/rail_damage_records.json"',
                language="toml"
            )

# Topbar
st.markdown("""
<div class="topbar-header">
    <div class="topbar-icon">🛤️</div>
    <div>
        <div class="topbar-title">ระบบรายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)</div>
        <div class="topbar-sub">Rail Damage Reporting System · จัดทำโดย กองทางถาวร และกองเทคนิคทางถาวร</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ================================================================
# หน้า 1: แจ้งความเสียหาย
# ================================================================
if menu == "📝 แจ้งความเสียหาย":
    st.markdown('<div class="section-header"><h4>📝 ส่งรายงานรางชำรุด หัก แตกร้าว (แบบ บท.27)</h4></div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="required-note">กรอกข้อมูลเท่าที่ทราบในขณะพบเหตุ โดยช่องที่มีเครื่องหมาย * เป็นข้อมูลจำเป็น</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="form-banner">
        <div class="form-banner-title">แบบ บท.27: รายงานรางชำรุด หัก แตกร้าว</div>
        <div class="form-banner-sub">จัดหมวดตามแบบฟอร์มกระดาษ พร้อมรองรับพิกัด แผนผัง และรูปประกอบสำหรับงานภาคสนาม</div>
    </div>
    <div class="form-chip-row">
        <div class="form-chip">1-10 รายการทั่วไป</div>
        <div class="form-chip">11-19 รายละเอียดเกี่ยวกับราง</div>
        <div class="form-chip">20-22 รายละเอียดเกี่ยวกับทาง</div>
        <div class="form-chip">23-28 รายละเอียดรางหัก/แตก/ร้าว</div>
        <div class="form-chip">แนบรูปแผนผัง</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_report_form", clear_on_submit=True):
        st.markdown("##### ข้อมูลหัวรายงาน")
        c0a, c0b, c0c = st.columns([1.2, 1.4, 1])
        with c0a:
            report_no_input = st.text_input("เลขที่รายงาน", placeholder="เช่น บท.27/2569-001")
        with c0b:
            completed_replace_input = st.text_input("ได้เปลี่ยนแล้วเสร็จเมื่อ", placeholder="วัน/เดือน/ปี หรือ เวลา")
        with c0c:
            report_status_input = st.selectbox("สถานะรายงาน", ["พบเหตุใหม่", "เปลี่ยนรางแล้ว", "รอตรวจสอบ", "ปิดงานแล้ว"])

        with st.expander("1-10 รายการทั่วไป", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                date_input = st.date_input("วันที่พบเหตุ *", value=datetime.today())
            with c2:
                time_input = st.time_input("เวลาที่พบเหตุ", value=datetime.now().time())
            with c3:
                line_input = st.selectbox("1. ทางประธาน/ทางแยก สาย *", options=["-- เลือกสายทาง --"] + RAILWAY_LINES)

            c4, c5, c6 = st.columns(3)
            with c4:
                track_class_input = st.text_input("2. ชั้นของทาง", placeholder="เช่น ชั้น 1 / ชั้น 2")
            with c5:
                main_branch_input = st.radio("ประเภททาง", ["ทางประธาน", "ทางแยก", "อื่นๆ"], horizontal=True)
            with c6:
                track_direction_input = st.radio("3. ชนิดของทาง", ["ทางขึ้น", "ทางล่อง", "ทางเดี่ยว"], horizontal=True)

            c7, c8, c9 = st.columns(3)
            with c7:
                service_track_input = st.radio("ลักษณะการเดินรถ", ["เร็ว", "ช้า", "โดยสาร/สินค้า"], horizontal=True)
            with c8:
                traction_input = st.radio("ชนิดแรงขับ", ["ดีเซล", "ไฟฟ้า", "อื่นๆ"], horizontal=True)
            with c9:
                station_input = st.text_input("สถานีใกล้เคียง", placeholder="ใช้ช่วยระบุตำแหน่งบนแผนที่")

            c10, c11, c12 = st.columns(3)
            with c10:
                station_from_input = st.text_input("4. ระหว่างสถานี", placeholder="สถานีต้นทาง")
            with c11:
                station_to_input = st.text_input("และ", placeholder="สถานีปลายทาง")
            with c12:
                km_input = st.text_input("5. กม. *", placeholder="เช่น 71+500")

            c13, c14, c15 = st.columns(3)
            with c13:
                alignment_input = st.selectbox("6. ลักษณะของทาง", ["ตรง", "เอียง", "โค้ง", "อื่นๆ"])
            with c14:
                curve_radius_input = st.text_input("รัศมีโค้ง/รายละเอียด", placeholder="เช่น R 400 ม.")
            with c15:
                wet_dry_input = st.radio("สภาพทาง", ["แห้ง", "เปียก", "ไม่ระบุ"], horizontal=True)

            c16, c17, c18 = st.columns(3)
            with c16:
                grade_input = st.text_input("7. ระดับความลาดชันของทาง", placeholder="ระดับ / ลาดขึ้น / ลาดลง")
            with c17:
                wheel_flat_input = st.text_input("8. จุดรถล้อหล่อ/เคลื่อนขบวน", placeholder="ขบวน/ตำแหน่ง/ข้อสังเกต")
            with c18:
                speed_limit_input = st.text_input("10. ความเร็วสูงสุดที่อนุญาต", placeholder="กม./ชม.")

            c19, c20, c21 = st.columns(3)
            with c19:
                train_passenger_input = st.number_input("9. ขบวนผู้โดยสาร/24 ชม.", min_value=0, step=1)
            with c20:
                train_freight_input = st.number_input("9. ขบวนสินค้า/24 ชม.", min_value=0, step=1)
            with c21:
                train_total_input = st.number_input("รวมขบวน/24 ชม.", min_value=0, step=1)

        with st.expander("11-19 รายละเอียดเกี่ยวกับราง", expanded=True):
            r1, r2, r3 = st.columns(3)
            with r1:
                rail_size_input = st.text_input("11. ขนาด/น้ำหนักราง", placeholder="เช่น 50 กก./ม. หรือ BS100A")
            with r2:
                rail_length_input = st.text_input("ความยาวราง", placeholder="ม.")
            with r3:
                cwr_length_input = st.text_input("รางเชื่อมยาว", placeholder="ม.")

            r4, r5, r6 = st.columns(3)
            with r4:
                broken_rail_type_input = st.selectbox(
                    "12. ชนิดของรางที่หัก",
                    ["รางธรรมดา", "รางสั้น", "รางลิ้นประแจ", "รางแม่คู่", "รางปีก", "อื่นๆ"]
                )
            with r5:
                rail_side_history_input = st.radio("13. เคยกลับ/เปลี่ยนข้างรางหรือไม่", ["กลับแล้ว", "เปลี่ยนข้างแล้ว", "ไม่ได้ทั้งสองอย่าง", "ไม่ทราบ"], horizontal=True)
            with r6:
                rail_condition_input = st.radio("16. สภาพรางเดิม", ["รางใหม่", "รางใช้แล้ว", "ไม่ทราบ"], horizontal=True)

            r7, r8, r9 = st.columns(3)
            with r7:
                rail_weight_break_input = st.text_input("14. น้ำหนักรางเมื่อหัก", placeholder="กก./ม.")
            with r8:
                rail_weight_loss_input = st.text_input("น้ำหนักที่หายไป", placeholder="กก. / ชั่ง / คำนวณ")
            with r9:
                rail_mark_input = st.text_input("15. เครื่องหมายราง", placeholder="ยี่ห้อ / ค.ศ. / Heat No.")

            r10, r11, r12 = st.columns(3)
            with r10:
                rail_laid_date_input = st.text_input("16. วางรางเมื่อ", placeholder="วัน/เดือน/ปี")
            with r11:
                weld_method_input = st.selectbox("17. วิธีเชื่อมใกล้จุดหัก", ["ไม่มี/ไม่เกี่ยวข้อง", "เทอร์มิต", "ไฟฟ้า", "อื่นๆ"])
            with r12:
                weld_last_date_input = st.text_input("เชื่อมครั้งสุดท้ายเมื่อวันที่")

            r13, r14 = st.columns(2)
            with r13:
                weld_repair_count_input = st.text_input("จำนวนครั้งที่ซ่อม")
            with r14:
                ballast_input = st.radio("18. หินโรยทาง", ["เต็มมาตรฐาน", "พร่อง", "ไม่ระบุ"], horizontal=True)

            tamping_frequency_input = st.radio("19. วาระการอัดหิน", ["นานๆ ครั้ง", "ปานกลาง", "บ่อยๆ", "ไม่ระบุ"], horizontal=True)

        with st.expander("20-22 รายละเอียดเกี่ยวกับทางและเหล็กประกบราง", expanded=False):
            st.markdown('<div class="subtle-box">ใช้กรอกเพิ่มเติมเมื่อรางหักอยู่ภายในเหล็กประกบราง หรือเกี่ยวข้องกับรอยต่อราง</div>', unsafe_allow_html=True)
            j1, j2, j3 = st.columns(3)
            with j1:
                joint_cut_method_input = st.selectbox("20 ก. การตัด/เปลี่ยนราง", ["ไม่เกี่ยวข้อง", "เปลี่ยนใหม่ทั้งท่อน", "ตัดโดยเลื่อย", "สกัด", "ออกซิเจน", "อื่นๆ"])
            with j2:
                joint_contact_condition_input = st.radio("20 ข. สภาพผิวสัมผัสเหล็กประกบ", ["ดี", "ปานกลาง", "สึกกร่อน", "ไม่ระบุ"], horizontal=True)
            with j3:
                bolt_hole_input = st.text_input("20 ค. รูสลักเกลียวต่อราง", placeholder="4-6 รู / สึกโต ø ... มม.")

            j4, j5, j6 = st.columns(3)
            with j4:
                fishplate_type_input = st.radio("20 ง. ชนิดเหล็กประกบราง", ["มีเขี้ยว", "ไม่มีเขี้ยว", "พิเศษ", "ไม่ระบุ"], horizontal=True)
            with j5:
                fishplate_condition_input = st.radio("20 จ. สภาพเหล็กประกบราง", ["ดี", "ปานกลาง", "สึกกร่อน", "ไม่ระบุ"], horizontal=True)
            with j6:
                sleeper_condition_input = st.text_input("21. ชนิดและสภาพหมอน", placeholder="ไม้/คอนกรีต ดี/พอใช้/ชำรุด")

            nearby_break_input = st.text_area("22. ประวัติรางหักในระยะใกล้เคียง", placeholder="ถ้ามี ระบุ กม. และวันที่", height=80)

        with st.expander("23-28 รายละเอียดเกี่ยวกับรางชำรุด หัก แตกร้าว", expanded=True):
            d1, d2, d3 = st.columns(3)
            with d1:
                type_input = st.selectbox("ประเภทเหตุ *", options=["-- เลือกประเภท --"] + DAMAGE_TYPES)
            with d2:
                severity_input = st.selectbox(
                    "ระดับความรุนแรง *",
                    options=list(SEVERITY_MAP.keys()),
                    format_func=lambda x: "สูง" if x == 'high' else "ปานกลาง" if x == 'med' else "ต่ำ"
                )
            with d3:
                defect_length_input = st.text_input("ความยาว/ขนาดชำรุด", placeholder="เช่น 15 ซม.")

            d4, d5, d6 = st.columns(3)
            with d4:
                found_by_input = st.text_input("23. ตรวจพบโดย", placeholder="ชื่อ/ตำแหน่ง/หน่วยงาน")
            with d5:
                found_position_input = st.text_input("ตำแหน่งที่พบ", placeholder="เช่น โคนราง/ด้านใน/ด้านนอก")
            with d6:
                found_context_input = st.text_input("ขณะตรวจพบ", placeholder="เดินตรวจทาง / ขบวนรถ / อื่นๆ")

            d7, d8, d9 = st.columns(3)
            with d7:
                rail_temp_input = st.radio("24. อุณหภูมิขณะพบ", ["ร้อน", "ปานกลาง", "หนาว", "ไม่ระบุ"], horizontal=True)
            with d8:
                crack_age_input = st.radio("25. ลักษณะรอยร้าว", ["ใหม่", "เก่า", "ผสมทั้งเก่า-ใหม่", "ไม่ระบุ"], horizontal=True)
            with d9:
                wheel_impact_input = st.radio("26. มีรอยล้อกระแทก", ["มี", "ไม่มี", "ไม่ระบุ"], horizontal=True)

            d10, d11, d12 = st.columns(3)
            with d10:
                replacement_rail_size_input = st.text_input("27. รางที่นำมาเปลี่ยน: ขนาด")
            with d11:
                replacement_rail_length_input = st.text_input("ความยาว", placeholder="ม.")
            with d12:
                replacement_rail_type_input = st.radio("ประเภท", ["ใหม่", "เก่า", "ไม่ระบุ"], horizontal=True)

            head_damage_input = st.multiselect(
                "28. การชำรุดเสียหายบริเวณหัวราง (ถ้ามี)",
                [
                    "รางลอก (Spalling)",
                    "ร่องหลุม (Squat)",
                    "ลื่นรางเป็นคลื่น (Corrugation)",
                    "การแตกมุมรางด้านในเป็นชิ้นเล็ก (Flaking/Gauge Corner Cracking)",
                    "ล้อดัน (Wheel Burn)",
                    "บุ๋มสนิม (Belgrospi)",
                    "การแตกมุมรางด้านใน (Shelling)",
                    "การแตกเป็นเส้น (Head Check)",
                    "อื่นๆ",
                ]
            )
            head_damage_other_input = st.text_input("ระบุอื่นๆ", placeholder="กรอกเมื่อเลือก อื่นๆ")

        with st.expander("พิกัด ภาพร่าง และหมายเหตุ", expanded=False):
            p1, p2 = st.columns(2)
            with p1:
                lat_input = st.text_input("ละติจูด (Latitude)", placeholder="เช่น 14.3567  ถ้าไม่กรอก ระบบจะใช้พิกัดสถานี")
            with p2:
                lon_input = st.text_input("ลองจิจูด (Longitude)", placeholder="เช่น 100.5706")

            attachments_input = st.file_uploader(
                "แนบรูปแผนผัง/รูปถ่าย/รูปตัด ตามหน้าที่ 2 ของแบบฟอร์ม",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True
            )
            note_input = st.text_area("หมายเหตุ", placeholder="ข้อสังเกตเพิ่มเติม / การเขียนรูปด้านบน ด้านข้าง รูปตัด และลูกศรทิศทางขบวน", height=90)
            action_input = st.text_area("การดำเนินการเบื้องต้น", placeholder="เช่น จำกัดความเร็ว เปลี่ยนราง ติดตามตรวจซ้ำ แจ้งหน่วยงานที่เกี่ยวข้อง", height=90)

        with st.expander("ข้อมูลผู้รายงานและผู้ตรวจรับรอง", expanded=True):
            u1, u2, u3 = st.columns(3)
            with u1:
                reporter_input = st.text_input("ชื่อ-นามสกุลผู้รายงาน *", placeholder="ชื่อผู้รายงาน")
            with u2:
                position_input = st.text_input("ตำแหน่ง", placeholder="เช่น นายตรวจทาง / นายช่างโยธา")
            with u3:
                phone_input = st.text_input("เบอร์โทรศัพท์", placeholder="เช่น 081-234-5678")

            u4, u5 = st.columns(2)
            with u4:
                dept_input = st.text_input("หน่วยงาน/เขต *", placeholder="เช่น แขวงบำรุงทาง / ตอนนายตรวจทาง / เขตพื้นที่")
            with u5:
                certifier_input = st.text_input("วิศวกร/ผู้รับรอง", placeholder="ชื่อผู้รับรองหรือผู้ตรวจสอบ")

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("บันทึกและส่งรายงาน บท.27", use_container_width=True)

        if submit_btn:
            errors = []
            if line_input == "-- เลือกสายทาง --": errors.append("สายทาง")
            if not km_input.strip(): errors.append("กม.")
            if type_input == "-- เลือกประเภท --": errors.append("ประเภทเหตุ")
            if not reporter_input.strip(): errors.append("ชื่อ-นามสกุลผู้รายงาน")
            if not dept_input.strip(): errors.append("หน่วยงาน/เขต")

            if errors:
                st.error(f"กรุณากรอก/เลือก: {', '.join(errors)}")
            else:
                try:
                    lat = float(lat_input) if lat_input.strip() else None
                    lon = float(lon_input) if lon_input.strip() else None
                except ValueError:
                    lat = lon = None

                station_lookup = station_input or station_from_input or station_to_input
                if lat is None or lon is None:
                    for k, v in STATION_COORDS.items():
                        if k in station_lookup:
                            lat, lon = v
                            break

                record_id = generate_id()
                saved_attachments = save_uploaded_files(attachments_input, record_id)
                actual_train_total = train_total_input or (train_passenger_input + train_freight_input)
                station_display = station_input or f"{station_from_input}-{station_to_input}".strip("-")
                length_input = defect_length_input or replacement_rail_length_input or rail_length_input
                detail_input = (
                    f"แบบ บท.27 | {type_input} | กม. {km_input} | "
                    f"ระหว่าง {station_from_input or '-'} และ {station_to_input or '-'} | "
                    f"ราง {rail_size_input or '-'} | จุดพบ {found_position_input or '-'} | "
                    f"หัวราง: {', '.join(head_damage_input) if head_damage_input else '-'}"
                )

                form_details = {
                    'reportNo': report_no_input,
                    'completedReplaceAt': completed_replace_input,
                    'reportStatus': report_status_input,
                    'mainBranch': main_branch_input,
                    'trackClass': track_class_input,
                    'trackDirection': track_direction_input,
                    'serviceTrack': service_track_input,
                    'traction': traction_input,
                    'stationFrom': station_from_input,
                    'stationTo': station_to_input,
                    'alignment': alignment_input,
                    'curveRadius': curve_radius_input,
                    'wetDry': wet_dry_input,
                    'grade': grade_input,
                    'wheelFlatRemark': wheel_flat_input,
                    'trainPassenger24h': train_passenger_input,
                    'trainFreight24h': train_freight_input,
                    'trainTotal24h': actual_train_total,
                    'speedLimit': speed_limit_input,
                    'railSize': rail_size_input,
                    'railLength': rail_length_input,
                    'cwrLength': cwr_length_input,
                    'brokenRailType': broken_rail_type_input,
                    'railSideHistory': rail_side_history_input,
                    'railWeightAtBreak': rail_weight_break_input,
                    'railWeightLoss': rail_weight_loss_input,
                    'railMark': rail_mark_input,
                    'railLaidDate': rail_laid_date_input,
                    'railCondition': rail_condition_input,
                    'weldMethod': weld_method_input,
                    'weldLastDate': weld_last_date_input,
                    'weldRepairCount': weld_repair_count_input,
                    'ballast': ballast_input,
                    'tampingFrequency': tamping_frequency_input,
                    'jointCutMethod': joint_cut_method_input,
                    'jointContactCondition': joint_contact_condition_input,
                    'boltHole': bolt_hole_input,
                    'fishplateType': fishplate_type_input,
                    'fishplateCondition': fishplate_condition_input,
                    'sleeperCondition': sleeper_condition_input,
                    'nearbyBreakRecord': nearby_break_input,
                    'foundBy': found_by_input,
                    'foundPosition': found_position_input,
                    'foundContext': found_context_input,
                    'railTemperature': rail_temp_input,
                    'crackAge': crack_age_input,
                    'wheelImpact': wheel_impact_input,
                    'replacementRailSize': replacement_rail_size_input,
                    'replacementRailLength': replacement_rail_length_input,
                    'replacementRailType': replacement_rail_type_input,
                    'headDamage': head_damage_input,
                    'headDamageOther': head_damage_other_input,
                    'note': note_input,
                    'certifier': certifier_input,
                    'attachments': saved_attachments,
                }

                new_record = {
                    'id': record_id,
                    'date': str(date_input),
                    'time': str(time_input),
                    'line': line_input,
                    'station': station_display,
                    'km': km_input,
                    'railId': rail_mark_input,
                    'type': type_input,
                    'length': length_input,
                    'severity': severity_input,
                    'detail': detail_input,
                    'action': action_input,
                    'lat': lat,
                    'lon': lon,
                    'reporter': reporter_input,
                    'position': position_input,
                    'dept': dept_input.strip(),
                    'phone': phone_input,
                    'status': 'pending',
                    'formType': 'บท.27',
                    'formDetails': form_details,
                    'createdAt': datetime.now().isoformat()
                }
                records.append(new_record)
                save_records(records)
                st.session_state['latest_report_download'] = save_report_files(new_record)
                st.success(f"บันทึกรายงานสำเร็จ! รหัสเอกสาร: **{new_record['id']}**")
                st.balloons()

    render_report_downloads(st.session_state.get('latest_report_download'))


# ================================================================
# หน้า 2: รายการแจ้งเหตุ
# ================================================================
elif menu == "📋 รายการแจ้งเหตุ":
    st.markdown('<div class="section-header"><h4>📋 รายการรายงานความเสียหายทั้งหมด</h4></div>',
                unsafe_allow_html=True)

    if len(records) == 0:
        st.info("ยังไม่มีข้อมูลรายงานในระบบ")
    else:
        fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
        with fc1:
            f_line = st.selectbox("กรองตามสายทาง", ["ทั้งหมด"] + RAILWAY_LINES)
        with fc2:
            f_sev  = st.selectbox("กรองตามความรุนแรง",
                                   ["ทั้งหมด"] + list(SEVERITY_MAP.values()))
        with fc3:
            f_stat = st.selectbox("กรองตามสถานะ",
                                   ["ทั้งหมด"] + list(STATUS_MAP.values()))
        with fc4:
            st.markdown("<br>", unsafe_allow_html=True)
            output = StringIO()
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow([
                'รหัส','เลขที่รายงาน','วันที่','เวลา','สาย','กม.','สถานี/ช่วงสถานี','ประเภท',
                'ความรุนแรง','สถานะ','ผู้รายงาน','หน่วยงาน','ขนาดราง','รางเปลี่ยนใหม่','หมายเหตุ'
            ])
            for r in records:
                fd = r.get('formDetails', {})
                writer.writerow([
                    r.get('id'), fd.get('reportNo', ''), r.get('date'), r.get('time'), r.get('line'),
                    r.get('km'), r.get('station'), r.get('type'),
                    SEVERITY_MAP.get(r.get('severity'), ''),
                    STATUS_MAP.get(r.get('status'), ''),
                    r.get('reporter'), r.get('dept'),
                    fd.get('railSize', ''), fd.get('replacementRailSize', ''), fd.get('note', '')
                ])
            st.download_button("📥 CSV",
                               data=output.getvalue().encode('utf-8-sig'),
                               file_name='rail_damage.csv', mime='text/csv')

        filtered = records[:]
        if f_line != "ทั้งหมด":
            filtered = [r for r in filtered if r.get('line') == f_line]
        if f_sev  != "ทั้งหมด":
            filtered = [r for r in filtered if SEVERITY_MAP.get(r.get('severity')) == f_sev]
        if f_stat != "ทั้งหมด":
            filtered = [r for r in filtered if STATUS_MAP.get(r.get('status')) == f_stat]

        st.caption(f"แสดง {len(filtered)} รายการ จากทั้งหมด {len(records)} รายการ")
        st.markdown("<br>", unsafe_allow_html=True)

        for r in filtered:
            orig_idx    = records.index(r)
            sev_key     = r.get('severity', 'low')
            sev_label   = SEVERITY_MAP.get(sev_key, 'ไม่ระบุ')
            sev_icon    = {'high': '🔴', 'med': '🟡', 'low': '🟢'}.get(sev_key, '⚪')
            status_icon = {'pending': '⏳', 'inprog': '🛠️', 'done': '✅'}.get(r.get('status'), '⏳')
            fd = r.get('formDetails', {})
            report_no = fd.get('reportNo') or r.get('id')

            with st.expander(
                f"{status_icon} {sev_icon} [{report_no}]  "
                f"{r.get('line','–')}  |  "
                f"กม. {r.get('km','–')}  |  "
                f"{r.get('type','–')}  |  ความรุนแรง: {sev_label}"
            ):
                detail_tab, edit_tab = st.tabs(["รายละเอียด", "แก้ไขข้อมูล"])

                with detail_tab:
                    cd1, cd2 = st.columns(2)
                    with cd1:
                        st.markdown(f"**เลขที่ระบบ:** {r.get('id')}")
                        st.markdown(f"**📅 วันที่-เวลา:** {r.get('date')} เวลา {r.get('time')}")
                        st.markdown(f"**📍 ตำแหน่ง:** KM {r.get('km','–')}  |  {r.get('station','–')}")
                        if fd:
                            st.markdown(f"**ช่วงสถานี:** {fd.get('stationFrom','–')} - {fd.get('stationTo','–')}")
                            st.markdown(f"**ลักษณะทาง:** {fd.get('alignment','–')} | {fd.get('wetDry','–')} | ลาดชัน {fd.get('grade','–')}")
                            st.markdown(f"**ขนาดราง:** {fd.get('railSize','–')} | ยาว {fd.get('railLength','–')} ม.")
                        st.markdown(f"**💥 ประเภท:** {r.get('type','–')}")
                        st.markdown(f"**📐 ขนาด:** {r.get('length','–')}")
                        st.markdown(f"**📝 รายละเอียด:** {r.get('detail','–')}")
                        st.markdown(f"**💡 การดำเนินการ:** {r.get('action','–')}")
                    with cd2:
                        st.markdown(f"**👤 ผู้รายงาน:** {r.get('reporter','–')}")
                        st.markdown(f"**💼 ตำแหน่ง:** {r.get('position','–')}")
                        st.markdown(f"**🏢 หน่วยงาน:** {r.get('dept','–')}")
                        st.markdown(f"**📞 ติดต่อ:** {r.get('phone','–')}")
                        if fd:
                            st.markdown(f"**ผู้ตรวจพบ:** {fd.get('foundBy','–')} | {fd.get('foundContext','–')}")
                            st.markdown(f"**สภาพรอยร้าว:** {fd.get('crackAge','–')} | อุณหภูมิ {fd.get('railTemperature','–')}")
                            head_damage = ', '.join(fd.get('headDamage', [])) if fd.get('headDamage') else '–'
                            st.markdown(f"**หัวราง:** {head_damage}")
                            attachments = fd.get('attachments', [])
                            if attachments:
                                st.markdown(f"**ไฟล์แนบ:** {len(attachments)} ไฟล์")
                    st.markdown("---")
                    render_report_downloads(save_report_files(r), show_message=False)

                with edit_tab:
                    line_options = ["-- เลือกสายทาง --"] + RAILWAY_LINES
                    if r.get('line') and r.get('line') not in line_options:
                        line_options.append(r.get('line'))
                    type_options = ["-- เลือกประเภท --"] + DAMAGE_TYPES
                    if r.get('type') and r.get('type') not in type_options:
                        type_options.append(r.get('type'))

                    with st.form(f"edit_form_{r.get('id')}"):
                        st.markdown("##### แก้ไขข้อมูลรายงาน")
                        e0, e1, e2 = st.columns(3)
                        with e0:
                            edit_report_no = st.text_input("เลขที่รายงาน", value=fd.get('reportNo', ''), key=f"report_no_{r.get('id')}")
                        with e1:
                            edit_date = st.date_input("วันที่พบเหตุ", value=parse_date_value(r.get('date')), key=f"date_{r.get('id')}")
                        with e2:
                            edit_time = st.time_input("เวลาที่พบเหตุ", value=parse_time_value(r.get('time')), key=f"time_{r.get('id')}")

                        e3, e4, e5 = st.columns(3)
                        with e3:
                            edit_line = st.selectbox("สายทาง", line_options, index=option_index(line_options, r.get('line'), 0), key=f"line_{r.get('id')}")
                        with e4:
                            edit_km = st.text_input("กม.", value=r.get('km', ''), key=f"km_{r.get('id')}")
                        with e5:
                            edit_station = st.text_input("สถานี/ช่วงสถานี", value=r.get('station', ''), key=f"station_{r.get('id')}")

                        e6, e7, e8 = st.columns(3)
                        with e6:
                            edit_type = st.selectbox("ประเภทเหตุ", type_options, index=option_index(type_options, r.get('type'), 0), key=f"type_{r.get('id')}")
                        with e7:
                            edit_severity = st.selectbox(
                                "ระดับความรุนแรง",
                                list(SEVERITY_MAP.keys()),
                                index=option_index(list(SEVERITY_MAP.keys()), r.get('severity', 'low'), 0),
                                format_func=lambda x: "สูง" if x == 'high' else "ปานกลาง" if x == 'med' else "ต่ำ",
                                key=f"severity_{r.get('id')}"
                            )
                        with e8:
                            edit_status = st.selectbox(
                                "สถานะการซ่อมแซม",
                                list(STATUS_MAP.keys()),
                                index=option_index(list(STATUS_MAP.keys()), r.get('status', 'pending'), 0),
                                format_func=lambda x: STATUS_MAP[x],
                                key=f"status_edit_{r.get('id')}"
                            )

                        e9, e10, e11 = st.columns(3)
                        with e9:
                            edit_rail_size = st.text_input("ขนาด/น้ำหนักราง", value=fd.get('railSize', ''), key=f"rail_size_{r.get('id')}")
                        with e10:
                            edit_length = st.text_input("ความยาว/ขนาดชำรุด", value=r.get('length', ''), key=f"length_{r.get('id')}")
                        with e11:
                            edit_rail_mark = st.text_input("เครื่องหมายราง", value=r.get('railId', ''), key=f"rail_mark_{r.get('id')}")

                        e12, e13, e14 = st.columns(3)
                        with e12:
                            edit_station_from = st.text_input("ระหว่างสถานี", value=fd.get('stationFrom', ''), key=f"station_from_{r.get('id')}")
                        with e13:
                            edit_station_to = st.text_input("และ", value=fd.get('stationTo', ''), key=f"station_to_{r.get('id')}")
                        with e14:
                            edit_found_by = st.text_input("ตรวจพบโดย", value=fd.get('foundBy', ''), key=f"found_by_{r.get('id')}")

                        e15, e16 = st.columns(2)
                        with e15:
                            edit_reporter = st.text_input("ผู้รายงาน", value=r.get('reporter', ''), key=f"reporter_{r.get('id')}")
                            edit_position = st.text_input("ตำแหน่ง", value=r.get('position', ''), key=f"position_{r.get('id')}")
                            edit_dept = st.text_input("หน่วยงาน/เขต", value=r.get('dept', ''), key=f"dept_{r.get('id')}")
                            edit_phone = st.text_input("เบอร์โทรศัพท์", value=r.get('phone', ''), key=f"phone_{r.get('id')}")
                        with e16:
                            edit_lat = st.text_input("ละติจูด", value="" if r.get('lat') is None else str(r.get('lat')), key=f"lat_{r.get('id')}")
                            edit_lon = st.text_input("ลองจิจูด", value="" if r.get('lon') is None else str(r.get('lon')), key=f"lon_{r.get('id')}")
                            edit_note = st.text_area("หมายเหตุ", value=fd.get('note', ''), height=82, key=f"note_{r.get('id')}")

                        edit_detail = st.text_area("รายละเอียด", value=r.get('detail', ''), height=90, key=f"detail_{r.get('id')}")
                        edit_action = st.text_area("การดำเนินการ", value=r.get('action', ''), height=90, key=f"action_{r.get('id')}")
                        edit_attachments = st.file_uploader(
                            "เพิ่มรูปแนบ/รูปตัด/ภาพถ่าย",
                            type=["png", "jpg", "jpeg"],
                            accept_multiple_files=True,
                            key=f"attachments_{r.get('id')}"
                        )

                        save_col, delete_col = st.columns([3, 1])
                        save_submit = save_col.form_submit_button("บันทึกการแก้ไข", use_container_width=True)
                        delete_submit = delete_col.form_submit_button("ลบรายการ", use_container_width=True)

                        if save_submit:
                            errors = []
                            if edit_line == "-- เลือกสายทาง --": errors.append("สายทาง")
                            if edit_type == "-- เลือกประเภท --": errors.append("ประเภทเหตุ")
                            if not edit_km.strip(): errors.append("กม.")
                            if not edit_reporter.strip(): errors.append("ผู้รายงาน")
                            if not edit_dept.strip(): errors.append("หน่วยงาน/เขต")

                            if errors:
                                st.error(f"กรุณากรอก/เลือก: {', '.join(errors)}")
                            else:
                                try:
                                    edit_lat_value = float(edit_lat) if edit_lat.strip() else None
                                    edit_lon_value = float(edit_lon) if edit_lon.strip() else None
                                except ValueError:
                                    edit_lat_value = r.get('lat')
                                    edit_lon_value = r.get('lon')
                                    st.warning("พิกัดไม่ถูกต้อง จึงคงค่าพิกัดเดิมไว้")

                                updated_fd = dict(fd)
                                updated_fd.update({
                                    'reportNo': edit_report_no,
                                    'stationFrom': edit_station_from,
                                    'stationTo': edit_station_to,
                                    'railSize': edit_rail_size,
                                    'foundBy': edit_found_by,
                                    'note': edit_note,
                                })
                                if edit_attachments:
                                    old_attachments = updated_fd.get('attachments', [])
                                    updated_fd['attachments'] = old_attachments + save_uploaded_files(edit_attachments, r.get('id'))

                                records[orig_idx].update({
                                    'date': str(edit_date),
                                    'time': str(edit_time),
                                    'line': edit_line,
                                    'station': edit_station,
                                    'km': edit_km,
                                    'railId': edit_rail_mark,
                                    'type': edit_type,
                                    'length': edit_length,
                                    'severity': edit_severity,
                                    'detail': edit_detail,
                                    'action': edit_action,
                                    'lat': edit_lat_value,
                                    'lon': edit_lon_value,
                                    'reporter': edit_reporter,
                                    'position': edit_position,
                                    'dept': edit_dept.strip(),
                                    'phone': edit_phone,
                                    'status': edit_status,
                                    'formDetails': updated_fd,
                                    'updatedAt': datetime.now().isoformat(),
                                })
                                save_records(records)
                                st.success("บันทึกการแก้ไขแล้ว")
                                st.rerun()

                        if delete_submit:
                            records.pop(orig_idx)
                            save_records(records)
                            st.success("ลบรายการแล้ว")
                            st.rerun()


# ================================================================
# หน้า 3: แดชบอร์ดสถิติ
# ================================================================
elif menu == "📊 แดชบอร์ดสถิติ":
    st.markdown('<div class="section-header"><h4>📊 แดชบอร์ดภาพรวมสถิติ</h4></div>',
                unsafe_allow_html=True)

    total   = len(records)
    high    = len([r for r in records if r.get('severity') == 'high'])
    pending = len([r for r in records if r.get('status') == 'pending'])
    inprog  = len([r for r in records if r.get('status') == 'inprog'])
    done    = len([r for r in records if r.get('status') == 'done'])

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📋 รายงานทั้งหมด",  total)
    k2.metric("🔴 ความรุนแรงสูง",  high)
    k3.metric("⏳ รอดำเนินการ",    pending)
    k4.metric("🛠️ กำลังซ่อมแซม", inprog)
    k5.metric("✅ ซ่อมแซมแล้ว",   done)

    st.markdown("<br>", unsafe_allow_html=True)

    if total == 0:
        st.info("📭 ยังไม่มีข้อมูล กรุณาแจ้งความเสียหายก่อน")
    else:
        if not PLOTLY_AVAILABLE:
            render_basic_dashboard(records)
            st.stop()

        # =====================================================
        # แผนที่ — รองรับทั้ง Plotly รุ่นใหม่และรุ่นเก่า
        # =====================================================
        st.markdown('<div class="section-header"><h4>🗺️ แผนที่จุดเกิดเหตุ</h4></div>',
                    unsafe_allow_html=True)

        map_records = [r for r in records if r.get('lat') and r.get('lon')]

        if len(map_records) == 0:
            st.info("⚠️ ยังไม่มีพิกัด — กรอกละติจูด/ลองจิจูด หรือชื่อสถานี ตอนแจ้งเหตุ")
        else:
            map_df = pd.DataFrame([{
                'lat':       r['lat'],
                'lon':       r['lon'],
                'ประเภท':   r.get('type', 'ไม่ระบุ'),
                'สถานี':    r.get('station', '–'),
                'สาย':      r.get('line', '–'),
                'KM':        r.get('km', '–'),
                'ความรุนแรง': SEVERITY_MAP.get(r.get('severity'), '–'),
                'สถานะ':    STATUS_MAP.get(r.get('status'), '–'),
                'ผู้รายงาน': r.get('reporter', '–'),
                'รหัส':     r.get('id', '–'),
                'สี':       TYPE_MAP_COLORS.get(r.get('type', ''), '#6b7280'),
                'ขนาด':     {'high': 18, 'med': 14, 'low': 10}.get(r.get('severity'), 12),
            } for r in map_records])

            map_kwargs = dict(
                data_frame=map_df,
                lat='lat',
                lon='lon',
                color='ประเภท',
                size='ขนาด',
                size_max=20,
                color_discrete_map={t: c for t, c in TYPE_MAP_COLORS.items()},
                hover_name='รหัส',
                hover_data={
                    'สถานี': True, 'สาย': True, 'KM': True,
                    'ความรุนแรง': True, 'สถานะ': True, 'ผู้รายงาน': True,
                    'lat': False, 'lon': False, 'สี': False, 'ขนาด': False,
                },
                zoom=5,
                center={"lat": 13.5, "lon": 101.0},
                height=520,
            )
            if hasattr(px, "scatter_map"):
                fig_map = px.scatter_map(**map_kwargs, map_style="carto-positron")
            else:
                fig_map = px.scatter_mapbox(**map_kwargs, mapbox_style="carto-positron")
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                font=dict(family='Sarabun', size=13),
                legend=dict(
                    title="ประเภทความเสียหาย",
                    orientation='v',
                    x=0.01, y=0.99,
                    bgcolor='rgba(255,255,255,0.85)',
                    bordercolor='#e2e8f0',
                    borderwidth=1,
                )
            )
            st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # =====================================================
        # Row 1: ประเภทความเสียหาย + พื้นที่เกิดบ่อย
        # =====================================================
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown('<div class="section-header"><h4>💥 สถิติประเภทความเสียหาย</h4></div>',
                        unsafe_allow_html=True)
            type_counts = {}
            for r in records:
                t = r.get('type', 'ไม่ระบุ')
                type_counts[t] = type_counts.get(t, 0) + 1
            type_df = pd.DataFrame({
                'ประเภท': list(type_counts.keys()),
                'จำนวน':  list(type_counts.values()),
                'สี':     [TYPE_MAP_COLORS.get(t, '#6b7280') for t in type_counts.keys()]
            }).sort_values('จำนวน', ascending=True)

            fig_type = px.bar(
                type_df, x='จำนวน', y='ประเภท',
                orientation='h',
                color='ประเภท',
                color_discrete_map=TYPE_MAP_COLORS,
                template='plotly_white',
                text='จำนวน',
            )
            fig_type.update_traces(textposition='outside')
            fig_type.update_layout(
                margin=dict(l=0, r=30, t=10, b=0),
                font=dict(family='Sarabun', size=12),
                showlegend=False,
                height=340,
                xaxis_title="จำนวน (รายการ)",
                yaxis_title="",
            )
            st.plotly_chart(fig_type, use_container_width=True)

        with ch2:
            st.markdown('<div class="section-header"><h4>📍 พื้นที่/สถานีที่เกิดบ่อย (Top 10)</h4></div>',
                        unsafe_allow_html=True)
            station_counts = {}
            for r in records:
                s = r.get('station') or r.get('line', 'ไม่ระบุ') or 'ไม่ระบุ'
                station_counts[s] = station_counts.get(s, 0) + 1
            top10 = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            sta_df = pd.DataFrame(top10, columns=['สถานี','จำนวน']).sort_values('จำนวน', ascending=True)

            fig_sta = px.bar(
                sta_df, x='จำนวน', y='สถานี',
                orientation='h',
                color='จำนวน',
                color_continuous_scale=['#bbf7d0','#16a34a','#14532d'],
                template='plotly_white',
                text='จำนวน',
            )
            fig_sta.update_traces(textposition='outside')
            fig_sta.update_layout(
                margin=dict(l=0, r=30, t=10, b=0),
                font=dict(family='Sarabun', size=12),
                showlegend=False,
                coloraxis_showscale=False,
                height=340,
                xaxis_title="จำนวน (รายการ)",
                yaxis_title="",
            )
            st.plotly_chart(fig_sta, use_container_width=True)

        # =====================================================
        # Row 2: สถานะ + ความรุนแรง
        # =====================================================
        ch3, ch4 = st.columns(2)

        with ch3:
            st.markdown('<div class="section-header"><h4>🔧 สถานะการซ่อมแซม</h4></div>',
                        unsafe_allow_html=True)
            stat_data = {STATUS_MAP[k]: len([r for r in records if r.get('status') == k])
                         for k in STATUS_MAP}
            fig_stat = go.Figure(go.Pie(
                labels=list(stat_data.keys()),
                values=list(stat_data.values()),
                marker_colors=['#6366f1','#f59e0b','#10b981'],
                hole=0.55,
                textinfo='label+percent+value',
                textfont=dict(family='Sarabun', size=13),
                pull=[0.03, 0.03, 0.03],
            ))
            fig_stat.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                font=dict(family='Sarabun', size=13),
                showlegend=True,
                height=320,
                legend=dict(orientation='h', yanchor='bottom', y=-0.2,
                            xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_stat, use_container_width=True)

        with ch4:
            st.markdown('<div class="section-header"><h4>⚠️ ระดับความรุนแรง</h4></div>',
                        unsafe_allow_html=True)
            sev_data = {SEVERITY_MAP[k]: len([r for r in records if r.get('severity') == k])
                        for k in SEVERITY_MAP}
            fig_sev = go.Figure(go.Pie(
                labels=list(sev_data.keys()),
                values=list(sev_data.values()),
                marker_colors=['#16a34a','#d97706','#dc2626'],
                hole=0.55,
                textinfo='label+percent+value',
                textfont=dict(family='Sarabun', size=13),
                pull=[0.03, 0.03, 0.03],
            ))
            fig_sev.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
                font=dict(family='Sarabun', size=13),
                showlegend=True,
                height=320,
                legend=dict(orientation='h', yanchor='bottom', y=-0.2,
                            xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_sev, use_container_width=True)

        # =====================================================
        # Timeline
        # =====================================================
        st.markdown('<div class="section-header"><h4>📈 แนวโน้มการรายงานตามวัน</h4></div>',
                    unsafe_allow_html=True)
        date_counts = {}
        for r in records:
            d = r.get('date', '')
            if d:
                date_counts[d] = date_counts.get(d, 0) + 1
        if date_counts:
            date_df = pd.DataFrame({
                'วันที่':  list(date_counts.keys()),
                'จำนวน': list(date_counts.values())
            })
            date_df['วันที่'] = pd.to_datetime(date_df['วันที่'])
            date_df = date_df.sort_values('วันที่')
            fig_line = px.area(
                date_df, x='วันที่', y='จำนวน',
                color_discrete_sequence=['#2563eb'],
                template='plotly_white',
                markers=True,
            )
            fig_line.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(family='Sarabun', size=13),
                height=260,
                xaxis_title="วันที่",
                yaxis_title="จำนวนรายงาน",
            )
            fig_line.update_traces(
                line=dict(width=2.5),
                marker=dict(size=7),
                fillcolor='rgba(37,99,235,0.12)'
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # =====================================================
        # ตารางสรุป
        # =====================================================
        st.markdown('<div class="section-header"><h4>📋 สรุปรายการล่าสุด 10 รายการ</h4></div>',
                    unsafe_allow_html=True)
        latest = sorted(records, key=lambda x: x.get('createdAt', ''), reverse=True)[:10]
        summary_df = pd.DataFrame([{
            'รหัส':       r.get('id'),
            'วันที่':     r.get('date'),
            'สาย':        r.get('line', '–'),
            'สถานี':      r.get('station', '–'),
            'ประเภท':     r.get('type', '–'),
            'ความรุนแรง': SEVERITY_MAP.get(r.get('severity'), '–'),
            'สถานะ':      STATUS_MAP.get(r.get('status'), '–'),
            'ผู้รายงาน':  r.get('reporter', '–'),
        } for r in latest])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
