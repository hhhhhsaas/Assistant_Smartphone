#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Index CellphoneS_Data_Final_Cleaned.xlsx into Knowledge Base.
Parse 55 columns, clean data, determine categories, extract features.
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openpyxl import load_workbook
import json, numpy as np, re
from pathlib import Path
import pickle
from knowledge_base.rules import get_classification_rules


def clean_price(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    try:
        return int(float(v))
    except (ValueError, TypeError):
        digits = re.sub(r'[^\d]', '', str(v))
        return int(digits) if digits else None


def clean_ram(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).upper().strip()
    m = re.search(r'(\d+)', s)
    if not m:
        return None
    val = m.group(1)
    return f"{val}GB" if 'GB' not in s else s


def clean_storage(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).upper().strip()
    m = re.search(r'(\d+)', s)
    if not m:
        return None
    val = m.group(1)
    if 'TB' in s:
        return f"{val}TB"
    return f"{val}GB" if 'GB' not in s else s


def clean_numeric(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    m = re.search(r'(\d+\.?\d*)', str(v))
    return float(m.group(1)) if m else None


def parse_battery(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).strip()
    m = re.search(r'([\d.,]+)\s*m[Aa][Hh]', s)
    if m:
        try:
            raw = m.group(1).replace('.', '').replace(',', '')
            return int(raw)
        except:
            pass
    m2 = re.search(r'^(\d{3,5})$', s)
    if m2:
        return int(m2.group(1))
    return None


def clean_camera_mp(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    m = re.search(r'(\d+\.?\d*)', str(v))
    return int(float(m.group(1))) if m else None


def parse_network_support(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).upper()
    if '5G' in s:
        return '5G'
    return s


def parse_nfc(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).lower()
    return 'Có' in s or 'yes' in s or 'true' in s or v is True


def extract_ram_gb(v):
    if not v:
        return 0
    m = re.search(r'(\d+)', str(v))
    return int(m.group(1)) if m else 0


def extract_refresh_hz(v):
    if not v or (isinstance(v, float) and np.isnan(v)):
        return 60
    m = re.search(r'(\d+)', str(v))
    return int(m.group(1)) if m else 60


def determine_category(phone_data):
    """Dùng ClassificationRule từ Knowledge Base để phân loại phone"""
    cls_rules = get_classification_rules()
    for rule in cls_rules:
        if rule.evaluate(phone_data):
            return rule.category
    return 'entry'  # fallback


def extract_features(phone_data):
    features = []
    name = str(phone_data.get('name', '')).lower()
    ram = str(phone_data.get('ram', ''))
    storage = str(phone_data.get('storage', ''))
    network = str(phone_data.get('network_support', ''))
    refresh = str(phone_data.get('refresh_rate', ''))
    special = str(phone_data.get('special_features', '')).lower()
    cooling = str(phone_data.get('cooling_system', '')).lower()

    # 5G
    if '5g' in name or '5G' in network or '5g' in special:
        features.append('5G')

    # Model tier
    for kw, tag in [('pro max', 'Pro Max'), ('ultra', 'Ultra'),
                     ('pro', 'Pro'), ('plus', 'Plus')]:
        if kw in name:
            features.append(tag)
            break

    # High RAM
    rm = re.search(r'(\d+)', ram)
    if rm and int(rm.group(1)) >= 12:
        features.append('High RAM')
    elif rm and int(rm.group(1)) >= 8:
        features.append('Large RAM')

    # High storage
    if 'TB' in storage.upper():
        features.append('High Storage')
    else:
        sm = re.search(r'(\d+)', storage)
        if sm and int(sm.group(1)) >= 512:
            features.append('High Storage')

    # High res camera
    cr = phone_data.get('camera_rear')
    if cr:
        try:
            if int(cr) >= 100:
                features.append('High Resolution Camera')
            elif int(cr) >= 48:
                features.append('Good Camera')
        except:
            pass

    # High refresh rate
    hz = extract_refresh_hz(refresh)
    if hz >= 120:
        features.append('High Refresh Rate')

    # NFC
    if phone_data.get('nfc'):
        features.append('NFC')

    # Wireless charging
    charging = str(phone_data.get('charging', '')).lower()
    if 'không dây' in charging or 'wireless' in charging:
        features.append('Wireless Charging')

    # Water resistant
    wr = str(phone_data.get('water_resistance', '')).lower()
    if 'ip' in wr:
        features.append('Water Resistant')

    # Gaming cooling
    if any(kw in cooling for kw in ['vapor chamber', 'tản nhiệt', 'làm mát',
                                     'e-sports', 'ice']):
        features.append('Cooling System')

    return features


def create_text_description(p):
    parts = [f"Tên: {p.get('name','')}", f"Hãng: {p.get('brand','')}"]
    if p.get('price'):
        parts.append(f"Giá: {p['price']:,} VND")
    for k, label in [('ram', 'RAM'), ('storage', 'Bộ nhớ'), ('processor', 'Chip'),
                     ('camera_rear', 'Camera sau'), ('camera_front', 'Camera trước'),
                     ('screen_size', 'Màn hình'), ('battery', 'Pin'), ('colors', 'Màu sắc')]:
        if p.get(k):
            unit = '"' if k == 'screen_size' else ('MP' if 'camera' in k else '')
            parts.append(f"{label}: {p[k]}{unit}")
    parts.append(f"Phân loại: {p.get('category','smartphone')}")
    if p.get('features'):
        parts.append(f"Tính năng: {', '.join(p['features'])}")
    return ". ".join(parts)


def main():
    print("=" * 60)
    print("INDEXING CELLPHONES DATA INTO KNOWLEDGE BASE")
    print("=" * 60)

    excel_path = Path("data/CellphoneS_Data_Final_Cleaned.xlsx")
    print(f"\n1. Loading: {excel_path}")

    wb = load_workbook(excel_path, read_only=True)
    ws = wb.active
    headers = [str(c.value) for c in ws[1] if c.value]

    mapping_file = Path("data/column_mapping.json")
    if not mapping_file.exists():
        print("ERROR: column_mapping.json not found!")
        return
    with open(mapping_file, 'r', encoding='utf-8') as f:
        column_mapping = json.load(f)

    print(f"   {len(headers)} columns mapped to {len(column_mapping)} fields")

    # Process rows
    print("\n2. Processing phone data...")
    phones, errors, skipped_no_price = [], [], 0

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        if not any(row):
            continue

        p = {}
        for i, val in enumerate(row):
            if i < len(headers) and val is not None:
                h = headers[i]
                if h in column_mapping:
                    p[column_mapping[h]] = val

        if not p.get('name'):
            errors.append(f"Row {row_idx}: No name")
            continue

        # Price — nếu không có, set = 0 (hiển thị "Liên Hệ" trong UI)
        price_raw = p.pop('price_raw', None) or p.get('price')
        price = clean_price(price_raw)
        if price is None:
            skipped_no_price += 1
            price = 0
        p['price'] = price

        # Clean fields
        if 'ram' in p:
            p['ram'] = clean_ram(p['ram'])
        if 'storage' in p:
            p['storage'] = clean_storage(p['storage'])
        if 'screen_size' in p:
            p['screen_size'] = clean_numeric(p['screen_size'])
        if 'weight' in p:
            p['weight'] = clean_numeric(p['weight'])
        if 'camera_rear' in p:
            p['camera_rear'] = clean_camera_mp(p['camera_rear'])
        if 'camera_front' in p:
            p['camera_front'] = clean_camera_mp(p['camera_front'])

        # Battery: use raw field or try Pin field
        batt = parse_battery(p.get('battery'))
        if batt:
            p['battery'] = batt
        else:
            p.pop('battery', None)

        # Network support
        net = parse_network_support(p.get('network_support'))
        if net:
            p['network_support'] = net

        # NFC
        nfc = parse_nfc(p.get('nfc'))
        if nfc is not None:
            p['nfc'] = nfc

        # Category
        p['category'] = determine_category(p)

        # Features
        p['features'] = extract_features(p)

        # ID
        brand_clean = re.sub(r'[^\w]', '_', str(p.get('brand', 'unknown')).lower().strip())[:30]
        name_clean = re.sub(r'[^\w]', '_', str(p.get('name', '')).lower().strip())[:60]
        p['id'] = f"{brand_clean}_{name_clean}_{row_idx}"

        # Clean up empty fields
        p = {k: v for k, v in p.items() if v is not None
             and (not isinstance(v, float) or not np.isnan(v))}

        phones.append(p)
        if len(phones) % 100 == 0:
            print(f"   Processed {len(phones)} phones...")

    wb.close()

    print(f"\n   Total: {len(phones)} phones indexed")
    print(f"   Skipped (no price): {skipped_no_price}")
    print(f"   Errors: {len(errors)}")
    if errors:
        for e in errors[:3]:
            print(f"     - {e}")

    # Save to vector store pickle (format compatible with PhoneFacts)
    print("\n3. Saving to vector store...")
    store_path = Path("data/cellphones_vector_store.pkl")
    data = {
        'metadata': phones,
        'embeddings': [],
        'ids': [p['id'] for p in phones]
    }
    with open(store_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"   Saved {len(phones)} phones to {store_path}")

    # Save full JSON
    print("\n4. Saving processed data...")
    with open("data/cellphones_processed_full.json", 'w', encoding='utf-8') as f:
        json.dump(phones, f, ensure_ascii=False, indent=2)

    # Stats
    categories = {}
    for p in phones:
        c = p.get('category', 'unknown')
        categories[c] = categories.get(c, 0) + 1

    prices = [p['price'] for p in phones if p.get('price', 0) > 0]
    brands = sorted(set(p.get('brand', '') for p in phones))
    has_ram = sum(1 for p in phones if p.get('ram'))
    has_battery = sum(1 for p in phones if p.get('battery'))
    has_camera = sum(1 for p in phones if p.get('camera_rear'))
    has_screen = sum(1 for p in phones if p.get('screen_size'))
    has_weight = sum(1 for p in phones if p.get('weight'))

    stats = {
        'total_phones': len(phones),
        'brands': brands,
        'categories': categories,
        'price_range': {
            'min': min(prices), 'max': max(prices),
            'avg': int(sum(prices) / len(prices)) if prices else 0
        },
        'data_quality': {
            'has_ram': has_ram, 'has_battery': has_battery,
            'has_camera': has_camera, 'has_screen': has_screen,
            'has_weight': has_weight,
            'total': len(phones)
        }
    }
    with open("data/cellphones_stats.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n   Saved stats: {stats['total_phones']} phones, {len(stats['brands'])} brands")

    # Summary
    print("\n" + "=" * 60)
    print("INDEXING SUMMARY")
    print("=" * 60)
    print(f"Total phones: {stats['total_phones']}")
    print(f"Brands: {len(stats['brands'])}")
    print(f"Price: {stats['price_range']['min']:,} - {stats['price_range']['max']:,} VND")
    print(f"Categories:")
    for c, n in sorted(categories.items()):
        print(f"  - {c}: {n}")
    print(f"\nData quality:")
    print(f"  RAM: {has_ram}/{len(phones)}")
    print(f"  Battery: {has_battery}/{len(phones)}")
    print(f"  Camera: {has_camera}/{len(phones)}")
    print(f"  Screen: {has_screen}/{len(phones)}")
    print(f"  Weight: {has_weight}/{len(phones)}")
    print("\n✅ Knowledge Base ready!")


if __name__ == "__main__":
    main()
