# ============================================================
# import_datasets.py —— 三大气象数据集一键导入 PostgreSQL
# ============================================================
# 使用前请先安装依赖：
#   pip install psycopg2-binary --break-system-packages
#
# 修改下方 CONFIG 区域的连接信息，然后运行：
#   python import_datasets.py
# ============================================================

import csv
import sys
import os
from datetime import datetime

# ==================== 配置区域（密码请通过环境变量 DB_PASSWORD 设置）====================
CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "dbname": os.environ.get("DB_NAME", "AcademicSearchDB"),
}

if not CONFIG["password"]:
    print("❌ 错误：请设置环境变量 DB_PASSWORD")
    print("   Windows:  set DB_PASSWORD=你的密码")
    print("   macOS/Linux: export DB_PASSWORD=你的密码")
    sys.exit(1)

# 数据集目录（根据实际情况修改）
DATA_DIR = r"C:\Users\hainuo\Desktop\检索系统\6.0版本\数据集"
# =====================================================================

# ---- 热带气旋区域过滤（太平洋区域）----
PACIFIC_LON_MIN = 100.0
PACIFIC_LON_MAX = 180.0
PACIFIC_LAT_MIN = 0.0
PACIFIC_LAT_MAX = 60.0

# ---- 地震区域过滤（中国及周边）----
# 设为 None 表示不过滤，导入全部数据；设具体值则只导入该区域
EARTHQUAKE_LON_MIN = 73.0
EARTHQUAKE_LON_MAX = 135.0
EARTHQUAKE_LAT_MIN = 18.0
EARTHQUAKE_LAT_MAX = 54.0


def connect():
    """连接 PostgreSQL"""
    try:
        import psycopg2
    except ImportError:
        print("❌ 缺少 psycopg2 库！请先安装：")
        print("   pip install psycopg2-binary --break-system-packages")
        sys.exit(1)

    try:
        conn = psycopg2.connect(**CONFIG)
        conn.autocommit = False
        print(f"✅ 已连接到 PostgreSQL: {CONFIG['host']}:{CONFIG['port']}/{CONFIG['dbname']}")
        return conn
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请检查 CONFIG 中的 host / port / user / password 是否正确")
        sys.exit(1)


