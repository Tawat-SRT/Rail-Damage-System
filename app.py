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
</style>
""", unsafe_allow_html=True)

# ----------------- 3. Data / Constants -----------------
APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / 'data' / 'rail_damage_records.json'
DATA_FILE.parent.mkdir(exist_ok=True)

def load_records():
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
    "รางหัก (Rail Break)",
    "รางแตกร้าว (Rail Crack)",
    "รางชำรุด (Rail Defect)",
    "รางบิดเบี้ยว (Rail Twist)",
    "รางสึกกร่อน (Rail Wear)",
    "รอยเชื่อมแตก (Weld Fracture)",
    "หมอนรถไฟชำรุด (Sleeper Defect)",
    "หินโรยทางทรุด (Ballast Settlement)",
    "สลักยึดรางชำรุด (Fastener Defect)",
    "อื่นๆ",
]

SEVERITY_MAP = {'low': 'ต่ำ', 'med': 'ปานกลาง', 'high': 'สูง'}
STATUS_MAP   = {'pending': 'รอดำเนินการ', 'inprog': 'กำลังซ่อมแซม', 'done': 'ซ่อมแซมแล้ว'}

# สีบนแผนที่ตามประเภท
TYPE_MAP_COLORS = {
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
    menu = st.radio(
        "เมนู",
        ["📝 แจ้งความเสียหาย", "📋 รายการแจ้งเหตุ", "📊 แดชบอร์ดสถิติ"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:12px; opacity:0.6; text-align:center;'>
        เวอร์ชัน 2.2.0<br>
        อัปเดต: {datetime.now().strftime('%d/%m/%Y')}
        <div class="sidebar-credit">
            จัดทำโดย<br>
            กองทางถาวร และกองเทคนิคทางถาวร
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    with st.form("new_report_form", clear_on_submit=True):

        # ส่วนที่ 1
        st.markdown("##### 📍 ข้อมูลจุดเกิดเหตุ")
        c1, c2, c3 = st.columns(3)
        with c1:
            date_input    = st.date_input("📅 วันที่พบเหตุ", value=datetime.today())
        with c2:
            time_input    = st.time_input("⏰ เวลาที่พบเหตุ", value=datetime.now().time())
        with c3:
            line_input    = st.selectbox("🚆 สายทาง *",
                                         options=["-- เลือกสายทาง --"] + RAILWAY_LINES)

        c4, c5, c6 = st.columns(3)
        with c4:
            station_input = st.text_input("🏠 สถานีใกล้เคียง", placeholder="เช่น อยุธยา")
        with c5:
            km_input      = st.text_input("📏 กิโลเมตรที่ (KM)", placeholder="เช่น 71+500")
        with c6:
            rail_id_input = st.text_input("🔢 หมายเลขราง (Rail ID)", placeholder="เช่น R-01-L")

        st.markdown("<br>", unsafe_allow_html=True)

        # ส่วนที่ 2
        st.markdown("##### 🔧 ลักษณะความเสียหาย")
        c7, c8, c9 = st.columns(3)
        with c7:
            type_input    = st.selectbox("💥 ประเภทความชำรุด *",
                                         options=["-- เลือกประเภท --"] + DAMAGE_TYPES)
        with c8:
            length_input  = st.text_input("📐 ความยาว/ขนาดชำรุด", placeholder="เช่น 15 ซม.")
        with c9:
            severity_input = st.selectbox(
                "⚠️ ระดับความรุนแรง *",
                options=list(SEVERITY_MAP.keys()),
                format_func=lambda x: (
                    "🔴 สูง" if x == 'high' else
                    "🟡 ปานกลาง" if x == 'med' else
                    "🟢 ต่ำ"
                )
            )

        c10, c11 = st.columns(2)
        with c10:
            detail_input  = st.text_area("📝 รายละเอียดเพิ่มเติม",
                                          placeholder="อธิบายลักษณะความเสียหายโดยละเอียด...",
                                          height=110)
        with c11:
            action_input  = st.text_area("💡 การดำเนินการเบื้องต้น",
                                          placeholder="ระบุการดำเนินการที่ได้ดำเนินไปแล้ว...",
                                          height=110)

        c12, c13 = st.columns(2)
        with c12:
            lat_input = st.text_input("🌐 ละติจูด (Latitude)",
                                       placeholder="เช่น 14.3567  (ถ้าไม่กรอก ระบบจะใช้พิกัดสถานี)")
        with c13:
            lon_input = st.text_input("🌐 ลองจิจูด (Longitude)",
                                       placeholder="เช่น 100.5706")

        st.markdown("<br>", unsafe_allow_html=True)

        # ส่วนที่ 3
        st.markdown("##### 👤 ข้อมูลผู้รายงาน")
        c14, c15, c16 = st.columns(3)
        with c14:
            reporter_input = st.text_input("👤 ชื่อ-นามสกุล *", placeholder="ชื่อผู้รายงาน")
        with c15:
            position_input = st.text_input("💼 ตำแหน่ง", placeholder="เช่น นายช่างโยธา")
        with c16:
            phone_input    = st.text_input("📞 เบอร์โทรศัพท์", placeholder="เช่น 081-234-5678")

        dept_input = st.text_input(
            "🏢 หน่วยงาน/เขต *",
            placeholder="เช่น กองทางถาวร / แขวงบำรุงทาง / ตอนนายตรวจทาง / เขตพื้นที่"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("💾 บันทึกและส่งรายงาน", use_container_width=True)

        if submit_btn:
            errors = []
            if line_input  == "-- เลือกสายทาง --":   errors.append("สายทาง")
            if type_input  == "-- เลือกประเภท --":   errors.append("ประเภทความชำรุด")
            if not reporter_input.strip():             errors.append("ชื่อ-นามสกุลผู้รายงาน")
            if not dept_input.strip():                errors.append("หน่วยงาน/เขต")

            if errors:
                st.error(f"⚠️ กรุณากรอก/เลือก: {', '.join(errors)}")
            else:
                try:
                    lat = float(lat_input) if lat_input.strip() else None
                    lon = float(lon_input) if lon_input.strip() else None
                except ValueError:
                    lat = lon = None

                if lat is None or lon is None:
                    for k, v in STATION_COORDS.items():
                        if k in station_input:
                            lat, lon = v
                            break

                new_record = {
                    'id':        generate_id(),
                    'date':      str(date_input),
                    'time':      str(time_input),
                    'line':      line_input,
                    'station':   station_input,
                    'km':        km_input,
                    'railId':    rail_id_input,
                    'type':      type_input,
                    'length':    length_input,
                    'severity':  severity_input,
                    'detail':    detail_input,
                    'action':    action_input,
                    'lat':       lat,
                    'lon':       lon,
                    'reporter':  reporter_input,
                    'position':  position_input,
                    'dept':      dept_input.strip(),
                    'phone':     phone_input,
                    'status':    'pending',
                    'createdAt': datetime.now().isoformat()
                }
                records.append(new_record)
                save_records(records)
                st.success(f"✅ บันทึกรายงานสำเร็จ! รหัสเอกสาร: **{new_record['id']}**")
                st.balloons()


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
            writer.writerow(['รหัส','วันที่','เวลา','สาย','สถานี','ประเภท',
                              'ความรุนแรง','สถานะ','ผู้รายงาน','หน่วยงาน'])
            for r in records:
                writer.writerow([
                    r.get('id'), r.get('date'), r.get('time'), r.get('line'),
                    r.get('station'), r.get('type'),
                    SEVERITY_MAP.get(r.get('severity'), ''),
                    STATUS_MAP.get(r.get('status'), ''),
                    r.get('reporter'), r.get('dept')
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

            with st.expander(
                f"{status_icon} {sev_icon} [{r.get('id')}]  "
                f"{r.get('line','–')}  |  "
                f"สถานี {r.get('station','–')}  |  "
                f"{r.get('type','–')}  |  ความรุนแรง: {sev_label}"
            ):
                cd1, cd2 = st.columns(2)
                with cd1:
                    st.markdown(f"**📅 วันที่-เวลา:** {r.get('date')} เวลา {r.get('time')}")
                    st.markdown(f"**📍 ตำแหน่ง:** KM {r.get('km','–')}  |  ราง: {r.get('railId','–')}")
                    st.markdown(f"**💥 ประเภท:** {r.get('type','–')}")
                    st.markdown(f"**📐 ขนาด:** {r.get('length','–')}")
                    st.markdown(f"**📝 รายละเอียด:** {r.get('detail','–')}")
                    st.markdown(f"**💡 การดำเนินการ:** {r.get('action','–')}")
                with cd2:
                    st.markdown(f"**👤 ผู้รายงาน:** {r.get('reporter','–')}")
                    st.markdown(f"**💼 ตำแหน่ง:** {r.get('position','–')}")
                    st.markdown(f"**🏢 หน่วยงาน:** {r.get('dept','–')}")
                    st.markdown(f"**📞 ติดต่อ:** {r.get('phone','–')}")
                    st.markdown("---")
                    new_status = st.selectbox(
                        "🔄 สถานะการซ่อมแซม",
                        options=list(STATUS_MAP.keys()),
                        index=list(STATUS_MAP.keys()).index(r.get('status', 'pending')),
                        format_func=lambda x: STATUS_MAP[x],
                        key=f"status_{r.get('id')}"
                    )
                    cb1, cb2 = st.columns(2)
                    if cb1.button("🔄 อัปเดต", key=f"upd_{r.get('id')}"):
                        records[orig_idx]['status'] = new_status
                        save_records(records)
                        st.success("อัปเดตแล้ว!")
                        st.rerun()
                    if cb2.button("🗑️ ลบ", key=f"del_{r.get('id')}"):
                        records.pop(orig_idx)
                        save_records(records)
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
