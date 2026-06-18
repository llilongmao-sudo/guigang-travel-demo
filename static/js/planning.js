// ============================================================
//  V8 AI 旅行规划 – 前端逻辑
// ============================================================

// ── 全局状态 ────────────────────────────────────────────────
let planningFormData = {
    days: 2,
    budget: 1000,
    people: 2,
    transport: 'self-drive',
    accommodation: 'standard',
    preferences: ['nature']
};

// ── 打开 / 关闭 规划表单弹窗 ───────────────────────────────
function openPlanningModal() {
    // 重置表单为默认值
    resetPlanningForm();
    document.getElementById('planningModal').style.display = 'flex';
}

function closePlanningModal() {
    document.getElementById('planningModal').style.display = 'none';
}

// ── 重置表单 ────────────────────────────────────────────────
function resetPlanningForm() {
    planningFormData = {
        days: 2,
        budget: 1000,
        people: 2,
        transport: 'self-drive',
        accommodation: 'standard',
        preferences: ['nature']
    };
    // 重置 UI
    setOptionActive('daysOptions', '2');
    setOptionActive('budgetOptions', '1000');
    setOptionActive('transportOptions', 'self-drive');
    setOptionActive('accommodationOptions', 'standard');
    document.getElementById('peopleValue').textContent = '2';
    // 重置复选框
    const checkboxes = document.querySelectorAll('#preferencesCheckboxes input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = (cb.value === 'nature');
    });
}

// ── 选项按钮点击 ────────────────────────────────────────────
function selectOption(btn, group) {
    // 移除同组所有 active
    btn.parentElement.querySelectorAll('.option-btn').forEach(b => b.classList.remove('active'));
    // 激活当前按钮
    btn.classList.add('active');
    // 更新数据
    const value = btn.getAttribute('data-value');
    switch(group) {
        case 'days':          planningFormData.days = parseInt(value); break;
        case 'budget':        planningFormData.budget = parseInt(value); break;
        case 'transport':      planningFormData.transport = value; break;
        case 'accommodation': planningFormData.accommodation = value; break;
    }
}

function setOptionActive(parentId, value) {
    const parent = document.getElementById(parentId);
    if (!parent) return;
    parent.querySelectorAll('.option-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-value') === value);
    });
}

// ── 步进器（+ / -）────────────────────────────────────────
function updateStepper(field, delta) {
    const valEl = document.getElementById('peopleValue');
    let val = parseInt(valEl.textContent) || 2;
    val = Math.max(1, Math.min(20, val + delta));
    valEl.textContent = val;
    planningFormData.people = val;
}

// ── 生成行程 ────────────────────────────────────────────────
async function generateItinerary() {
    // 收集偏好（复选框）
    const checked = document.querySelectorAll('#preferencesCheckboxes input[type="checkbox"]:checked');
    planningFormData.preferences = Array.from(checked).map(cb => cb.value);

    // 显示加载状态
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ 生成中...';

    try {
        const resp = await fetch('/api/plan-itinerary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(planningFormData)
        });
        const data = await resp.json();

        if (data.error) {
            showToast('❌ ' + data.error);
            return;
        }

        // 渲染结果
        renderItineraryResult(data);
        closePlanningModal();
        document.getElementById('itineraryResultModal').style.display = 'flex';

    } catch (e) {
        showToast('❌ 网络错误，请重试');
        console.error(e);
    } finally {
        btn.disabled = false;
        btn.textContent = '🎲 生成行程';
    }
}

// ── 渲染行程结果（时间轴）────────────────────────────────
function renderItineraryResult(data) {
    const container = document.getElementById('itineraryResultBody');
    if (!container) return;

    let html = '';

    // 逐天渲染
    (data.itinerary || []).forEach((day, idx) => {
        html += `<div style="margin-bottom:20px;">
            <div style="font-size:16px;font-weight:700;color:#10b981;margin-bottom:12px;">📅 第 ${day.day} 天</div>
            <div class="timeline">`;

        (day.activities || []).forEach(act => {
            html += `<div class="timeline-item">
                <div class="timeline-time">${act.time || ''}</div>
                <div class="timeline-title">${act.title || ''}</div>
                <div class="timeline-desc">${act.description || ''}</div>
                ${act.cost ? `<div class="timeline-cost">💰 ${act.cost}</div>` : ''}
            </div>`;
        });

        html += `</div></div>`;
    });

    // 预算卡片
    if (data.budget_breakdown) {
        const b = data.budget_breakdown;
        html += `<div class="budget-card">
            <div style="font-size:14px;font-weight:700;margin-bottom:10px;color:#333;">💰 预算估算（${planningFormData.people}人）</div>
            <div class="budget-row"><span>门票</span><span>¥${b.tickets || 0}</span></div>
            <div class="budget-row"><span>餐饮</span><span>¥${b.dining || 0}</span></div>
            <div class="budget-row"><span>交通</span><span>¥${b.transport || 0}</span></div>
            ${b.accommodation ? `<div class="budget-row"><span>住宿</span><span>¥${b.accommodation}</span></div>` : ''}
            <div class="budget-total"><span>总计（预估）</span><span>¥${b.total || 0}</span></div>
        </div>`;
    }

    // 提示
    if (data.tips && data.tips.length > 0) {
        html += `<div style="margin-top:14px;padding:12px 14px;background:#e8f5e9;border-radius:10px;font-size:12px;color:#2e7d32;line-height:1.6;">`;
        html += `<div style="font-weight:600;margin-bottom:6px;">💡 温馨提示</div>`;
        data.tips.forEach(tip => {
            html += `<div>• ${tip}</div>`;
        });
        html += `</div>`;
    }

    container.innerHTML = html;
}

// ── 关闭结果弹窗 ──────────────────────────────────────────
function closeItineraryResultModal() {
    document.getElementById('itineraryResultModal').style.display = 'none';
}

// ── 保存行程到 LocalStorage ────────────────────────────────
function saveItinerary() {
    const resultBody = document.getElementById('itineraryResultBody');
    if (!resultBody) return;

    const itineraries = JSON.parse(localStorage.getItem('guigang_itineraries') || '[]');
    const record = {
        id: 'itin_' + Date.now(),
        created_at: new Date().toISOString(),
        form_data: { ...planningFormData },
        result_html: resultBody.innerHTML
    };
    itineraries.unshift(record);
    // 最多保存 20 条
    if (itineraries.length > 20) itineraries.pop();
    localStorage.setItem('guigang_itineraries', JSON.stringify(itineraries));
    showToast('✅ 行程已保存！可前往"我的行程"查看');
    closeItineraryResultModal();
}

// ── Helper: showToast（如果页面已有则不再重复定义）─────────
if (typeof showToast !== 'function') {
    function showToast(msg) {
        let toast = document.getElementById('toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast';
            toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.75);color:#fff;padding:8px 18px;border-radius:20px;font-size:13px;z-index:99999;transition:opacity 0.3s;pointer-events:none;';
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.style.opacity = '1';
        clearTimeout(toast._timer);
        toast._timer = setTimeout(() => { toast.style.opacity = '0'; }, 2500);
    }
}
