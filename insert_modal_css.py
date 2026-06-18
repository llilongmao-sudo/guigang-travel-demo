"""
向 index.html 的 </style> 前插入 modal CSS
"""
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

css = """
        /* ── AI规划弹窗 ── */
        .modal-overlay {
            position: fixed; top:0; left:0; width:100%; height:100%;
            background: rgba(0,0,0,0.55);
            z-index: 1000;
            display: flex; align-items: center; justify-content: center;
            padding: 16px;
        }
        .modal-card {
            background: #fff; border-radius: 18px;
            width: 100%; max-width: 520px;
            max-height: 85vh;
            display: flex; flex-direction: column;
            box-shadow: 0 12px 40px rgba(0,0,0,0.18);
            animation: modalIn 0.25s ease;
        }
        @keyframes modalIn {
            from { opacity:0; transform: translateY(30px) scale(0.96); }
            to { opacity:1; transform: translateY(0) scale(1); }
        }
        .modal-header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid #eee;
        }
        .modal-header h3 { font-size: 17px; font-weight: 700; margin: 0; }
        .modal-close {
            width: 32px; height: 32px;
            border: none; background: #f5f5f5;
            border-radius: 50%; font-size: 16px;
            cursor: pointer; display: flex;
            align-items: center; justify-content: center;
            transition: background 0.2s;
        }
        .modal-close:hover { background: #e0e0e0; }
        .modal-body {
            padding: 16px 20px;
            overflow-y: auto; flex: 1;
        }
        .modal-footer {
            display: flex; gap: 10px;
            padding: 14px 20px;
            border-top: 1px solid #eee;
        }
        .form-group { margin-bottom: 18px; }
        .form-group > label { display: block; font-size: 13px; font-weight: 600; color: #444; margin-bottom: 8px; }
        .option-row { display: flex; gap: 8px; flex-wrap: wrap; }
        .option-btn {
            padding: 7px 14px; border-radius: 10px;
            border: 1.5px solid #ddd; background: #fff;
            font-size: 13px; cursor: pointer;
            transition: all 0.2s; font-family: inherit;
        }
        .option-btn:hover { border-color: #10b981; color: #10b981; }
        .option-btn.active { background: #10b981; border-color: #10b981; color: #fff; }
        .stepper-row { display: flex; align-items: center; gap: 14px; }
        .stepper-btn {
            width: 34px; height: 34px;
            border: 1.5px solid #ddd; background: #fff;
            border-radius: 10px; font-size: 18px;
            cursor: pointer; display: flex;
            align-items: center; justify-content: center;
            transition: all 0.2s; font-family: inherit;
        }
        .stepper-btn:hover { border-color: #10b981; color: #10b981; }
        .stepper-value { font-size: 18px; font-weight: 700; min-width: 24px; text-align: center; }
        .checkbox-row { display: flex; gap: 10px; flex-wrap: wrap; }
        .checkbox-item {
            display: flex; align-items: center; gap: 5px;
            font-size: 13px; color: #555; cursor: pointer;
        }
        .checkbox-item input[type="checkbox"] { accent-color: #10b981; }
        .btn-cancel {
            flex: 1; padding: 10px; border-radius: 12px;
            border: 1.5px solid #ddd; background: #fff;
            font-size: 14px; cursor: pointer;
            transition: all 0.2s; font-family: inherit;
        }
        .btn-cancel:hover { border-color: #999; }
        .btn-primary {
            flex: 2; padding: 10px; border-radius: 12px;
            border: none; background: linear-gradient(135deg, #10b981, #059669);
            color: #fff; font-size: 14px; font-weight: 600;
            cursor: pointer; transition: all 0.2s; font-family: inherit;
            box-shadow: 0 3px 12px rgba(16,185,129,0.25);
        }
        .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 5px 16px rgba(16,185,129,0.35); }
        .btn-primary:active { transform: translateY(0); }
        .itinerary-result-modal { max-width: 640px; }
        .timeline { position: relative; padding-left: 24px; }
        .timeline::before {
            content: ''; position: absolute;
            left: 8px; top: 0; bottom: 0;
            width: 2px; background: #e0e0e0;
        }
        .timeline-item {
            position: relative; margin-bottom: 20px;
            padding-left: 16px;
        }
        .timeline-item::before {
            content: ''; position: absolute;
            left: -20px; top: 6px;
            width: 12px; height: 12px;
            border-radius: 50%; background: #10b981;
            border: 2px solid #fff; box-shadow: 0 0 0 2px #10b981;
        }
        .timeline-time { font-size: 12px; color: #10b981; font-weight: 600; margin-bottom: 4px; }
        .timeline-title { font-size: 14px; font-weight: 600; color: #222; margin-bottom: 2px; }
        .timeline-desc { font-size: 12px; color: #666; line-height: 1.5; }
        .timeline-cost { font-size: 12px; color: #e65100; margin-top: 4px; }
        .budget-card {
            background: #f8fffe; border: 1px solid #c8e6c9;
            border-radius: 12px; padding: 14px 16px;
            margin-top: 14px;
        }
        .budget-row { display: flex; justify-content: space-between; font-size: 13px; color: #555; margin-bottom: 6px; }
        .budget-total { display: flex; justify-content: space-between; font-size: 15px; font-weight: 700; color: #222; margin-top: 8px; padding-top: 8px; border-top: 1px dashed #c8e6c9; }
"""

# Insert CSS before </style>
content = content.replace('    </style>', css + '    </style>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Modal CSS inserted successfully')
print(f'Total length: {len(content)} chars')
