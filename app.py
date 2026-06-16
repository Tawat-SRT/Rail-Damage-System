"""
Rail Damage Reporting System - Streamlit Application
ระบบรายงานรางชำรุดหักแตกร้าว (Custom UI Version)
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

# ----------------- 1. ตั้งค่าหน้าเพจ (Page Config) -----------------
st.set_page_config(
    page_title="ระบบรายงานรางชำรุดหักแตกร้าว",
    page_icon="🛤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- 2. ตกแต่งหน้าตา (Custom CSS) -----------------
# แทรก CSS เพื่อปรับฟอนต์ สีพื้นหลัง และการ์ด ให้เหมือนไฟล์ App Rail.html
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&display=swap');
    
    /* บังคับใช้ฟอนต์ Sarabun ทั้งระบบ */
    html, body, [class*="css"]  {
        font-family: 'Sarabun', sans-serif !important;
    }
    
    /* สีพื้นหลังของแอป */
    .stApp {
        background-color: #f0f4f8;
    }
    
    /* ตกแต่งแถบด้านข้าง (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* ตกแต่งแถบหัวเว็บ (Topbar) */
    .topbar-header {
        background: linear-gradient(135deg, #1a3a6b 0%, #1e4d9e 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 15px;
        box-shadow: 0 4px 12px rgba(26,58,107,0.2);
    }
    .topbar-title {
        font-size: 22px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .topbar-sub {
        font-size: 13px;
        opacity: 0.8;
        font-weight: 300;
    }
    .topbar-icon {
        font-size: 32px;
        background: rgba(255,255,255,0.15);
        padding: 10px;
        border-radius: 10px;
    }
    
    /* ตกแต่งกล่องตัวเลข (Metrics) */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-top: 4px solid #1e4d9e;
    }
    
    /* ตกแต่งกล่องฟอร์ม */
    [data-testid="stForm"] {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: none;
    }
    
    /* ปุ่มต่างๆ */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- 3. ส่วนจัดการฐานข้อมูล (JSON) -----------------
DATA_FILE = 'data/rail_damage_records.json'
Path('data').mkdir(exist_ok=True)

def load_records():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return []
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

DEPARTMENTS = [
    "ศูนย์อาคารและสถานที่", "กองบำรุงอาคารสถานที่เขตกรุงเทพ", "พสถ.กรุงเทพ",
    "พสถ.เชียงใหม่", "พสถ.ขอนแก่น", "พสถ.นครราชสีมา", "พสถ.อุดรธานี",
    "พสถ.นครสวรรค์", "พสถ.สมุทรปราการ", "พสถ.ชลบุรี"
]
SEVERITY_MAP = {'low': 'ต่ำ', 'med': 'ปานกลาง', 'high': 'สูง'}
STATUS_MAP = {'pending': 'รอดำเนินการ', 'inprog': 'กำลังซ่อมแซม', 'done': 'ซ่อมแซมแล้ว'}

records = load_records()

# ----------------- 4. โครงสร้างหน้าจอ (Layout) -----------------

# แถบหัวเว็บจำลอง (Topbar)
st.markdown("""
<div class="topbar-header">
    <div class="topbar-icon">🛤️</div>
    <div>
        <div class="topbar-title">ระบบรายงานรางชำรุดหักแตกร้าว</div>
        <div class="topbar-sub">Rail Damage Reporting System · การรถไฟแห่งประเทศไทย</div>
    </div>
