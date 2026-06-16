"""
Rail Damage Reporting System - Streamlit Application
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

# ตั้งค่าหน้าตาของแอปพลิเคชัน
st.set_page_config(
    page_title="ระบบรายงานรางชำรุดหักแตกร้าว",
    page_icon="🛤️",
    layout="wide"
)

# ----------------- ส่วนจัดการฐานข้อมูล (JSON) -----------------
DATA_FILE = 'data/rail_damage_records.json'
Path('data').mkdir(exist_ok=True)

def load_records():
    """โหลดข้อมูลทั้งหมดจากไฟล์ JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_records(records):
    """บันทึกข้อมูลลงไฟล์ JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def generate_id():
    """สร้างรหัสรายงานแบบไม่ซ้ำ (Unique ID)"""
    records = load_records()
    year = datetime.now().year
    num = len(records) + 1
    suffix = ''.join([chr(random.randint(65, 90)) for _ in range(3)])
    return f'RPT-{year}-{num:04d}-{suffix}'

# ----------------- ข้อมูลมาสเตอร์ (Constants) -----------------
DEPARTMENTS = [
    "ศูนย์อาคารและสถานที่", "กองบำรุงอาคารสถานที่เขตกรุงเทพ", "พสถ.กรุงเทพ",
    "พสถ.เชียงใหม่", "พสถ.ขอนแก่น", "พสถ.นครราชสีมา", "พสถ.อุดรธานี",
    "พสถ.นครสวรรค์", "พสถ.สมุทรปราการ", "พสถ.ชลบุรี"
]

SEVERITY_MAP = {'low': 'ต่ำ', 'med': 'ปานกลาง', 'high': 'สูง'}
STATUS_MAP = {'pending': 'รอดำเนินการ', 'inprog': 'กำลังซ่อมแซม', 'done': 'ซ่อมแซมแล้ว'}

# ----------------- หน้าตาโปรแกรม (UI) -----------------
st.title("🛤️ ระบบรายงานรางชำรุดหักแตกร้าว")
st.markdown("---")

# แบ่งหน้าจอเป็น 3 แท็บหลัก (แดชบอร์ด, รายงานใหม่, จัดการข้อมูล)
tab1, tab2, tab3 = st.tabs(["📊 แดชบอร์ดสถิติ", "📝 ส่งรายงานชำรุดใหม่", "📋 รายการรายงานทั้งหมด"])

records = load_records()

# ================= TAB 1: แดชบอร์ดสถิติ =================
with tab1:
    st.header("ภาพรวมและสถิติข้อมูล")
    
    total_reports = len(records)
    high_severity = len([r for r in records if r.get('severity') == 'high'])
    pending_status = len([r for r in records if r.get('status') == 'pending'])
    resolved_status = len([r for r in records if r.get('status') == 'done'])
    
    # แสดงการ์ดตัวเลข (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("รายงานทั้งหมด", f"{total_reports} รายการ")
    col2.metric("ความรุนแรงสูง 🚨", f"{high_severity} รายการ")
    col3.metric("รอดำเนินการ ⏳", f"{pending_status} รายการ")
    col4.metric("ซ่อมแซมแล้ว ✅", f"{resolved_status} รายการ")
    
    if total_reports > 0:
        st.markdown("### สถิติแยกตามประเภท")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("ระดับความรุนแรง")
            sev_data = {}
            for sev, name in SEVERITY_MAP.items():
                sev_data[name] = len([r for r in records if r.get('severity') == sev])
            st.bar_chart(sev_data)
            
        with col_chart2:
            st.subheader("สถานะการดำเนินงาน")
            stat_data = {}
            for stat, name in STATUS_MAP.items():
                stat_data[name] = len([r for r in records if r.get('status') == stat])
            st.bar_chart(stat_data)
    else:
        st.info("ยังไม่มีข้อมูลในระบบที่จะนำมาแสดงสถิติได้")

# ================= TAB 2: ส่งรายงานชำรุดใหม่ =================
with tab2:
    st.header("ฟอร์มแจ้งรายงานรางชำรุด")
    
    with st.form("new_report_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            date_input = st.date_input("วันที่พบเหตุ", datetime.now())
            time_input = st.text_input("เวลาที่พบเหตุ (เช่น 14:30)", datetime.now().strftime("%H:%M"))
            line_input = st.text_input("สายทาง (เช่น สายเหนือ, สายใต้) *")
            station_input = st.text_input("สถานีใกล้เคียง")
            km_input = st.text_input("กิโลเมตรที่ (KM)")
            rail_id_input = st.text_input("หมายเลขราง (Rail ID)")
            
        with col_f2:
            type_input = st.text_input("ประเภทความชำรุด (เช่น รางแตก, รางร้าว) *")
            length_input = st.text_input("ความยาวชำรุด (เมตร/เซนติเมตร)")
            severity_input = st.selectbox("ระดับความรุนแรง *", options=list(SEVERITY_MAP.keys()), format_func=lambda x: SEVERITY_MAP[x])
            detail_input = st.text_area("รายละเอียดเพิ่มเติม")
            action_input = st.text_area("การดำเนินการเบื้องต้น")

        st.markdown("#### ข้อมูลผู้รายงาน")
        col_f3, col_f4 = st.columns(2)
        with col_f3:
            reporter_input = st.text_input("ชื่อ-นามสกุล ผู้รายงาน")
            position_input = st.text_input("ตำแหน่ง")
        with col_f4:
            dept_input = st.selectbox("หน่วยงาน/ฝ่าย", options=DEPARTMENTS)
            phone_input = st.text_input("เบอร์โทรศัพท์ติดต่อ")
            
        submit_btn = st.form_submit_button("💾 บันทึกรายงาน")
        
        if submit_btn:
            # ตรวจสอบข้อมูลบังคับกรอก (Validation)
            if not line_input or not type_input:
                st.error("กรุณากรอกข้อมูลในช่องที่มีเครื่องหมาย * ให้ครบถ้วน")
            else:
                new_record = {
                    'id': generate_id(),
                    'date': str(date_input),
                    'time': time_input,
                    'line': line_input,
                    'station': station_input,
                    'km': km_input,
                    'railId': rail_id_input,
                    'type': type_input,
                    'length': length_input,
                    'severity': severity_input,
                    'detail': detail_input,
                    'action': action_input,
                    'images': [],
                    'reporter': reporter_input,
                    'position': position_input,
                    'dept': dept_input,
                    'phone': phone_input,
                    'status': 'pending',
                    'dueDate': '',
                    'note': '',
                    'createdAt': datetime.now().isoformat(),
                    'updatedAt': datetime.now().isoformat()
                }
                
                records.append(new_record)
                save_records(records)
                st.success(f"บันทึกรายงานสำเร็จ! รหัสเอกสารของคุณคือ: {new_record['id']}")
                st.rerun()

# ================= TAB 3: รายการรายงานทั้งหมด =================
with tab3:
    st.header("รายการที่ถูกบันทึกไว้ในระบบ")
    
    if len(records) > 0:
        # ปุ่มสำหรับ Export เป็น CSV
        output = StringIO()
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(['รหัส', 'วันที่', 'เวลา', 'สาย', 'สถานี', 'ประเภท', 'ความรุนแรง', 'สถานะ', 'ผู้รายงาน'])
        for r in records:
            writer.writerow([
                r.get('id'), r.get('date'), r.get('time'), r.get('line'), r.get('station'),
                r.get('type'), SEVERITY_MAP.get(r.get('severity'), ''), STATUS_MAP.get(r.get('status'), ''), r.get('reporter')
            ])
        csv_data = output.getvalue()
        st.download_button(label="📥 ดาวน์โหลดข้อมูลทั้งหมดเป็น (.CSV)", data=csv_data.encode('utf-8-sig'), file_name='rail_damage_report.csv', mime='text/csv')
        
        st.markdown("---")
        
        # วนลูปแสดงรายงานแต่ละชิ้นด้วย Expander (กล่องพับเก็บได้)
        for idx, r in enumerate(records):
            severity_label = SEVERITY_MAP.get(r.get('severity'), 'ไม่ระบุ')
            status_label = STATUS_MAP.get(r.get('status'), 'รอดำเนินการ')
            
            expander_title = f"📋 [{r.get('id')}] สาย: {r.get('line')} | ประเภท: {r.get('type')} | ความรุนแรง: {severity_label} | สถานะ: {status_label}"
            
            with st.expander(expander_title):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"**📅 วันที่-เวลา:** {r.get('date')} {r.get('time')}")
                    st.write(f"**📍 สถานที่:** สาย {r.get('line')} สถานี {r.get('station')} (KM ที่ {r.get('km')})")
                    st.write(f"**🛠️ หมายเลขราง:** {r.get('railId')} | **ความยาวชำรุด:** {r.get('length')}")
                    st.write(f"**📝 รายละเอียด:** {r.get('detail')}")
                    st.write(f"**💡 การแก้ไขเบื้องต้น:** {r.get('action')}")
                with col_d2:
                    st.write(f"**👤 ผู้รายงาน:** {r.get('reporter')} ({r.get('position')})")
                    st.write(f"**🏢 หน่วยงาน:** {r.get('dept')} | **📞 โทร:** {r.get('phone')}")
                    st.write(f"**⏱️ สร้างเมื่อ:** {r.get('createdAt')}")
                    
                    st.markdown("---")
                    # ฟังก์ชันการอัปเดตสถานะและการลบ (แทนที่ PUT และ DELETE API)
                    new_status = st.selectbox(f"เปลี่ยนสถานะงาน ({r.get('id')})", options=list(STATUS_MAP.keys()), index=list(STATUS_MAP.keys()).index(r.get('status', 'pending')), key=f"status_{r.get('id')}")
                    
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button("🔄 อัปเดตสถานะ", key=f"update_{r.get('id')}"):
                        records[idx]['status'] = new_status
                        records[idx]['updatedAt'] = datetime.now().isoformat()
                        save_records(records)
                        st.success("อัปเดตสถานะเรียบร้อยแล้ว!")
                        st.rerun()
                        
                    if col_b2.button("🗑️ ลบรายงานนี้", key=f"delete_{r.get('id')}"):
                        records.pop(idx)
                        save_records(records)
                        st.warning("ลบรายการเรียบร้อยแล้ว!")
                        st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลรายงานรางชำรุดในระบบ ณ ขณะนี้")
