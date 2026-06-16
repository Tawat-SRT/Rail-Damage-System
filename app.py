"""
Rail Damage Reporting System - Streamlit Application (Enhanced)
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
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# ----------------- 1. Page Config -----------------
st.set_page_config(
    page_title="ระบบรายงานรางชำรุดหักแตกร้าว",
    page_icon="🛤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- 2. Custom CSS -----------------
st.markdown("""
<style>
    @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&display=swap)');

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

    /* Topbar */
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

    /* Section header */
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

    /* Metrics */
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

    /* Form */
    [data-testid="stForm"] {
        background: white;
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.07);
        border: 1px solid #e2e8f0;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }

    /* Buttons */
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

    /* Inputs */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-family: 'Sarabun', sans-serif !important;
    }
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }

    /* Badge */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-high { background: #fee2e2; color: #dc2626; }
    .badge-med  { background: #fef3c7; color: #d97706; }
    .badge-low  { background: #dcfce7; color: #16a34a; }

    .info-card {
        background: white;
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.07);
        margin-bottom: 16px;
        border: 1px solid #f1f5f9;
    }

    /* Sidebar logo area */
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
</style>
""", unsafe_allow_html=True)

# ----------------- 3. Data / Constants -----------------
DATA_FILE = 'data/rail_damage_records.json'
Path('data').mkdir(exist_ok=True)

def load_records():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_records(records):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def generate_id():
    records = load_records()
    year = datetime.now().year
    num = len(records) + 1
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

# สายทาง
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

# ประเภทความชำรุด
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

SEVERITY_MAP  = {'low': 'ต่ำ', 'med': 'ปานกลาง', 'high': 'สูง'}
STATUS_MAP    = {'pending': 'รอดำเนินการ', 'inprog': 'กำลังซ่อมแซม', 'done': 'ซ่อมแซมแล้ว'}

SEVERITY_COLORS = {'low': '#16a34a', 'med': '#d97706', 'high': '#dc2626'}
STATUS_COLORS   = {'pending': '#6366f1', 'inprog': '#f59e0b', 'done': '#10b981'}

# พิกัดสถานีหลัก (ตัวอย่างสำหรับแผนที่)
STATION_COORDS = {
    "กรุงเทพ": (13.7437, 100.5316),
    "ดอนเมือง": (13.9135, 100.6066),
    "อยุธยา": (14.3567, 100.5706),
    "ลพบุรี": (14.7994, 100.6536),
    "นครสวรรค์": (15.7030, 100.1373),
    "พิษณุโลก": (16.8239, 100.2659),
    "ลำปาง": (18.2855, 99.4931),
    "เชียงใหม่": (18.7967, 98.9665),
    "แก่งคอย": (14.5882, 101.1516),
    "นครราชสีมา": (14.9799, 102.0978),
    "ขอนแก่น": (16.4419, 102.8360),
    "อุดรธานี": (17.4138, 102.7876),
    "สุรินทร์": (14.8827, 103.4956),
    "ศรีสะเกษ": (15.1186, 104.3220),
    "อุบลราชธานี": (15.2448, 104.8473),
    "ชุมพร": (10.4930, 99.1800),
    "สุราษฎร์ธานี": (9.1400, 99.3308),
    "ทุ่งสง": (8.1617, 99.6756),
    "หาดใหญ่": (7.0086, 100.4747),
    "ยะลา": (6.5425, 101.2800),
    "ฉะเชิงเทรา": (13.6909, 101.0724),
    "ปราจีนบุรี": (14.0511, 101.3661),
    "สระแก้ว": (13.8240, 102.0643),
    "ชลบุรี": (13.3611, 100.9847),
    "ศรีราชา": (13.1282, 100.9235),
    "กาญจนบุรี": (14.0227, 99.5328),
    "เพชรบุรี": (13.1119, 99.9392),
    "หัวหิน": (12.5706, 99.9578),
    "ประจวบคีรีขันธ์": (11.8131, 99.7967),
    "บางซื่อ": (13.8036, 100.5295),
    "ธนบุรี": (13.7269, 100.4836),
    "มักกะสัน": (13.7500, 100.5611),
}

records = load_records()

# ----------------- 4. Sidebar -----------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <img src="[upload.wikimedia.org](https://upload.wikimedia.org/wikipedia/th/thumb/d/d5/State_Railway_of_Thailand_Logo.svg/1200px-State_Railway_of_Thailand_Logo.svg.png)"
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
        เวอร์ชัน 2.0.0<br>
        อัปเดต: {datetime.now().strftime('%d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)

# Topbar
st.markdown("""
<div class="topbar-header">
    <div class="topbar-icon">🛤️</div>
    <div>
        <div class="topbar-title">ระบบรายงานรางชำรุดหักแตกร้าว</div>
        <div class="topbar-sub">Rail Damage Reporting System · การรถไฟแห่งประเทศไทย (SRT)</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ===============================================================
# หน้า 1: แจ้งความเสียหาย
# ===============================================================
if menu == "📝 แจ้งความเสียหาย":
    st.markdown("""
    <div class="section-header"><h4>📝 ส่งรายงานรางชำรุดใหม่</h4></div>
    """, unsafe_allow_html=True)

    with st.form("new_report_form", clear_on_submit=True):

        # === ส่วนที่ 1: ข้อมูลจุดเกิดเหตุ ===
        st.markdown("##### 📍 ข้อมูลจุดเกิดเหตุ")
        c1, c2, c3 = st.columns(3)
        with c1:
            date_input     = st.date_input("📅 วันที่พบเหตุ", value=datetime.today())
        with c2:
            time_input     = st.time_input("⏰ เวลาที่พบเหตุ", value=datetime.now().time())
        with c3:
            line_input     = st.selectbox("🚆 สายทาง *", options=["-- เลือกสายทาง --"] + RAILWAY_LINES)

        c4, c5, c6 = st.columns(3)
        with c4:
            station_input  = st.text_input("🏠 สถานีใกล้เคียง", placeholder="เช่น สถานีอยุธยา")
        with c5:
            km_input       = st.text_input("📏 กิโลเมตรที่ (KM)", placeholder="เช่น 71+500")
        with c6:
            rail_id_input  = st.text_input("🔢 หมายเลขราง (Rail ID)", placeholder="เช่น R-01-L")

        st.markdown("<br>", unsafe_allow_html=True)

        # === ส่วนที่ 2: ลักษณะความเสียหาย ===
        st.markdown("##### 🔧 ลักษณะความเสียหาย")
        c7, c8, c9 = st.columns(3)
        with c7:
            type_input     = st.selectbox("💥 ประเภทความชำรุด *", options=["-- เลือกประเภท --"] + DAMAGE_TYPES)
        with c8:
            length_input   = st.text_input("📐 ความยาว/ขนาดชำรุด", placeholder="เช่น 15 ซม.")
        with c9:
            severity_input = st.selectbox(
                "⚠️ ระดับความรุนแรง *",
                options=list(SEVERITY_MAP.keys()),
                format_func=lambda x: f"{'🔴' if x=='high' else '🟡' if x=='med' else '🟢'} {SEVERITY_MAP[x]}"
            )

        c10, c11 = st.columns(2)
        with c10:
            detail_input   = st.text_area("📝 รายละเอียดเพิ่มเติม", placeholder="อธิบายลักษณะความเสียหายโดยละเอียด...", height=110)
        with c11:
            action_input   = st.text_area("💡 การดำเนินการเบื้องต้น", placeholder="ระบุการดำเนินการที่ได้ดำเนินไปแล้ว...", height=110)

        # พิกัด GPS
        c12, c13 = st.columns(2)
        with c12:
            lat_input      = st.text_input("🌐 ละติจูด (Latitude)", placeholder="เช่น 14.3567")
        with c13:
            lon_input      = st.text_input("🌐 ลองจิจูด (Longitude)", placeholder="เช่น 100.5706")

        st.markdown("<br>", unsafe_allow_html=True)

        # === ส่วนที่ 3: ข้อมูลผู้รายงาน ===
        st.markdown("##### 👤 ข้อมูลผู้รายงาน")
        c14, c15, c16 = st.columns(3)
        with c14:
            reporter_input = st.text_input("👤 ชื่อ-นามสกุล *", placeholder="ชื่อผู้รายงาน")
        with c15:
            position_input = st.text_input("💼 ตำแหน่ง", placeholder="เช่น นายช่างโยธา")
        with c16:
            phone_input    = st.text_input("📞 เบอร์โทรศัพท์", placeholder="เช่น 081-234-5678")

        dept_input = st.selectbox("🏢 หน่วยงาน/แขวง *", options=["-- เลือกหน่วยงาน --"] + DEPARTMENTS)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("💾 บันทึกและส่งรายงาน", use_container_width=True)

        if submit_btn:
            errors = []
            if line_input     == "-- เลือกสายทาง --":  errors.append("สายทาง")
            if type_input     == "-- เลือกประเภท --":  errors.append("ประเภทความชำรุด")
            if not reporter_input.strip():               errors.append("ชื่อ-นามสกุลผู้รายงาน")
            if dept_input     == "-- เลือกหน่วยงาน --": errors.append("หน่วยงาน")

            if errors:
                st.error(f"⚠️ กรุณากรอก/เลือก: {', '.join(errors)}")
            else:
                # แปลงพิกัด
                try:
                    lat = float(lat_input) if lat_input.strip() else None
                    lon = float(lon_input) if lon_input.strip() else None
                except ValueError:
                    lat = lon = None

                # ถ้าไม่มีพิกัด ใช้พิกัดสถานีใกล้เคียงถ้าหาได้
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
                    'dept':      dept_input,
                    'phone':     phone_input,
                    'status':    'pending',
                    'createdAt': datetime.now().isoformat()
                }
                records.append(new_record)
                save_records(records)
                st.success(f"✅ บันทึกรายงานสำเร็จ! รหัสเอกสาร: **{new_record['id']}**")
                st.balloons()


# ===============================================================
# หน้า 2: รายการแจ้งเหตุ
# ===============================================================
elif menu == "📋 รายการแจ้งเหตุ":
    st.markdown("""
    <div class="section-header"><h4>📋 รายการรายงานความเสียหายทั้งหมด</h4></div>
    """, unsafe_allow_html=True)

    if len(records) == 0:
        st.info("ยังไม่มีข้อมูลรายงานในระบบ")
    else:
        # ---- Filter bar ----
        fc1, fc2, fc3, fc4 = st.columns([2, 2, 2, 1])
        with fc1:
            f_line = st.selectbox("กรองตามสายทาง", ["ทั้งหมด"] + RAILWAY_LINES)
        with fc2:
            f_sev  = st.selectbox("กรองตามความรุนแรง",
                                  ["ทั้งหมด"] + [SEVERITY_MAP[k] for k in SEVERITY_MAP])
        with fc3:
            f_stat = st.selectbox("กรองตามสถานะ",
                                  ["ทั้งหมด"] + [STATUS_MAP[k] for k in STATUS_MAP])
        with fc4:
            st.markdown("<br>", unsafe_allow_html=True)
            # Export
            output = StringIO()
            writer = csv.writer(output, lineterminator='\n')
            writer.writerow(['รหัส','วันที่','เวลา','สาย','สถานี','ประเภท','ความรุนแรง','สถานะ','ผู้รายงาน','หน่วยงาน'])
            for r in records:
                writer.writerow([r.get('id'), r.get('date'), r.get('time'), r.get('line'),
                                  r.get('station'), r.get('type'),
                                  SEVERITY_MAP.get(r.get('severity'), ''),
                                  STATUS_MAP.get(r.get('status'), ''),
                                  r.get('reporter'), r.get('dept')])
            st.download_button("📥 CSV", data=output.getvalue().encode('utf-8-sig'),
                               file_name='rail_damage.csv', mime='text/csv')

        # Apply filters
        filtered = records
        if f_line != "ทั้งหมด":
            filtered = [r for r in filtered if r.get('line') == f_line]
        if f_sev  != "ทั้งหมด":
            filtered = [r for r in filtered if SEVERITY_MAP.get(r.get('severity')) == f_sev]
        if f_stat != "ทั้งหมด":
            filtered = [r for r in filtered if STATUS_MAP.get(r.get('status')) == f_stat]

        st.caption(f"แสดง {len(filtered)} รายการ จากทั้งหมด {len(records)} รายการ")
        st.markdown("<br>", unsafe_allow_html=True)

        for idx, r in enumerate(filtered):
            orig_idx  = records.index(r)
            sev_label = SEVERITY_MAP.get(r.get('severity'), 'ไม่ระบุ')
            sev_key   = r.get('severity', 'low')
            sev_color = {'high': '🔴', 'med': '🟡', 'low': '🟢'}.get(sev_key, '⚪')
            status_icon = {"pending": "⏳", "inprog": "🛠️", "done": "✅"}.get(r.get('status'), "⏳")

            with st.expander(
                f"{status_icon} {sev_color} [{r.get('id')}]  "
                f"{r.get('line','–')}  |  "
                f"สถานี{r.get('station','–')}  |  "
                f"{r.get('type','–')}  |  "
                f"ความรุนแรง: {sev_label}"
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


# ===============================================================
# หน้า 3: แดชบอร์ดสถิติ
# ===============================================================
elif menu == "📊 แดชบอร์ดสถิติ":
    st.markdown("""
    <div class="section-header"><h4>📊 แดชบอร์ดภาพรวมสถิติ</h4></div>
    """, unsafe_allow_html=True)

    total   = len(records)
    high    = len([r for r in records if r.get('severity') == 'high'])
    pending = len([r for r in records if r.get('status') == 'pending'])
    inprog  = len([r for r in records if r.get('status') == 'inprog'])
    done    = len([r for r in records if r.get('status') == 'done'])

    # --- KPI Row ---
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📋 รายงานทั้งหมด", total)
    k2.metric("🔴 ความรุนแรงสูง", high)
    k3.metric("⏳ รอดำเนินการ", pending)
    k4.metric("🛠️ กำลังซ่อมแซม", inprog)
    k5.metric("✅ ซ่อมแซมแล้ว", done)

    st.markdown("<br>", unsafe_allow_html=True)

    if total == 0:
        st.info("📭 ยังไม่มีข้อมูลสำหรับสร้างแดชบอร์ด กรุณาแจ้งความเสียหายก่อน")
    else:
        # =====================================================
        # แผนที่
        # =====================================================
        st.markdown("""<div class="section-header"><h4>🗺️ แผนที่จุดเกิดเหตุ</h4></div>""",
                    unsafe_allow_html=True)

        map_records = [r for r in records if r.get('lat') and r.get('lon')]

        if len(map_records) == 0:
            st.info("⚠️ ยังไม่มีข้อมูลพิกัดสำหรับแสดงบนแผนที่  "
                    "กรุณากรอก ละติจูด/ลองจิจูด หรือชื่อสถานี ตอนแจ้งเหตุ")
        else:
            # สีตามประเภทความเสียหาย
            type_color_map = {
                "รางหัก (Rail Break)":       "red",
                "รางแตกร้าว (Rail Crack)":   "orange",
                "รางชำรุด (Rail Defect)":    "blue",
                "รางบิดเบี้ยว (Rail Twist)": "purple",
                "รางสึกกร่อน (Rail Wear)":   "gray",
                "รอยเชื่อมแตก (Weld Fracture)": "darkred",
                "หมอนรถไฟชำรุด (Sleeper Defect)": "cadetblue",
                "หินโรยทางทรุด (Ballast Settlement)": "beige",
                "สลักยึดรางชำรุด (Fastener Defect)": "darkblue",
            }

            avg_lat = sum(r['lat'] for r in map_records) / len(map_records)
            avg_lon = sum(r['lon'] for r in map_records) / len(map_records)
            m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6,
                           tiles="CartoDB positron")

            for r in map_records:
                icon_color = type_color_map.get(r.get('type', ''), 'blue')
                sev_icon   = {'high': 'exclamation-sign', 'med': 'warning-sign', 'low': 'info-sign'}.get(r.get('severity'), 'info-sign')
                popup_html = f"""
                <div style='font-family:Sarabun,sans-serif; min-width:220px'>
                    <b style='color:#1a3a6b'>{r.get('id')}</b><br>
                    <b>สาย:</b> {r.get('line','–')}<br>
                    <b>สถานี:</b> {r.get('station','–')} (KM {r.get('km','–')})<br>
                    <b>ประเภท:</b> {r.get('type','–')}<br>
                    <b>ความรุนแรง:</b> {SEVERITY_MAP.get(r.get('severity'),'–')}<br>
                    <b>สถานะ:</b> {STATUS_MAP.get(r.get('status'),'–')}<br>
                    <b>วันที่:</b> {r.get('date','–')}<br>
                    <b>ผู้รายงาน:</b> {r.get('reporter','–')}
                </div>"""
                folium.Marker(
                    location=[r['lat'], r['lon']],
                    popup=folium.Popup(popup_html, max_width=280),
                    tooltip=f"{r.get('type','–')} | {r.get('station','–')}",
                    icon=folium.Icon(color=icon_color, icon=sev_icon, prefix='glyphicon')
                ).add_to(m)

            # Legend
            legend_html = """
            <div style='position:fixed; bottom:30px; left:30px; z-index:1000;
                        background:white; padding:12px 16px; border-radius:10px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.15); font-family:Sarabun,sans-serif; font-size:13px'>
                <b>ประเภทความเสียหาย</b><br>
                🔴 รางหัก &nbsp; 🟠 รางแตกร้าว &nbsp; 🔵 รางชำรุด<br>
                🟣 รางบิดเบี้ยว &nbsp; ⚫ รางสึกกร่อน &nbsp; 🟤 รอยเชื่อมแตก
            </div>"""
            m.get_root().html.add_child(folium.Element(legend_html))

            st_folium(m, width="100%", height=480)

        st.markdown("<br>", unsafe_allow_html=True)

        # =====================================================
        # Charts row 1: ประเภท + พื้นที่เกิดบ่อย
        # =====================================================
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown("""<div class="section-header"><h4>💥 สถิติประเภทความเสียหาย</h4></div>""",
                        unsafe_allow_html=True)
            type_counts = {}
            for r in records:
                t = r.get('type', 'ไม่ระบุ')
                type_counts[t] = type_counts.get(t, 0) + 1
            type_df = pd.DataFrame({'ประเภท': list(type_counts.keys()),
                                    'จำนวน': list(type_counts.values())})
            type_df = type_df.sort_values('จำนวน', ascending=True)
            fig_type = px.bar(
                type_df, x='จำนวน', y='ประเภท', orientation='h',
                color='จำนวน',
                color_continuous_scale=['#93c5fd', '#1e4d9e', '#1a3a6b'],
                template='plotly_white'
            )
            fig_type.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(family='Sarabun', size=13),
                showlegend=False,
                coloraxis_showscale=False,
                height=320
            )
            st.plotly_chart(fig_type, use_container_width=True)

        with ch2:
            st.markdown("""<div class="section-header"><h4>📍 พื้นที่/สถานีที่เกิดบ่อย (Top 10)</h4></div>""",
                        unsafe_allow_html=True)
            station_counts = {}
            for r in records:
                s = r.get('station') or r.get('line', 'ไม่ระบุ')
                if not s:
                    s = 'ไม่ระบุ'
                station_counts[s] = station_counts.get(s, 0) + 1
            top_stations = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            sta_df = pd.DataFrame(top_stations, columns=['สถานี', 'จำนวน'])
            sta_df = sta_df.sort_values('จำนวน', ascending=True)
            fig_sta = px.bar(
                sta_df, x='จำนวน', y='สถานี', orientation='h',
                color='จำนวน',
                color_continuous_scale=['#bbf7d0', '#16a34a', '#14532d'],
                template='plotly_white'
            )
            fig_sta.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(family='Sarabun', size=13),
                showlegend=False,
                coloraxis_showscale=False,
                height=320
            )
            st.plotly_chart(fig_sta, use_container_width=True)

        # =====================================================
        # Charts row 2: สถานะ + ความรุนแรง
        # =====================================================
        ch3, ch4 = st.columns(2)

        with ch3:
            st.markdown("""<div class="section-header"><h4>🔧 สถานะการซ่อมแซม</h4></div>""",
                        unsafe_allow_html=True)
            stat_counts = {STATUS_MAP[k]: len([r for r in records if r.get('status') == k])
                           for k in STATUS_MAP}
            fig_stat = go.Figure(go.Pie(
                labels=list(stat_counts.keys()),
                values=list(stat_counts.values()),
                marker_colors=['#6366f1', '#f59e0b', '#10b981'],
                hole=0.5,
                textinfo='label+percent+value',
                textfont=dict(family='Sarabun', size=13)
            ))
            fig_stat.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(family='Sarabun', size=13),
                showlegend=True,
                height=300,
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_stat, use_container_width=True)

        with ch4:
            st.markdown("""<div class="section-header"><h4>⚠️ ระดับความรุนแรง</h4></div>""",
                        unsafe_allow_html=True)
            sev_counts = {SEVERITY_MAP[k]: len([r for r in records if r.get('severity') == k])
                          for k in SEVERITY_MAP}
            fig_sev = go.Figure(go.Pie(
                labels=list(sev_counts.keys()),
                values=list(sev_counts.values()),
                marker_colors=['#16a34a', '#d97706', '#dc2626'],
                hole=0.5,
                textinfo='label+percent+value',
                textfont=dict(family='Sarabun', size=13)
            ))
            fig_sev.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                font=dict(family='Sarabun', size=13),
                showlegend=True,
                height=300,
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
            )
            st.plotly_chart(fig_sev, use_container_width=True)

        # =====================================================
        # Timeline
        # =====================================================
        st.markdown("""<div class="section-header"><h4>📈 แนวโน้มการรายงานตามวัน</h4></div>""",
                    unsafe_allow_html=True)
        date_counts = {}
        for r in records:
            d = r.get('date', '')
            if d:
                date_counts[d] = date_counts.get(d, 0) + 1
        if date_counts:
            date_df = pd.DataFrame({'วันที่': list(date_counts.keys()),
                                    'จำนวน': list(date_counts.values())})
            date_df['วันที่'] = pd.to_datetime(date_df['วันที่'])
            date_df = date_df.sort_values('วันที่')
            fig_line = px.area(
                date_df, x='วันที่', y='จำนวน',
                color_discrete_sequence=['#2563eb'],
                template='plotly_white',
                markers=True
            )
            fig_line.update_layout(
                margin=dict(l=0, r=0, t=10, b=0),
                font=dict(family='Sarabun', size=13),
                height=260
            )
            fig_line.update_traces(
                line=dict(width=2.5),
                marker=dict(size=7),
                fillcolor='rgba(37,99,235,0.12)'
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # =====================================================
        # สรุปตาราง
        # =====================================================
        st.markdown("""<div class="section-header"><h4>📋 สรุปรายการล่าสุด (10 รายการ)</h4></div>""",
                    unsafe_allow_html=True)
        latest = sorted(records, key=lambda x: x.get('createdAt', ''), reverse=True)[:10]
        summary_df = pd.DataFrame([{
            'รหัส':        r.get('id'),
            'วันที่':      r.get('date'),
            'สาย':         r.get('line','–'),
            'สถานี':       r.get('station','–'),
            'ประเภท':      r.get('type','–'),
            'ความรุนแรง':  SEVERITY_MAP.get(r.get('severity'),'–'),
            'สถานะ':       STATUS_MAP.get(r.get('status'),'–'),
            'ผู้รายงาน':  r.get('reporter','–'),
        } for r in latest])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