</div>
""", unsafe_allow_html=True)

# เมนูด้านข้าง (Sidebar)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/th/thumb/d/d5/State_Railway_of_Thailand_Logo.svg/1200px-State_Railway_of_Thailand_Logo.svg.png", width=80)
    st.markdown("### เมนูหลัก")
    menu = st.radio(
        "เลือกหน้าต่างการทำงาน",
        ["📝 แจ้งความเสียหาย", "📋 รายการแจ้งเหตุ", "📊 แดชบอร์ดสถิติ"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("เวอร์ชัน 1.0.0")

# ================= หน้า: แจ้งความเสียหาย =================
if menu == "📝 แจ้งความเสียหาย":
    st.markdown("### 📝 ส่งรายงานชำรุดใหม่")
    
    with st.form("new_report_form", clear_on_submit=True):
        st.markdown("#### ข้อมูลจุดเกิดเหตุ")
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("วันที่พบเหตุ")
            time_input = st.time_input("เวลาที่พบเหตุ")
            line_input = st.text_input("สายทาง (เช่น สายเหนือ) *")
            station_input = st.text_input("สถานีใกล้เคียง")
            km_input = st.text_input("กิโลเมตรที่ (KM)")
        with col2:
            rail_id_input = st.text_input("หมายเลขราง (Rail ID)")
            type_input = st.text_input("ประเภทความชำรุด (เช่น รางแตก) *")
            length_input = st.text_input("ความยาวชำรุด (เมตร/เซนติเมตร)")
            severity_input = st.selectbox("ระดับความรุนแรง *", options=list(SEVERITY_MAP.keys()), format_func=lambda x: SEVERITY_MAP[x])
        
        st.markdown("#### ข้อมูลเพิ่มเติม")
        detail_input = st.text_area("รายละเอียดเพิ่มเติม")
        action_input = st.text_area("การดำเนินการเบื้องต้น")
        
        st.markdown("#### ข้อมูลผู้รายงาน")
        col3, col4 = st.columns(2)
        with col3:
            reporter_input = st.text_input("ชื่อ-นามสกุล ผู้รายงาน *")
            position_input = st.text_input("ตำแหน่ง")
        with col4:
            dept_input = st.selectbox("หน่วยงาน/ฝ่าย", options=DEPARTMENTS)
            phone_input = st.text_input("เบอร์โทรศัพท์ติดต่อ")
            
        submit_btn = st.form_submit_button("💾 บันทึกข้อมูลรายงาน")
        
        if submit_btn:
            if not line_input or not type_input or not reporter_input:
                st.error("กรุณากรอกข้อมูลในช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
            else:
                new_record = {
                    'id': generate_id(),
                    'date': str(date_input),
                    'time': str(time_input),
                    'line': line_input,
                    'station': station_input,
                    'km': km_input,
                    'railId': rail_id_input,
                    'type': type_input,
                    'length': length_input,
                    'severity': severity_input,
                    'detail': detail_input,
                    'action': action_input,
                    'reporter': reporter_input,
                    'position': position_input,
                    'dept': dept_input,
                    'phone': phone_input,
                    'status': 'pending',
                    'createdAt': datetime.now().isoformat()
                }
                records.append(new_record)
                save_records(records)
                st.success(f"บันทึกรายงานสำเร็จ! รหัสเอกสารของคุณคือ: {new_record['id']}")

# ================= หน้า: รายการแจ้งเหตุ =================
elif menu == "📋 รายการแจ้งเหตุ":
    st.markdown("### 📋 รายการรายงานความเสียหายทั้งหมด")
    
    if len(records) > 0:
        # ปุ่มดาวน์โหลด
        output = StringIO()
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(['รหัส', 'วันที่', 'เวลา', 'สาย', 'สถานี', 'ประเภท', 'ความรุนแรง', 'สถานะ', 'ผู้รายงาน'])
        for r in records:
            writer.writerow([r.get('id'), r.get('date'), r.get('time'), r.get('line'), r.get('station'), r.get('type'), SEVERITY_MAP.get(r.get('severity'), ''), STATUS_MAP.get(r.get('status'), ''), r.get('reporter')])
        st.download_button(label="📥 ส่งออกเป็นไฟล์ CSV", data=output.getvalue().encode('utf-8-sig'), file_name='rail_damage.csv', mime='text/csv')
        
        st.markdown("<br>", unsafe_allow_html=True)

        for idx, r in enumerate(records):
            sev_label = SEVERITY_MAP.get(r.get('severity'), 'ไม่ระบุ')
            stat_label = STATUS_MAP.get(r.get('status'), 'รอดำเนินการ')
            
            # ใช้อีโมจิแทนจุดสีเพื่อความสวยงามบน Streamlit
            status_icon = "⏳" if r.get('status') == 'pending' else "🛠️" if r.get('status') == 'inprog' else "✅"
            
            with st.expander(f"{status_icon} [{r.get('id')}] สาย{r.get('line')} สถานี{r.get('station')} - {r.get('type')} (ความรุนแรง: {sev_label})"):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"**📅 วันที่พบเหตุ:** {r.get('date')} {r.get('time')}")
                    st.write(f"**📍 ตำแหน่ง:** KM ที่ {r.get('km')} | **ราง:** {r.get('railId')}")
                    st.write(f"**📝 รายละเอียด:** {r.get('detail')}")
                    st.write(f"**💡 การแก้ไขเบื้องต้น:** {r.get('action')}")
                with col_d2:
                    st.write(f"**👤 ผู้รายงาน:** {r.get('reporter')} ({r.get('dept')})")
                    st.write(f"**📞 ติดต่อ:** {r.get('phone')}")
                    
                    st.markdown("---")
                    # การจัดการสถานะ
                    new_status = st.selectbox(f"สถานะการซ่อมแซม", options=list(STATUS_MAP.keys()), index=list(STATUS_MAP.keys()).index(r.get('status', 'pending')), format_func=lambda x: STATUS_MAP[x], key=f"status_{r.get('id')}")
                    
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button("🔄 อัปเดตสถานะ", key=f"update_{r.get('id')}"):
                        records[idx]['status'] = new_status
                        save_records(records)
                        st.success("อัปเดตสถานะแล้ว!")
                        st.rerun()
                    if col_b2.button("🗑️ ลบข้อมูล", key=f"delete_{r.get('id')}"):
                        records.pop(idx)
                        save_records(records)
                        st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลรายงานในระบบ")

# ================= หน้า: แดชบอร์ด =================
elif menu == "📊 แดชบอร์ดสถิติ":
    st.markdown("### 📊 แดชบอร์ดภาพรวม")
    
    total = len(records)
    high = len([r for r in records if r.get('severity') == 'high'])
    pending = len([r for r in records if r.get('status') == 'pending'])
    done = len([r for r in records if r.get('status') == 'done'])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("รายงานทั้งหมด (รายการ)", total)
    col2.metric("ความรุนแรงสูง (รายการ)", high)
    col3.metric("รอดำเนินการ (รายการ)", pending)
    col4.metric("ซ่อมแซมแล้ว (รายการ)", done)
    
    if total > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### แยกตามระดับความรุนแรง")
            sev_data = pd.DataFrame([{ "ความรุนแรง": SEVERITY_MAP.get(r.get('severity')), "จำนวน": 1 } for r in records]).groupby("ความรุนแรง").count()
            st.bar_chart(sev_data)
        with c2:
            st.markdown("#### แยกตามสถานะการซ่อมแซม")
            stat_data = pd.DataFrame([{ "สถานะ": STATUS_MAP.get(r.get('status')), "จำนวน": 1 } for r in records]).groupby("สถานะ").count()
            st.bar_chart(stat_data)
    else:
        st.info("ยังไม่มีข้อมูลสำหรับสร้างกราฟ")
