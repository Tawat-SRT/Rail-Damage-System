"""
Rail Damage Reporting System - Flask Application
ระบบรายงานรางชำรุดหักแตกร้าว
"""

from flask import Flask, request, jsonify # เพิ่มกลับเข้ามา
from datetime import datetime
import json
import os
from pathlib import Path
import random

# กำหนดตัวแปร app ให้ Flask รู้จัก
app = Flask(__name__)
app.config['JSON_THAI_ENABLED'] = True

# Database file
DATA_FILE = 'data/rail_damage_records.json'
Path('data').mkdir(exist_ok=True)


def load_records():
    """Load all records from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_records(records):
    """Save records to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def generate_id():
    """Generate unique report ID"""
    records = load_records()
    year = datetime.now().year
    num = len(records) + 1
    suffix = ''.join([chr(random.randint(65, 90)) for _ in range(3)])
    return f'RPT-{year}-{num:04d}-{suffix}'


DEPARTMENTS = [
    "ศูนย์อาคารและสถานที่",
    "กองบำรุงอาคารสถานที่เขตกรุงเทพ",
    "พสถ.กรุงเทพ",
    "พสถ.เชียงใหม่",
    "พสถ.ขอนแก่น",
    "พสถ.นครราชสีมา",
    "พสถ.อุดรธานี",
    "พสถ.นครสวรรค์",
    "พสถ.สมุทรปราการ",
    "พสถ.ชลบุรี"
]

SEVERITY_MAP = {
    'low': 'ต่ำ',
    'med': 'ปานกลาง',
    'high': 'สูง'
}

STATUS_MAP = {
    'pending': 'รอดำเนินการ',
    'inprog': 'กำลังซ่อมแซม',
    'done': 'ซ่อมแซมแล้ว'
}

@app.route('/api/records', methods=['GET'])
def get_records():
    """Get all records"""
    records = load_records()
    return jsonify(records)


@app.route('/api/records', methods=['POST'])
def create_record():
    """Create new damage report"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'line', 'type', 'severity']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new record
        record = {
            'id': generate_id(),
            'date': data.get('date'),
            'time': data.get('time', ''),
            'line': data.get('line'),
            'station': data.get('station', ''),
            'km': data.get('km'),
            'railId': data.get('railId', ''),
            'lat': data.get('lat'),
            'lng': data.get('lng'),
            'type': data.get('type'),
            'length': data.get('length'),
            'severity': data.get('severity'),
            'detail': data.get('detail', ''),
            'action': data.get('action', ''),
            'images': data.get('images', []),
            'reporter': data.get('reporter', ''),
            'position': data.get('position', ''),
            'dept': data.get('dept', ''),
            'phone': data.get('phone', ''),
            'status': data.get('status', 'pending'),
            'dueDate': data.get('dueDate', ''),
            'note': data.get('note', ''),
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        records = load_records()
        records.append(record)
        save_records(records)
        
        return jsonify({'success': True, 'id': record['id']}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>', methods=['GET'])
def get_record(record_id):
    """Get specific record"""
    records = load_records()
    for record in records:
        if record['id'] == record_id:
            return jsonify(record)
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/records/<record_id>', methods=['PUT'])
def update_record(record_id):
    """Update damage report"""
    try:
        data = request.get_json()
        records = load_records()
        
        for i, record in enumerate(records):
            if record['id'] == record_id:
                # Update fields
                for key, value in data.items():
                    if key != 'id' and key != 'createdAt':
                        record[key] = value
                record['updatedAt'] = datetime.now().isoformat()
                save_records(records)
                return jsonify({'success': True})
        
        return jsonify({'error': 'Not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete damage report"""
    try:
        records = load_records()
        records = [r for r in records if r['id'] != record_id]
        save_records(records)
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get statistics for dashboard"""
    records = load_records()
    
    stats = {
        'total': len(records),
        'high': len([r for r in records if r.get('severity') == 'high']),
        'pending': len([r for r in records if r.get('status') == 'pending']),
        'resolved': len([r for r in records if r.get('status') == 'done']),
        'severityBreakdown': {},
        'statusBreakdown': {},
        'typeBreakdown': {},
        'lineBreakdown': {},
        'hotAreas': {}
    }
    
    # Severity breakdown
    for sev in ['low', 'med', 'high']:
        count = len([r for r in records if r.get('severity') == sev])
        stats['severityBreakdown'][SEVERITY_MAP.get(sev, sev)] = count
    
    # Status breakdown
    for status in ['pending', 'inprog', 'done']:
        count = len([r for r in records if r.get('status') == status])
        stats['statusBreakdown'][STATUS_MAP.get(status, status)] = count
    
    # Type breakdown
    for record in records:
        dtype = record.get('type', 'Unknown')
        stats['typeBreakdown'][dtype] = stats['typeBreakdown'].get(dtype, 0) + 1
    
    # Line breakdown
    for record in records:
        line = record.get('line', 'Unknown')
        stats['lineBreakdown'][line] = stats['lineBreakdown'].get(line, 0) + 1
    
    # Hot areas (locations with most reports)
    for record in records:
        key = f"{record.get('line', '')} - {record.get('station', '')}"
        stats['hotAreas'][key] = stats['hotAreas'].get(key, 0) + 1
    
    return jsonify(stats)


@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export records as CSV"""
    import csv
    from io import StringIO
    
    records = load_records()
    
    output = StringIO()
    writer = csv.writer(output, lineterminator='\n')
    
    # Header
    headers = ['รหัส', 'วันที่', 'เวลา', 'สาย', 'สถานี', 'ประเภท', 'ความรุนแรง', 'สถานะ', 'ผู้รายงาน']
    writer.writerow(headers)
    
    # Data
    for record in records:
        writer.writerow([
            record.get('id'),
            record.get('date'),
            record.get('time'),
            record.get('line'),
            record.get('station'),
            record.get('type'),
            SEVERITY_MAP.get(record.get('severity'), ''),
            STATUS_MAP.get(record.get('status'), ''),
            record.get('reporter')
        ])
    
    return output.getvalue(), 200, {
        'Content-Disposition': 'attachment; filename=rail_damage_report.csv',
        'Content-type': 'text/csv; charset=utf-8'
    }


@app.route('/api/departments', methods=['GET'])
def get_departments():
    """Get list of departments"""
    return jsonify(DEPARTMENTS)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Server error'}), 500

# เพิ่มคำสั่งรันเซิร์ฟเวอร์
if __name__ == '__main__':
    app.run(debug=True, port=5000)