def safe_float(val, default=None):
    """安全转为 float，空值返回 default"""
    if val is None or str(val).strip() == '':
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val, default=None):
    """安全转为 int"""
    if val is None or str(val).strip() == '':
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def parse_iso_time(val):
    """解析 ISO 时间字符串，如 '2024-07-01 12:00:00'"""
    if not val or str(val).strip() == '':
        return None
    val = str(val).strip()
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ']:
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    # 最后尝试截断到 19 字符
    try:
        return datetime.strptime(val[:19], '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None


def sshes_to_category(sshs):
    """USA_SSHS 数值转风暴等级字符串"""
    if sshs is None:
        return ''
    sshs = int(sshs)
    if sshs < 0:
        return ''
    mapping = {-1: '', 0: 'TD', 1: 'TS', 2: 'C1', 3: 'C2', 4: 'C3', 5: 'C4', 6: 'C5'}
    return mapping.get(sshs, f'C{sshs}' if sshs >= 1 else '')


# ============================================================
# 1. 导入 IBTrACS 热带气旋数据
# ============================================================
def import_typhoon(conn):
    csv_path = os.path.join(DATA_DIR, "热带气旋", "ibtracs.ALL.list.v04r01.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️  跳过台风：找不到文件 {csv_path}")
        return

    cur = conn.cursor()

    # 先清空旧数据
    cur.execute("TRUNCATE TABLE typhoon_track, typhoon_info RESTART IDENTITY CASCADE;")

    # 第一步：逐行读取 CSV，分类为太平洋台风数据
    print("\n📖 正在读取 IBTrACS 热带气旋数据...")
    print("   第1步：扫描并过滤太平洋区域数据（经度 100°E-180°E，纬度 0°-60°N）")

    typhoon_data = {}  # sid -> {info: {...}, tracks: [...]}

    with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)
        total_rows = 0
        pacific_rows = 0

        for row in reader:
            total_rows += 1

            lat = safe_float(row.get('LAT'))
            lon = safe_float(row.get('LON'))
            sid = (row.get('SID') or '').strip()

            if lat is None or lon is None or not sid:
                continue

            # 过滤太平洋区域 (经度 100~180, 纬度 0~60)
            if not (PACIFIC_LON_MIN <= lon <= PACIFIC_LON_MAX and
                    PACIFIC_LAT_MIN <= lat <= PACIFIC_LAT_MAX):
                continue

            pacific_rows += 1

            if sid not in typhoon_data:
                typhoon_data[sid] = {'info': None, 'tracks': []}

            date_time = parse_iso_time(row.get('ISO_TIME'))
            wind = safe_float(row.get('USA_WIND'), 0)
            pres = safe_float(row.get('USA_PRES'), 9999)
            sshs = safe_int(row.get('USA_SSHS'))

            track = {
                'date_time': date_time,
                'latitude': lat,
                'longitude': lon,
                'max_sustained_wind': wind,
                'min_pressure': pres,
                'storm_category': sshes_to_category(sshs),
                'wind_radius7_ne': safe_float(row.get('USA_R34_NE'), 0),
                'wind_radius7_se': safe_float(row.get('USA_R34_SE'), 0),
                'wind_radius7_sw': safe_float(row.get('USA_R34_SW'), 0),
                'wind_radius7_nw': safe_float(row.get('USA_R34_NW'), 0),
                'wind_radius10_ne': safe_float(row.get('USA_R50_NE'), 0),
                'wind_radius10_se': safe_float(row.get('USA_R50_SE'), 0),
                'wind_radius10_sw': safe_float(row.get('USA_R50_SW'), 0),
                'wind_radius10_nw': safe_float(row.get('USA_R50_NW'), 0),
            }
            typhoon_data[sid]['tracks'].append(track)

            # 汇总 typhoon_info
            season = safe_int(row.get('SEASON'))
            name = (row.get('NAME') or '').strip()
            basin = (row.get('BASIN') or 'WP').strip()

            if typhoon_data[sid]['info'] is None:
                typhoon_data[sid]['info'] = {
                    'typhoon_id': sid,
                    'typhoon_name': name,
                    'season': season,
                    'basin': basin,
                    'max_wind': wind,
                    'min_pressure': pres,
                    'start_time': date_time,
                    'end_time': date_time,
                }
            else:
                info = typhoon_data[sid]['info']
                if wind > info['max_wind']:
                    info['max_wind'] = wind
                if pres < info['min_pressure']:
                    info['min_pressure'] = pres
                if date_time and (info['start_time'] is None or date_time < info['start_time']):
                    info['start_time'] = date_time
                if date_time and (info['end_time'] is None or date_time > info['end_time']):
                    info['end_time'] = date_time

    print(f"   扫描完成：总行数 {total_rows:,}，太平洋区域 {pacific_rows:,} 行，共 {len(typhoon_data):,} 个台风")

    # 第二步：插入 typhoon_info
    print("   第2步：插入台风基本信息...")
    typhoon_count = 0
    for sid, data in typhoon_data.items():
        info = data['info']
        info['total_points'] = len(data['tracks'])
        cur.execute("""
            INSERT INTO typhoon_info (typhoon_id, typhoon_name, season, basin,
                max_wind, min_pressure, total_points, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (typhoon_id) DO NOTHING
        """, (
            info['typhoon_id'], info['typhoon_name'], info['season'], info['basin'],
            info['max_wind'], info['min_pressure'], info['total_points'],
            info['start_time'], info['end_time']
        ))
        typhoon_count += 1

    conn.commit()
    print(f"   插入台风基本信息 {typhoon_count:,} 条")

    # 第三步：批量插入 typhoon_track
    print("   第3步：批量插入台风路径点...")
    # collect all tracks
    track_rows = []
    for sid, data in typhoon_data.items():
        for t in data['tracks']:
            track_rows.append((
                sid, t['date_time'], t['latitude'], t['longitude'],
                t['max_sustained_wind'], t['min_pressure'], t['storm_category'],
                t['wind_radius7_ne'], t['wind_radius7_se'],
                t['wind_radius7_sw'], t['wind_radius7_nw'],
                t['wind_radius10_ne'], t['wind_radius10_se'],
                t['wind_radius10_sw'], t['wind_radius10_nw'],
            ))

    # 分批提交，每批 5000 行
    BATCH = 5000
    for i in range(0, len(track_rows), BATCH):
        batch = track_rows[i:i + BATCH]
        cur.executemany("""
            INSERT INTO typhoon_track (typhoon_id, date_time, latitude, longitude,
                max_sustained_wind, min_pressure, storm_category,
                wind_radius7_ne, wind_radius7_se, wind_radius7_sw, wind_radius7_nw,
                wind_radius10_ne, wind_radius10_se, wind_radius10_sw, wind_radius10_nw)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, batch)
        conn.commit()
        print(f"   已插入 {min(i + BATCH, len(track_rows)):,} / {len(track_rows):,} 个路径点", end='\r')

    print(f"\n   插入台风路径点 {len(track_rows):,} 条")
    cur.close()
    print(f"✅ 台风数据导入完成！{typhoon_count:,} 个台风，{len(track_rows):,} 个路径点")


# ============================================================
# 2. 导入 USGS 地震数据
# ============================================================
def import_earthquake(conn):
    eq_dir = os.path.join(DATA_DIR, "地震")
    csv_files = sorted([f for f in os.listdir(eq_dir) if f.endswith('.csv')])

    if not csv_files:
        print(f"⚠️  跳过地震：找不到 CSV 文件于 {eq_dir}")
        return

    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE earthquake_info RESTART IDENTITY CASCADE;")

    print(f"\n📖 正在导入 USGS 地震数据（{len(csv_files)} 个文件）...")

    total_rows = 0
    total_inserted = 0

    for csv_file in csv_files:
        csv_path = os.path.join(eq_dir, csv_file)
        file_rows = 0

        with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            batch = []

            for row in reader:
                total_rows += 1
                file_rows += 1

                lat = safe_float(row.get('latitude'))
                lon = safe_float(row.get('longitude'))

                if lat is None or lon is None:
                    continue

                # 区域过滤（如果配置了）
                if EARTHQUAKE_LON_MIN is not None:
                    if not (EARTHQUAKE_LON_MIN <= lon <= EARTHQUAKE_LON_MAX and
                            EARTHQUAKE_LAT_MIN <= lat <= EARTHQUAKE_LAT_MAX):
                        continue

                batch.append((
                    (row.get('id') or '').strip(),
                    parse_iso_time(row.get('time')),
                    lat, lon,
                    safe_float(row.get('depth'), 0),
                    safe_float(row.get('mag'), 0),
                    (row.get('magType') or '').strip(),
                    safe_int(row.get('nst'), 0),
                    safe_float(row.get('gap'), 0),
                    safe_float(row.get('dmin'), 0),
                    safe_float(row.get('rms'), 0),
                    (row.get('place') or '').strip()[:300],
                    (row.get('status') or '').strip(),
                    safe_int(row.get('tsunami'), 0) if row.get('tsunami') else 0,
                    (row.get('alert') or '').strip(),
                    safe_int(row.get('significance'), 0),
                    safe_float(row.get('horizontalError'), 0),
                    safe_float(row.get('depthError'), 0),
                    safe_float(row.get('magError'), 0),
                    safe_int(row.get('magNst'), 0),
                    parse_iso_time(row.get('updated')),
                ))

                # 批量插入
                if len(batch) >= 1000:
                    inserted = _insert_eq_batch(cur, batch)
                    total_inserted += inserted
                    conn.commit()
                    batch = []

            # 剩余批次
            if batch:
                inserted = _insert_eq_batch(cur, batch)
                total_inserted += inserted
                conn.commit()

        print(f"   {csv_file}: {file_rows:,} 行")

    cur.close()
    print(f"✅ 地震数据导入完成！从 {total_rows:,} 行中导入了 {total_inserted:,} 条记录")


def _insert_eq_batch(cur, batch):
    """批量插入地震数据，处理重复"""
    try:
        cur.executemany("""
            INSERT INTO earthquake_info (event_id, date_time, latitude, longitude,
                depth, magnitude, mag_type, nst, gap, dmin, rms, place, status,
                tsunami, alert, significance,
                horizontal_error, depth_error, mag_error, mag_nst, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING
        """, batch)
        return cur.rowcount
    except Exception as e:
        # 如果批量插入失败，尝试逐条插入
        inserted = 0
        for row in batch:
            try:
                cur.execute("""
                    INSERT INTO earthquake_info (event_id, date_time, latitude, longitude,
                        depth, magnitude, mag_type, nst, gap, dmin, rms, place, status,
                        tsunami, alert, significance,
                        horizontal_error, depth_error, mag_error, mag_nst, updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO NOTHING
                """, row)
                inserted += 1
            except Exception:
                pass
        return inserted


# ============================================================
# 3. 导入 NOAA 龙卷风数据
# ============================================================
def import_tornado(conn):
    csv_path = os.path.join(DATA_DIR, "龙卷风", "1950-2024_actual_tornadoes.csv")
    if not os.path.exists(csv_path):
        print(f"⚠️  跳过龙卷风：找不到文件 {csv_path}")
        return

    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE tornado_info RESTART IDENTITY CASCADE;")

    print(f"\n📖 正在导入 NOAA 龙卷风数据...")

    total_rows = 0
    batch = []

    # 美国州缩写 → 名称映射（常见州）
    US_STATES = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia',
        'PR': 'Puerto Rico', 'VI': 'Virgin Islands', 'GU': 'Guam',
    }

    with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_rows += 1

            # 构建时间
            date_str = (row.get('date') or '').strip()
            time_str = (row.get('time') or '').strip()

            date_time = None
            if date_str:
                try:
                    if time_str:
                        date_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
                    else:
                        date_time = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    pass

            lat = safe_float(row.get('slat'))
            lon = safe_float(row.get('slon'))
            if lat is None or lon is None:
                continue

            st = (row.get('st') or '').strip()
            province = US_STATES.get(st, st)
            mag = safe_int(row.get('mag'), 0)
            fc = safe_int(row.get('fc'), 0)
            inj = safe_int(row.get('inj'), 0)
            fat = safe_int(row.get('fat'), 0)
            loss = safe_float(row.get('loss'), 0)

            # EF 等级
            ef_scale = f"F{fc}" if fc > 0 else f"F{mag}" if mag > 0 else ''

            # 灾害描述
            damage_parts = []
            if loss and loss > 0:
                damage_parts.append(f"财产损失约{loss:.0f}万美元")
            damage = '; '.join(damage_parts)

            batch.append((
                date_time, lat, lon,
                (row.get('stn') or '').strip()[:200],  # 县名作为地点
                province,
                ef_scale, mag,
                inj + fat,  # casualties = injuries + deaths
                fat,       # deaths
                inj,       # injuries
                damage,
                'confirmed',  # NOAA 数据默认为确认
                'NOAA SPC',
            ))

            if len(batch) >= 2000:
                cur.executemany("""
                    INSERT INTO tornado_info (date_time, latitude, longitude,
                        place, province, ef_scale, magnitude,
                        casualties, deaths, injuries,
                        damage, confidence, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, batch)
                conn.commit()
                print(f"   已导入 {total_rows:,} 条", end='\r')
                batch = []

        if batch:
            cur.executemany("""
                INSERT INTO tornado_info (date_time, latitude, longitude,
                    place, province, ef_scale, magnitude,
                    casualties, deaths, injuries,
                    damage, confidence, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, batch)
            conn.commit()

    cur.close()
    print(f"\n✅ 龙卷风数据导入完成！共导入 {total_rows:,} 条记录")


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("  气象数据集一键导入工具")
    print("  MySQL → PostgreSQL 迁移")
    print("=" * 60)

    conn = connect()

    try:
        import_typhoon(conn)
        import_earthquake(conn)
        import_tornado(conn)

        # 验证
        print("\n" + "=" * 60)
        print("📊 导入完成！数据统计：")
        cur = conn.cursor()
        tables = [
            ('台风基本信息', 'typhoon_info'),
            ('台风路径点', 'typhoon_track'),
            ('地震信息', 'earthquake_info'),
            ('龙卷风信息', 'tornado_info'),
        ]
        for label, tbl in tables:
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            count = cur.fetchone()[0]
            print(f"   {label}（{tbl}）: {count:,} 条")
        cur.close()

    except Exception as e:
        conn.rollback()
        print(f"\n❌ 导入出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("\n数据库连接已关闭。")


if __name__ == '__main__':
    main()
