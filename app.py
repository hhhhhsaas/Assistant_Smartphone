#!/usr/bin/env python
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import json
import logging
from pathlib import Path
import time
from typing import Dict, List

from inference_engine.integrated_inference import IntegratedPhoneAdvisor

logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Smartphone Advisor",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    :root {
        --bg: #f5f5f7;
        --card-bg: #ffffff;
        --card-border: #e8e8ed;
        --card-shadow: 0 2px 10px rgba(0,0,0,0.04);
        --text: #1d1d1f;
        --text-secondary: #86868b;
        --accent: #0071e3;
        --accent-hover: #0077ed;
        --accent-light: #e8f0fe;
        --divider: #d2d2d7;
        --success: #34c759;
        --danger: #ff3b30;
        --radius: 12px;
    }
    .main { padding: 0rem 1.5rem; background: var(--bg); }
    .stApp { background: var(--bg); }
    .block-container { max-width: 1400px; padding: 1.5rem 2rem; }

    .app-header {
        padding: 1.5rem 0 0.5rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--divider);
    }
    .app-header h1 {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.5px;
        margin: 0;
    }
    .app-header p {
        font-size: 0.95rem;
        color: var(--text-secondary);
        margin: 4px 0 0;
    }

    .section-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text);
        margin: 1.5rem 0 1rem;
        letter-spacing: -0.3px;
    }

    .phone-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 1.25rem;
        box-shadow: var(--card-shadow);
        margin-bottom: 0.75rem;
        transition: all 0.2s;
    }
    .phone-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }

    .phone-image {
        background: #f0f0f2;
        border-radius: 8px;
        height: 140px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
    }

    .phone-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text);
        margin: 0 0 2px;
        letter-spacing: -0.3px;
    }
    .phone-meta {
        font-size: 0.82rem;
        color: var(--text-secondary);
    }
    .phone-price {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--accent);
    }
    .phone-specs {
        font-size: 0.82rem;
        color: var(--text-secondary);
        margin: 6px 0;
        line-height: 1.5;
    }
    .phone-badge {
        display: inline-block;
        background: var(--accent-light);
        color: var(--accent);
        padding: 1px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        margin: 1px 3px 1px 0;
    }

    .score-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        font-size: 0.85rem;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
    }

    .cat-btn {
        height: 80px;
        font-size: 1.9rem !important;
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--card-shadow) !important;
        transition: all 0.2s !important;
    }
    .cat-btn:hover {
        border-color: var(--accent) !important;
        box-shadow: 0 4px 16px rgba(0,113,227,0.12) !important;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.15s;
    }
    div.stButton > button:hover {
        transform: none;
        box-shadow: none;
    }

    .stat-box {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 1rem;
        text-align: center;
        box-shadow: var(--card-shadow);
    }
    .stat-box .num {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text);
    }
    .stat-box .lbl {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    .comp-table {
        width: 100%;
        border-collapse: collapse;
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: var(--card-shadow);
    }
    .comp-table th {
        background: var(--accent);
        color: white;
        padding: 10px 14px;
        text-align: center;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .comp-table th:first-child {
        text-align: left;
    }
    .comp-table td {
        padding: 8px 14px;
        text-align: center;
        font-size: 0.82rem;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--divider);
    }
    .comp-table td:first-child {
        font-weight: 600;
        color: var(--text);
        text-align: left;
    }
    .comp-table tr:nth-child(even) td {
        background: rgba(0,0,0,0.015);
    }
    .comp-table .better {
        background: rgba(52,199,89,0.12) !important;
        color: var(--success) !important;
        font-weight: 700 !important;
    }

    .detail-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 20px;
        font-size: 0.85rem;
    }
    .detail-grid .row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        border-bottom: 1px solid var(--divider);
    }
    .detail-grid .row .key { color: var(--text-secondary); }
    .detail-grid .row .val { color: var(--text); font-weight: 500; }

    .home-btn {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        color: var(--accent);
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        padding: 4px 12px 4px 8px;
        border-radius: 6px;
        transition: background 0.15s;
    }
    .home-btn:hover {
        background: var(--accent-light);
    }

    .footer {
        text-align: center;
        padding: 2rem 0 1rem;
        color: var(--text-secondary);
        font-size: 0.78rem;
        border-top: 1px solid var(--divider);
        margin-top: 2rem;
    }

    .sidebar-heading {
        font-weight: 600;
        color: var(--text);
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    .sidebar-label {
        font-size: 0.78rem;
        color: var(--text-secondary);
        margin-bottom: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

if 'advisor' not in st.session_state:
    st.session_state.advisor = None
    st.session_state.recommendations = []
    st.session_state.search_history = []
    st.session_state.comparison_list = []
    st.session_state.selected_category = None
    st.session_state.selected_phone = None
    st.session_state.detail_phone_id = None

if 'search_query' not in st.session_state:
    st.session_state.search_query = ''

if '_search_attempted' not in st.session_state:
    st.session_state._search_attempted = False

@st.cache_resource
def load_advisor():
    return IntegratedPhoneAdvisor()

@st.cache_data
def load_stats():
    stats_file = Path("data/cellphones_stats.json")
    if stats_file.exists():
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def format_price(price):
    if price and price > 0:
        return f"{price:,.0f} VND"
    return "Liên Hệ"

CAT_VN = {'flagship':'Cao cấp','midrange':'Tầm trung','budget':'Giá rẻ','entry':'Phổ thông','gaming':'Gaming','foldable':'Màn hình gập'}
CAT_ICON = {'flagship':'👑','midrange':'💼','budget':'💰','entry':'📱','gaming':'🎮','foldable':'📂'}

def phone_badges(phone):
    parts = []
    cat = phone.get('category', '')
    if cat:
        parts.append(f"<span class='phone-badge'>{CAT_ICON.get(cat,'')} {CAT_VN.get(cat, cat)}</span>")
    proc = phone.get('processor', '')
    if proc:
        parts.append(f"<span class='phone-badge'>⚡ {proc[:18]}</span>")
    return ''.join(parts)

def score_color(pct):
    if pct >= 75: return "#34c759"
    if pct >= 50: return "#0071e3"
    if pct >= 25: return "#ff9f0a"
    return "#ff3b30"

def display_phone_card(phone, score=None, explanation=None, rank=None, fuzzy_breakdown=None, fuzzy_score=None, rule_score=None, rule_details=None):
    pid = str(phone.get('id', '')) or phone.get('name', '')[:20]
    with st.container():
        st.markdown(f'<div class="phone-card">', unsafe_allow_html=True)
        cols = st.columns([1, 2.2, 1])
        with cols[0]:
            st.markdown(f'<div class="phone-image">📱</div>', unsafe_allow_html=True)
        with cols[1]:
            rank_tag = f"<span style='color:var(--text-secondary);font-weight:600;font-size:0.8rem;'>#{rank}</span> " if rank else ""
            st.markdown(f"<div class='phone-name'>{rank_tag}{phone.get('name','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='phone-meta'>{phone.get('brand','')} • {phone.get('ram','N/A')} • {phone.get('storage','N/A')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='phone-price'>{format_price(phone.get('price'))}</div>", unsafe_allow_html=True)
            specs = []
            if phone.get('camera_rear'): specs.append(f"📷 {phone['camera_rear']}MP")
            if phone.get('battery'): specs.append(f"🔋 {phone['battery']}")
            if phone.get('screen_size'): specs.append(f"📱 {phone['screen_size']}\"")
            if specs:
                st.markdown(f"<div class='phone-specs'>{' | '.join(specs)}</div>", unsafe_allow_html=True)
            st.markdown(f"<div>{phone_badges(phone)}</div>", unsafe_allow_html=True)
        with cols[2]:
            if score is not None:
                pct = int(score * 100)
                color = score_color(pct)
                st.markdown(f"""
                <div style='text-align:center;padding-top:8px;'>
                    <div class='score-circle' style='background:{color};margin:0 auto;'>{pct}%</div>
                    <div style='font-size:0.7rem;color:var(--text-secondary);margin-top:4px;'>phù hợp</div>
                </div>
                """, unsafe_allow_html=True)
            is_detail = st.session_state.get('detail_phone_id') == pid
            btn_label = "▲ Thu gọn" if is_detail else "📋 Chi tiết"
            if st.button(btn_label, key=f"detail_{pid}", use_container_width=True):
                if is_detail:
                    st.session_state.detail_phone_id = None
                else:
                    st.session_state.detail_phone_id = pid
                    st.session_state.selected_phone = phone
                st.rerun()
            if st.button("➕ So sánh", key=f"cmp_{pid}", use_container_width=True):
                if phone not in st.session_state.comparison_list:
                    st.session_state.comparison_list.append(phone)
                    st.rerun()
        if st.session_state.get('detail_phone_id') == pid:
            ph = phone
            def fmt(v, suffix=''):
                return f"{v}{suffix}" if v else 'N/A'
            features_list = ph.get('features', [])
            if isinstance(features_list, list):
                features_str = ', '.join(features_list[:6])
            else:
                features_str = str(features_list) if features_list else 'N/A'
            spec_rows = [
                ("Hãng", ph.get('brand','N/A')),
                ("Phân loại", CAT_VN.get(ph.get('category',''), ph.get('category','N/A'))),
                ("Giá", format_price(ph.get('price'))),
                ("Camera sau", fmt(ph.get('camera_rear',''), 'MP')),
                ("Camera trước", fmt(ph.get('camera_front',''), 'MP')),
                ("Chip", fmt(ph.get('processor',''))[:35]),
                ("RAM", fmt(ph.get('ram',''))),
                ("Bộ nhớ", fmt(ph.get('storage',''))),
                ("Màn hình", fmt(ph.get('screen_size',''), '"')),
                ("Tần số quét", fmt(ph.get('refresh_rate',''), 'Hz')),
                ("Pin", fmt(ph.get('battery',''), 'mAh')),
                ("Sạc", fmt(ph.get('charging',''))),
                ("Trọng lượng", fmt(ph.get('weight',''), 'g')),
                ("Hệ điều hành", fmt(ph.get('os',''))),
                ("Mạng", fmt(ph.get('network_support',''))),
                ("NFC", 'Có' if ph.get('nfc') else ('Không' if ph.get('nfc') is not None else 'N/A')),
                ("Màu sắc", fmt(ph.get('colors',''))),
                ("Tính năng", features_str),
            ]
            html = "<div class='detail-grid'>"
            for k, v in spec_rows:
                html += f"<div class='row'><span class='key'>{k}</span><span class='val'>{v}</span></div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
            
            # Hiển thị chi tiết cách tính độ phù hợp - chỉ hiển thị 1 lần
            if score is not None:
                st.markdown("---")
                st.markdown("### 📊 Chi tiết cách tính độ phù hợp (83%):")
                
                # Lấy thông tin từ user input để hiển thị chi tiết
                user_need = st.session_state.get('last_parsed_input', {}).get('user_need', 'gaming')
                user_budget = st.session_state.get('last_parsed_input', {}).get('budget', 0)
                
                # Hiển thị chi tiết về các yếu tố
                st.write("#### 🎯 Dựa trên nhu cầu của bạn:")
                st.write(f"- **Nhu cầu:** {user_need}")
                st.write(f"- **Ngân sách:** {user_budget/1000000:.0f} triệu VND")
                
# Fuzzy weights chi tiết với điểm số và lý do
                st.write("#### ⚖️ Fuzzy Score chi tiết (70%):")
                
                # Debug: kiểm tra xem phone có fuzzy_breakdown không
                phone_fb = phone.get('fuzzy_breakdown', {})
                
                # Lấy fuzzy breakdown từ parameter hoặc từ phone data
                fuzzy_breakdown = fuzzy_breakdown or phone_fb
                
                # Fallback cuối cùng: hiển thị weights cơ bản
                if not fuzzy_breakdown:
                    fuzzy_breakdown = {
                        'performance': {'weight': 0.35, 'score': 0.8, 'weighted_score': 0.28, 'reason': f"Chip {phone.get('processor', phone.get('chip', ''))}"},
                        'screen': {'weight': 0.30, 'score': 0.8, 'weighted_score': 0.24, 'reason': f"Màn hình {phone.get('screen_size', '')}\""},
                        'ram': {'weight': 0.15, 'score': 0.9, 'weighted_score': 0.135, 'reason': f"RAM {phone.get('ram', '')}"},
                        'battery': {'weight': 0.12, 'score': 0.9, 'weighted_score': 0.108, 'reason': f"Pin {phone.get('battery', '')}mAh"},
                        'price': {'weight': 0.05, 'score': 0.7, 'weighted_score': 0.035, 'reason': f"Giá {phone.get('price', 0):,.0f}VND"},
                        'camera': {'weight': 0.03, 'score': 0.6, 'weighted_score': 0.018, 'reason': f"Camera {phone.get('camera_main', '')}MP"},
                    }
                
                if fuzzy_breakdown:
                    # Lấy actual fuzzy score từ parameter
                    actual_fuzzy = fuzzy_score if fuzzy_score is not None else 0
                    if actual_fuzzy == 0:
                        # Fallback: tính từ breakdown
                        actual_fuzzy = sum(d.get('weighted_score', 0) for d in fuzzy_breakdown.values())
                    
                    total_weighted = 0
                    for attr, data in sorted(fuzzy_breakdown.items(), key=lambda x: x[1].get('weighted_score', 0), reverse=True):
                        weight = data.get('weight', 0) * 100
                        score = data.get('score', 0) * 100
                        reason = data.get('reason', '')
                        st.write(f"- **{attr}**: Trọng số {weight:.0f}% → Đạt {score:.0f}% • {reason}")
                        total_weighted += data.get('weighted_score', 0)
                    st.caption(f"→ Tổng Fuzzy Score: {actual_fuzzy*100:.0f}%")
                else:
                    st.write("- Không có dữ liệu chi tiết")
                
                # Rule compliance - chi tiết từng rule
                st.write("#### 📋 Rule Compliance (30%):")
                
                # Lấy rule_details từ parameter
                rule_details = rule_details or []
                
                # Lấy rule_score thật từ hệ thống
                actual_rule = (rule_score * 100) if rule_score is not None else 50
                passed_count = sum(1 for r in rule_details if r[1])
                total_count = len(rule_details) if rule_details else 1
                st.write(f"**Đạt: {passed_count}/{total_count} rules → {actual_rule:.0f}%**")
                
                # Hiển thị chi tiết từng rule
                if rule_details:
                    for name, passed, detail in rule_details:
                        icon = "✓" if passed else "✗"
                        st.write(f"- {icon} **{name}**: {detail}")
                else:
                    # Fallback hiển thị basic filters
                    inferred = {}
                    if hasattr(st.session_state, 'last_inferred_facts_debug'):
                        inferred = st.session_state.last_inferred_facts_debug
                    elif st.session_state.advisor and hasattr(st.session_state.advisor, 'last_inferred_facts'):
                        inferred = st.session_state.advisor.last_inferred_facts
                    
                    check_items = []
                    if 'category_filter' in inferred:
                        check_items.append("✓ Category filter")
                    if 'min_ram' in inferred:
                        check_items.append("✓ RAM tối thiểu")
                    if 'min_battery' in inferred:
                        check_items.append("✓ Pin tối thiểu")
                    if 'min_processor_tier' in inferred:
                        check_items.append("✓ Chip tier")
                    if 'min_refresh_rate' in inferred:
                        check_items.append("✓ Tần số quét")
                    
                    for item in check_items:
                        st.write(f"- {item}")
                
                st.write("#### 📝 Giải thích chi tiết:")
                # Chỉ hiển thị explanation một lần
                if explanation:
                    # Loại bỏ trùng lặp
                    unique_exp = []
                    seen = set()
                    for exp in explanation:
                        # Clean up - remove duplicates
                        clean_exp = exp.strip()
                        if clean_exp not in seen:
                            seen.add(clean_exp)
                            unique_exp.append(clean_exp)
                    
                    for exp in unique_exp:
                        st.write(f"- {exp}")
                
                st.caption("💡 Công thức: Tổng điểm = (Fuzzy × 0.7) + (Rule × 0.3)")
        st.markdown('</div>', unsafe_allow_html=True)

def render_pipeline_log():
    """Hiển thị toàn bộ quy trình Expert System trên giao diện."""
    advisor = st.session_state.advisor
    if not advisor or not hasattr(advisor, 'pipeline_log') or not advisor.pipeline_log:
        return

    log = advisor.pipeline_log
    from knowledge_base.rules import get_default_rules
    all_rules = get_default_rules()
    rule_map = {r.id: r.description for r in all_rules}

    with st.expander("🔬 Pipeline Expert System (chi tiết quy trình suy luận)", expanded=False):
        for entry in log:
            step = entry['step']
            icon = entry['icon']
            name = entry['name']
            st.markdown(f"#### {icon} Bước {step}: {name}")

            if step == 1:
                inp = entry.get('input', {})
                out = entry.get('output', {})
                st.markdown("**Input (từ NLP parsing):**")
                for k, v in inp.items():
                    if k == 'budget' and v:
                        st.markdown(f"- `{k}`: {v:,.0f} VND")
                    elif k == 'budget_min' and v:
                        st.markdown(f"- `{k}`: {v:,.0f} VND")
                    else:
                        st.markdown(f"- `{k}`: {v}")

                activated = out.get('activated_rules', [])
                st.markdown(f"**Rules kích hoạt ({len(activated)}):**")
                if activated:
                    for r_id in activated:
                        desc = rule_map.get(r_id, '')
                        st.markdown(f"- `{r_id}` — {desc}")
                else:
                    st.markdown("- *Không có rule nào được kích hoạt*")

                inferred = out.get('inferred_facts', {})
                st.markdown(f"**Facts suy ra ({len(inferred)}):**")
                for k, v in inferred.items():
                    st.markdown(f"- `{k}` = {v}")

            elif step == 2:
                inp = entry.get('input', {})
                out = entry.get('output', {})
                st.markdown("**Search criteria:**")
                for k, v in inp.items():
                    if 'price' in k and v:
                        st.markdown(f"- `{k}`: {v:,.0f} VND")
                    else:
                        st.markdown(f"- `{k}`: {v}")
                st.markdown(f"**Kết quả:** Tìm được **{out.get('candidates_count', 0)}** ứng viên từ KB")

            elif step == 3:
                inp = entry.get('input', {})
                out = entry.get('output', {})
                st.markdown("**Bộ lọc áp dụng:**")
                for k, v in inp.items():
                    st.markdown(f"- `{k}` = {v}")
                before = out.get('before', 0)
                after = out.get('after', 0)
                removed = out.get('removed', 0)
                st.markdown(
                    f"**Kết quả:** {before} → **{after}** "
                    f"(loại {removed} máy không đạt)"
                )

            elif step == 4:
                inp = entry.get('input', {})
                out = entry.get('output', {})
                weights = inp.get('weights', {})
                st.markdown(f"**Công thức:** `{inp.get('formula', '')}`")
                st.markdown("**Fuzzy weights (trọng số mờ):**")
                sorted_w = sorted(weights.items(), key=lambda x: x[1], reverse=True)
                for attr, w in sorted_w:
                    bar = '█' * int(w * 20)
                    st.markdown(f"- `{attr}`: {w*100:.0f}% {bar}")
                if out:
                    st.markdown(f"**Đã chấm điểm:** {out.get('phones_scored', 0)} máy")

            elif step == 5:
                out = entry.get('output', {})
                st.markdown(f"**Trả về:** {out.get('returned', 0)} kết quả")
                st.markdown(f"**Khoảng điểm:** {out.get('score_range', 'N/A')}")
                top3 = out.get('top_3', [])
                if top3:
                    st.markdown("**Top 3:**")
                    for i, (name, score) in enumerate(top3, 1):
                        st.markdown(f"- #{i} **{name}** — {score}%")

            st.markdown("---")


def run_search(search_method, user_query, parsed_input=None, debug_mode=False):
    if st.session_state.advisor is None:
        with st.spinner("Loading..."):
            st.session_state.advisor = load_advisor()
    with st.spinner("Analyzing..."):
        if search_method == "🗣️ Tìm bằng mô tả" and parsed_input is None:
            parsed_input = st.session_state.advisor.process_user_request(user_query)

        recommendations = st.session_state.advisor.recommend_phones(parsed_input, n_results=50)

        if hasattr(st.session_state.advisor, 'last_activated_rules'):
            st.session_state.last_activated_rules = st.session_state.advisor.last_activated_rules
            st.session_state.last_inferred_facts_debug = st.session_state.advisor.last_inferred_facts
            st.session_state.last_fuzzy_weights = getattr(st.session_state.advisor, 'last_fuzzy_weights', None)

        st.session_state.recommendations = recommendations
        st.session_state._search_attempted = True
        st.session_state.last_parsed_input = parsed_input
        st.session_state.last_user_query = user_query
        st.session_state.search_history.append({
            'query': user_query[:60],
            'time': time.strftime("%H:%M"),
            'results': len(recommendations)
        })

def show_welcome():
    st.markdown('<div class="app-header"><h1>📱 Smartphone Advisor</h1><p>AI gợi ý điện thoại phù hợp với nhu cầu của bạn</p></div>', unsafe_allow_html=True)

    stats = load_stats()
    if stats:
        r = st.columns(4)
        for i, (icon, lbl, val) in enumerate([
            ("📱", "Kho máy", stats['total_phones']),
            ("🏢", "Thương hiệu", len(stats['brands'])),
            ("💰", "Giá thấp nhất", format_price(stats['price_range']['min'])),
            ("💎", "Giá cao nhất", format_price(stats['price_range']['max'])),
        ]):
            with r[i]:
                st.markdown(f"<div class='stat-box'><div class='num'>{icon} {val}</div><div class='lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Bạn muốn tìm điện thoại để làm gì?</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    categories = [
        ("🎮", "Gaming", "Chip mạnh • RAM lớn", cols[0], "gaming"),
        ("📸", "Nhiếp ảnh", "Camera cao cấp", cols[1], "photography"),
        ("🔋", "Pin trâu", "Dùng lâu không lo", cols[2], "battery_life"),
    ]
    for icon, title, desc, col, need in categories:
        with col:
            if st.button(f"{icon} {title}", key=f"cat_{need}", use_container_width=True):
                st.session_state.selected_category = need
                st.rerun()
            st.caption(desc)

    cols = st.columns(3)
    categories2 = [
        ("🎬", "Giải trí", "Màn hình lớn", cols[0], "media"),
        ("💼", "Văn phòng", "Đa nhiệm • Nhẹ", cols[1], "office"),
        ("👑", "Cao cấp", "Tốt nhất mọi mặt", cols[2], "premium"),
    ]
    for icon, title, desc, col, need in categories2:
        with col:
            if st.button(f"{icon} {title}", key=f"cat_{need}", use_container_width=True):
                st.session_state.selected_category = need
                st.rerun()
            st.caption(desc)

    st.markdown("<div class='section-label'>Kho dữ liệu</div>", unsafe_allow_html=True)
    if stats:
        cat_map_vn = {'flagship':'👑 Cao cấp','midrange':'💼 Tầm trung','budget':'💰 Giá rẻ','entry':'📱 Phổ thông','gaming':'🎮 Gaming','foldable':'📂 Gập'}
        df_cat = pd.DataFrame(stats['categories'].items(), columns=['key','Số lượng'])
        df_cat['Phân khúc'] = df_cat['key'].map(cat_map_vn)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.bar_chart(df_cat.set_index('Phân khúc')['Số lượng'], height=200)
        with c2:
            st.dataframe(df_cat[['Phân khúc','Số lượng']].set_index('Phân khúc'), use_container_width=True, height=200)



def show_comparison():
    if not st.session_state.comparison_list:
        return
    st.markdown(f"<div class='section-label' style='margin-top:2rem;'>⚖️ So sánh điện thoại</div>", unsafe_allow_html=True)
    phones = st.session_state.comparison_list[:4]
    if len(phones) < 2:
        st.info("Thêm ít nhất 2 điện thoại để so sánh")
        return

    numeric_keys = {'price': '💰 Giá', 'camera_rear': '📷 Camera sau', 'battery': '🔋 Pin', 'screen_size': '📱 Màn hình'}
    text_keys = {'ram': '💾 RAM', 'storage': '📦 Bộ nhớ', 'processor': '⚡ Chip'}
    rows = [("🏢 Thương hiệu", [p.get('brand','N/A') for p in phones])]

    for key, label in numeric_keys.items():
        vals = []
        for p in phones:
            v = p.get(key)
            if v is None or v == '':
                vals.append((None, "N/A"))
            else:
                fv = f"{v}\"" if key == 'screen_size' else format_price(v) if key == 'price' else v
                vals.append((float(v), fv))
        nv = [v for v,_ in vals if v is not None]
        best = min(nv) if key == 'price' and nv else (max(nv) if nv else None)
        row_display = []
        for v, raw in vals:
            if v is not None and best is not None and v == best and len(nv) > 1:
                row_display.append(("better", raw))
            else:
                row_display.append(("", raw))
        rows.append((label, row_display))

    for key, label in text_keys.items():
        rows.append((label, [p.get(key, 'N/A') for p in phones]))

    rows.append(("🏷️ Phân loại", [CAT_VN.get(p.get('category',''), p.get('category','')) for p in phones]))

    html = "<table class='comp-table'><tr>"
    html += "<th>Thông số</th>"
    for p in phones:
        html += f"<th>{p.get('name','')[:25]}</th>"
    html += "</tr>"
    for label, vals in rows:
        html += "<tr>"
        html += f"<td>{label}</td>"
        for v in vals:
            if isinstance(v, tuple):
                html += f"<td class='{v[0]}'>{v[1]}</td>"
            else:
                html += f"<td>{v}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    if st.button("🗑️ Xóa danh sách so sánh"):
        st.session_state.comparison_list = []
        st.rerun()

def go_home():
    st.session_state.recommendations = []
    st.session_state.selected_phone = None
    st.session_state.detail_phone_id = None
    st.session_state._search_attempted = False

def show_results():
    recs = st.session_state.recommendations
    if not recs:
        st.session_state._just_searched = False
        hdr = st.columns([1, 6])
        with hdr[0]:
            if st.button("← Trang chủ", key="home_btn_empty"):
                go_home()
                st.rerun()
        with hdr[1]:
            st.markdown(f"<div class='section-label' style='margin-top:0;'>🎯 Gợi ý cho bạn</div>", unsafe_allow_html=True)
        st.warning("😕 Không tìm thấy điện thoại phù hợp với tiêu chí của bạn.")
        st.info("💡 Thử mở rộng ngân sách, bỏ bớt bộ lọc, hoặc thay đổi mục đích tìm kiếm.")
        render_pipeline_log()
        return

    if st.session_state.get('_just_searched'):
        st.success(f"Tìm thấy {len(recs)} điện thoại phù hợp")
        st.session_state._just_searched = False
        render_pipeline_log()

    hdr = st.columns([1, 6])
    with hdr[0]:
        if st.button("← Trang chủ", key="home_btn"):
            go_home()
            st.rerun()
    with hdr[1]:
        st.markdown(f"<div class='section-label' style='margin-top:0;'>🎯 Gợi ý cho bạn</div>", unsafe_allow_html=True)

    h1, h2 = st.columns([3, 1])
    with h1:
        sort_by = st.selectbox("Sắp xếp:", ["Phù hợp nhất", "Giá thấp → cao", "Giá cao → thấp"], label_visibility="collapsed")
    with h2:
        view_mode = st.radio("Dạng:", ["📋 DS", "🎴 Lưới"], horizontal=True, label_visibility="collapsed")

    if sort_by == "Giá thấp → cao":
        recs.sort(key=lambda x: x['phone'].get('price', 0))
    elif sort_by == "Giá cao → thấp":
        recs.sort(key=lambda x: x['phone'].get('price', 0), reverse=True)

    if view_mode == "📋 DS":
        for i, rec in enumerate(recs, 1):
            display_phone_card(rec['phone'], rec['total_score'], rec['explanations'], rank=i, fuzzy_breakdown=rec.get('fuzzy_breakdown'), fuzzy_score=rec.get('fuzzy_score'), rule_score=rec.get('rule_score'), rule_details=rec.get('rule_details'))
    else:
        for i in range(0, len(recs), 2):
            row = st.columns(2)
            for j in range(2):
                if i + j < len(recs):
                    rec = recs[i+j]
                    with row[j]:
                        display_phone_card(rec['phone'], rec['total_score'], rec['explanations'], rank=i+j+1, fuzzy_breakdown=rec.get('fuzzy_breakdown'), fuzzy_score=rec.get('fuzzy_score'), rule_score=rec.get('rule_score'), rule_details=rec.get('rule_details'))

    if len(recs) >= 2:
        st.markdown("---")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"<div style='font-weight:600;color:var(--text);'>⚡ So sánh nhanh 2 máy top đầu</div>", unsafe_allow_html=True)
        with c2:
            if st.button("📊 So sánh ngay", type="primary", key="quick_cmp"):
                st.session_state.comparison_list = [rec['phone'] for rec in recs[:2]]
                st.rerun()

        cols = st.columns(2)
        for i, rec in enumerate(recs[:2]):
            with cols[i]:
                ph = rec['phone']
                pct = int(rec['total_score']*100)
                clr = score_color(pct)
                st.markdown(f"""
                <div style='background:var(--card-bg);border:1px solid var(--card-border);border-radius:var(--radius);padding:1rem;text-align:center;box-shadow:var(--card-shadow);'>
                    <div style='font-size:2rem;'>📱</div>
                    <div style='font-weight:600;color:var(--text);font-size:0.92rem;margin:6px 0 2px;'>{ph.get('name','')[:35]}</div>
                    <div style='font-size:0.82rem;color:var(--text-secondary);'>{format_price(ph.get('price'))}</div>
                    <div style='margin-top:6px;'><span class='score-circle' style='background:{clr};display:inline-flex;'>{pct}%</span></div>
                    <div style='font-size:0.7rem;color:var(--text-secondary);margin-top:2px;'>phù hợp</div>
                </div>
                """, unsafe_allow_html=True)
                if rec['explanations']:
                    with st.expander("Tại sao?"):
                        for e in rec['explanations']:
                            st.write(f"• {e}")

def main():
    has_results = len(st.session_state.recommendations) > 0

    with st.sidebar:
        st.markdown("**🔍 Tìm kiếm**")

        search_method = st.radio("", ["🗣️ Tìm bằng mô tả", "⚙️ Tìm kiếm chi tiết", "❓ Hỏi đáp tìm máy"], label_visibility="collapsed")

        if search_method == "🗣️ Tìm bằng mô tả":
            st.markdown("Mô tả nhu cầu của bạn")
            if '_suggested' in st.session_state:
                st.session_state.search_query = st.session_state.pop('_suggested')
            st.text_area("", height=90, placeholder="VD: Điện thoại chụp ảnh đẹp tầm 15 triệu", label_visibility="collapsed", key="search_query")
            st.markdown("Gợi ý nhanh")
            for t in ["Điện thoại chơi game tầm 20 triệu", "iPhone giá dưới 15 triệu", "Pin trâu giá rẻ", "Samsung màn hình gập", "Chụp ảnh đẹp cho học sinh", "Xiaomi pin lớn giá rẻ", "Điện thoại nhẹ dưới 180g", "Máy tính tiền 5G tầm 10 triệu"]:
                if st.button(t, key=f"t_{t}", use_container_width=True):
                    st.session_state._suggested = t
                    st.rerun()
            query = st.session_state.search_query
            if st.button("🔍 Tìm kiếm", type="primary", use_container_width=True):
                run_search(search_method, st.session_state.search_query)
                st.session_state._just_searched = True
                st.rerun()
        elif search_method == "\u2753 H\u1ecfi \u0111\u00e1p t\u00ecm m\u00e1y":
            st.markdown("Tr\u1ea3 l\u1eddi t\u1eebng c\u00e2u h\u1ecfi \u0111\u1ec3 t\u00ecm m\u00e1y ph\u00f9 h\u1ee3p")
            if 'qa_step' not in st.session_state:
                st.session_state.qa_step = 0
                st.session_state.qa_answers = {}
            step = st.session_state.qa_step
            qa_questions = [
                ("B\u1ea1n mu\u1ed1n mua \u0111i\u1ec7n tho\u1ea1i h\u00e3ng n\u00e0o?", ["Kh\u00f4ng quan tr\u1ecdng", "Apple", "Samsung", "Xiaomi", "OPPO", "Vivo", "Realme"], "brand"),
                ("Ng\u00e2n s\u00e1ch c\u1ee7a b\u1ea1n kho\u1ea3ng bao nhi\u00eau?", ["D\u01b0\u1edbi 5 tri\u1ec7u", "5-10 tri\u1ec7u", "10-20 tri\u1ec7u", "20-35 tri\u1ec7u", "Tr\u00ean 35 tri\u1ec7u"], "budget"),
                ("B\u1ea1n d\u00f9ng \u0111i\u1ec7n tho\u1ea1i \u0111\u1ec3 l\u00e0m g\u00ec ch\u00ednh?", ["Ch\u01a1i game", "Ch\u1ee5p \u1ea3nh", "Pin tr\u00e2u", "Cao c\u1ea5p", "V\u0103n ph\u00f2ng", "Gi\u1ea3i tr\u00ed"], "purpose"),
                ("B\u1ea1n c\u00f3 y\u00eau c\u1ea7u \u0111\u1eb7c bi\u1ec7t n\u00e0o kh\u00f4ng?", ["Kh\u00f4ng", "M\u00e0n h\u00ecnh g\u1eadp", "5G", "S\u1ea1c kh\u00f4ng d\u00e2y", "NFC"], "special"),
            ]
            if step < len(qa_questions):
                q_text, options, key = qa_questions[step]
                st.markdown(f"**{q_text}**")
                ans = st.radio("", options, key=f"qa_{step}", label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("\u23ea Quay l\u1ea1i", disabled=(step==0), use_container_width=True):
                        st.session_state.qa_step -= 1
                        st.rerun()
                with c2:
                    if st.button("Ti\u1ebfp theo \u23e9", use_container_width=True):
                        st.session_state.qa_answers[key] = ans
                        st.session_state.qa_step += 1
                        st.rerun()
            else:
                st.success("\u2705 \u0110\u00e3 tr\u1ea3 l\u1eddi xong! Nh\u1ea5n t\u00ecm ki\u1ebfm \u0111\u1ec3 xem g\u1ee3i \u00fd.")
                if st.button("\U0001f50d T\u00ecm ngay", type="primary", use_container_width=True):
                    ans = st.session_state.qa_answers
                    qa_parsed = {}
                    budget_map = {"D\u01b0\u1edbi 5 tri\u1ec7u": 5000000, "5-10 tri\u1ec7u": 10000000, "10-20 tri\u1ec7u": 20000000, "20-35 tri\u1ec7u": 35000000, "Tr\u00ean 35 tri\u1ec7u": 50000000}
                    purpose_map = {"Ch\u01a1i game": "gaming", "Ch\u1ee5p \u1ea3nh": "photography", "Pin tr\u00e2u": "battery_life", "Cao c\u1ea5p": "premium", "V\u0103n ph\u00f2ng": "office", "Gi\u1ea3i tr\u00ed": "media"}
                    special_map = {"M\u00e0n h\u00ecnh g\u1eadp": "innovation"}
                    if ans.get('budget') in budget_map:
                        qa_parsed['budget'] = budget_map[ans['budget']]
                    if ans.get('purpose') in purpose_map:
                        qa_parsed['user_need'] = purpose_map[ans['purpose']]
                    if ans.get('brand') and ans['brand'] != "Kh\u00f4ng quan tr\u1ecdng":
                        qa_parsed['preferred_brand'] = ans['brand']
                    if ans.get('special') in special_map:
                        qa_parsed['user_need'] = special_map[ans['special']]
                    if ans.get('special') == "5G":
                        qa_parsed['network'] = '5G'
                    if ans.get('special') == "NFC":
                        qa_parsed['features'] = ['NFC']
                    qa_query = " ".join(f"{k}:{v}" for k, v in qa_parsed.items())
                    run_search(search_method, qa_query, qa_parsed)
                    st.session_state._just_searched = True
                    st.session_state.qa_step = 0
                    st.session_state.qa_answers = {}
                    st.rerun()
                if st.button("\U0001f504 L\u00e0m l\u1ea1i", use_container_width=True):
                    st.session_state.qa_step = 0
                    st.session_state.qa_answers = {}
                    st.rerun()
        else:
            st.markdown("Ng\u00e2n s\u00e1ch")
            budget_range = st.slider("triệu", min_value=0, max_value=65, value=(5, 25), step=1, label_visibility="collapsed")
            st.markdown("Hãng")
            selected_brand = st.selectbox("", ["Tất cả", "Apple", "Samsung", "Xiaomi", "OPPO", "Vivo", "Realme", "OnePlus"], label_visibility="collapsed")
            st.markdown("Mục đích")
            use_cases = {"Tất cả": None, "🎮 Chơi game": "gaming", "📸 Chụp ảnh": "photography", "🔋 Pin trâu": "battery_life", "💼 Văn phòng": "office", "👑 Cao cấp": "premium", "🎓 Học sinh": "student", "💼 Doanh nhân": "business", "🤳 Selfie": "selfie"}
            selected_use = st.selectbox("", list(use_cases.keys()), label_visibility="collapsed")
            st.markdown("Phân loại")
            # Updated: Phản ánh các phân khúc mới
            cat_options = {"Tất cả": None, 
                          "👑 Cao cấp (>20M)": "flagship", 
                          "💼 Cận cao cấp (10-20M)": "midrange", 
                          "💰 Tầm trung (5-10M)": "budget", 
                          "📱 Giá rẻ (<5M)": "entry", 
                          "🎮 Gaming": "gaming", 
                          "📂 Màn hình gập": "foldable"}
            selected_cat = st.selectbox("Phân loại", list(cat_options.keys()), label_visibility="collapsed")
            with st.expander("Tùy chọn thêm"):
                c1, c2 = st.columns(2)
                with c1:
                    want_5g = st.checkbox("📶 5G")
                    high_ram = st.checkbox("💾 RAM ≥12GB")
                    good_camera = st.checkbox("📷 ≥48MP")
                    need_nfc = st.checkbox("📡 NFC")
                    need_otg = st.checkbox("🔌 OTG")
                with c2:
                    big_battery = st.checkbox("🔋 ≥5000mAh")
                    light_weight = st.checkbox("🪶 Nhẹ <175g")
                    small_screen = st.checkbox("📱 <6\"")
                    large_screen = st.checkbox("📱 ≥6.5\"")
                    high_refresh = st.checkbox("⚡ ≥120Hz")
            if st.button("🔍 Tìm kiếm", type="primary", use_container_width=True):
                # Define category mapping first
                cat_options = {"Tất cả": None, 
                              "👑 Cao cấp (>20M)": "flagship", 
                              "💼 Cận cao cấp (10-20M)": "midrange", 
                              "💰 Tầm trung (5-10M)": "budget", 
                              "📱 Giá rẻ (<5M)": "entry", 
                              "🎮 Gaming": "gaming", 
                              "📂 Màn hình gập": "foldable"}
                
                # Get actual category value (None if "Tất cả")
                selected_cat_value = cat_options.get(selected_cat)
                
                # Build query string for display - only add category if not "Tất cả"
                q = []
                if use_cases[selected_use]: q.append(f"user_need: {use_cases[selected_use]}")
                q.append(f"budget: {budget_range[1]*1000000}")
                if selected_brand != "Tất cả": q.append(f"brand: {selected_brand}")
                if selected_cat_value: q.append(f"category: {selected_cat_value}")
                if want_5g: q.append("5G")
                if high_ram: q.append("RAM cao")
                if good_camera: q.append("camera tốt")
                if big_battery: q.append("pin khỏe")
                if light_weight: q.append("máy nhẹ")
                if small_screen: q.append("màn hình nhỏ")
                if large_screen: q.append("màn hình lớn")
                if need_nfc: q.append("có NFC")
                if need_otg: q.append("hỗ trợ OTG")
                if high_refresh: q.append("tần số quét cao")
                user_query = " ".join(q)
                
                # Build parsed_input
                parsed_input = {}
                if use_cases[selected_use]: parsed_input['user_need'] = use_cases[selected_use]
                parsed_input['budget'] = budget_range[1] * 1000000
                # Fix: Thêm budget_min
                if budget_range[0] > 0:
                    parsed_input['budget_min'] = budget_range[0] * 1000000
                if selected_brand != "Tất cả": parsed_input['preferred_brand'] = selected_brand
                # Fix: Only set category_filter if not "Tất cả"
                if selected_cat_value:
                    parsed_input['category_filter'] = selected_cat_value
                if want_5g: parsed_input.setdefault('features', []).append('5G')
                if high_ram: parsed_input['min_ram'] = '12GB'
                if big_battery: parsed_input['min_battery'] = 5000
                if light_weight: parsed_input['max_weight'] = 175
                if good_camera: parsed_input['min_camera_mp'] = 48
                if small_screen: parsed_input['max_screen_size'] = 6.0
                if large_screen: parsed_input['min_screen_size'] = 6.5
                if high_refresh: parsed_input['min_refresh_rate'] = 120
                if need_nfc: parsed_input['required_nfc'] = True
                if need_otg: parsed_input['required_memory_card_slot'] = True
                
                run_search(search_method, user_query, parsed_input)
                st.session_state._just_searched = True
                st.rerun()

        if st.session_state.search_history:
            st.markdown("---")
            st.markdown("📜 Lịch sử")
            for h in reversed(st.session_state.search_history[-5:]):
                st.markdown(f"""
                <div style='background:var(--card-bg);border-radius:6px;padding:5px 8px;margin:3px 0;font-size:0.72rem;border:1px solid var(--card-border);'>
                    <div style='color:var(--text);'>{h['query'][:30]}{'...' if len(h['query'])>30 else ''}</div>
                    <div style='color:var(--text-secondary);'>{h['time']} • {h['results']} kết quả</div>
                </div>
                """, unsafe_allow_html=True)

    if st.session_state.get('selected_category'):
        need = st.session_state.selected_category
        st.session_state.selected_category = None
        cat_q = {"gaming":"Tôi cần điện thoại chơi game","photography":"Tôi cần điện thoại chụp ảnh đẹp","battery_life":"Tôi cần điện thoại pin trâu","media":"Tôi cần điện thoại xem phim giải trí","office":"Tôi cần điện thoại văn phòng","premium":"Tôi cần điện thoại cao cấp","student":"Tôi cần điện thoại cho học sinh","business":"Tôi cần điện thoại doanh nhân","selfie":"Tôi cần điện thoại selfie đẹp"}
        q = cat_q.get(need, "")
        if q:
            run_search("🗣️ Tìm bằng mô tả", q)
            st.session_state._just_searched = True
            has_results = True

    if st.session_state.get('_search_attempted') or has_results:
        show_results()
        show_comparison()
    else:
        show_welcome()

    stats = load_stats()
    if stats:
        rule_count = len(st.session_state.advisor.knowledge_base.get_all_rules()) if st.session_state.advisor else 30
        st.markdown(f"<div class='footer'>Hệ Chuyên Gia • {rule_count} rules • {stats['total_phones']} phone facts • 58 trường • Forward Chaining + Fuzzy Logic</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
