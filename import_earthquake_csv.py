"""
USGS 地震目录数据导入脚本

数据来源：USGS Earthquake Catalog（FDSN Event Web Service）
  Web 搜索：https://earthquake.usgs.gov/earthquakes/search/
  API 文档：https://earthquake.usgs.gov/fdsnws/event/1/

范围约束：中国境内及周边，经度 73°E–135°E，纬度 18°N–54°N

使用方式：
  # 方式 1：从本地 CSV 导入（CSV 不含 tsunami/alert/sig 时填默认值）
  python import_earthquake_csv.py --file "earthquake_data.csv"

  # 方式 2：通过 USGS GeoJSON API 拉取（推荐，含完整字段）
  python import_earthquake_csv.py --api --start-year 2000 --end-year 2025

  # 预览
  python import_earthquake_csv.py --file quakes.csv --dry-run

USGS CSV 标准列名（从 Web 搜索导出）：
  time, latitude, longitude, depth, mag, magType, nst, gap, dmin, rms,
  net, id, updated, place, type, horizontalError, depthError, magError,
  magNst, status, locationSource, magSource

  ⚠️ USGS CSV 默认不含 tsunami / alert / sig 三列！
     如需完整数据，推荐用 --api（GeoJSON 格式）导入。

USGS GeoJSON 字段映射（API 返回的 properties 对象）：
  ids     → EventID
  time    → DateTime (Unix ms)
  mag     → Magnitude
  ...
  tsunami → Tsunami (0/1)
  alert   → Alert
  sig     → Significance
"""

import csv
import sys
import os
import argparse
import io
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
import pymysql
from config import Config


def parse_float(v, default=0.0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def parse_int(v, default=0):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return default


def parse_usgs_datetime(s):
    """解析 USGS ISO 8601 时间字符串，如 '2025-03-28T06:20:52.940Z'"""
    if not s or not s.strip():
        return None
    s = s.strip()
    try:
        # 去掉毫秒部分
        if '.' in s:
            # 保留小数点前的部分 + 时区信息
            main, frac_tz = s.split('.', 1)
            # 从 frac_tz 中提取时区后缀（Z / +HH:MM / -HH:MM）
            tz = ''
            for ch in frac_tz:
                if ch in ('Z', '+', '-'):
                    tz = ch + frac_tz.split(ch, 1)[1] if ch in ('+', '-') else 'Z'
                    break
                if ch.isdigit():
                    continue
            s = main + tz

        # 处理时区
        if s.endswith('Z'):
            s = s[:-1]
        elif '+' in s or (s.count('-') > 2):
            # 有时区偏移，去掉（存 UTC，DB 无时区）
            for sep in ('+', '-'):
                idx = s.rfind(sep)
                if idx > 19:  # 时区在时间部分之后
                    s = s[:idx]
                    break

        if 'T' in s:
            return datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
        elif ' ' in s:
            return datetime.strptime(s[:19], '%Y-%m-%d %H:%M:%S')
        return None
    except (ValueError, IndexError):
        try:
            return datetime.strptime(s[:19], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return None


def read_events_from_csv(file_obj):
    """从 CSV 文件对象读取地震事件。USGS CSV 默认不含 tsunami/alert/sig，
       这三个字段取不到时自动填默认值。"""
    events = []
    reader = csv.DictReader(file_obj)
    for row in reader:
        # 优先用 id，兼容有的导出文件用 event_id
        event_id = (row.get('id') or row.get('event_id') or '').strip()
        if not event_id:
            continue

        events.append({
            'EventID': event_id,
            'DateTime': parse_usgs_datetime(row.get('time', '')),
            'Latitude': parse_float(row.get('latitude')),
            'Longitude': parse_float(row.get('longitude')),
            'Depth': parse_float(row.get('depth')),
            'Magnitude': parse_float(row.get('mag')),
            'MagType': (row.get('magType') or '').strip(),
            'Place': (row.get('place') or '').strip(),
            'Status': (row.get('status') or '').strip(),
            # tsunami/alert/sig: USGS CSV 默认不含这些列
            'Tsunami': parse_int(row.get('tsunami')),
            'Alert': (row.get('alert') or '').strip(),
            'Significance': parse_int(row.get('sig')),
            'Gap': parse_float(row.get('gap')),
            'Dmin': parse_float(row.get('dmin')),
            'Rms': parse_float(row.get('rms')),
            'Nst': parse_int(row.get('nst')),
            'HorizontalError': parse_float(row.get('horizontalError')),
            'DepthError': parse_float(row.get('depthError')),
            'MagError': parse_float(row.get('magError')),
            'MagNst': parse_int(row.get('magNst')),
            'Updated': parse_usgs_datetime(row.get('updated')),
        })
    return events


def fetch_from_usgs_geojson(start_year, end_year):
    """通过 USGS GeoJSON API 拉取完整字段的地震数据（含 tsunami/alert/sig）。
       API 限制单次最多 20000 条，按月拆分拉取。"""
    import requests

    all_events = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            url = (
                "https://earthquake.usgs.gov/fdsnws/event/1/query"
                f"?format=geojson"
                f"&starttime={year}-{month:02d}-01"
                f"&endtime={year}-{month:02d}-28"
                f"&minlatitude=18&maxlatitude=54"
                f"&minlongitude=73&maxlongitude=135"
            )
            month_events = []
            try:
                resp = requests.get(url, timeout=120)
                resp.raise_for_status()
                data = resp.json()
                for feature in data.get('features', []):
                    geom = feature.get('geometry', {}) or {}
                    coords = geom.get('coordinates', [0, 0, 0])
                    props = feature.get('properties', {}) or {}
                    ts = props.get('time')
                    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).replace(tzinfo=None) if ts else None

                    month_events.append({
                        'EventID': (feature.get('id') or props.get('ids') or '').strip(),
                        'DateTime': dt,
                        'Latitude': coords[1] if len(coords) > 1 else 0,
                        'Longitude': coords[0] if len(coords) > 0 else 0,
                        'Depth': coords[2] if len(coords) > 2 else 0,
                        'Magnitude': props.get('mag') or 0,
                        'MagType': (props.get('magType') or '').strip(),
                        'Place': (props.get('place') or '').strip(),
                        'Status': (props.get('status') or '').strip(),
                        'Tsunami': props.get('tsunami', 0) or 0,
                        'Alert': (props.get('alert') or '').strip(),
                        'Significance': props.get('sig', 0) or 0,
                        'Gap': props.get('gap') or 0,
                        'Dmin': props.get('dmin') or 0,
                        'Rms': props.get('rms') or 0,
                        'Nst': props.get('nst') or 0,
                        'HorizontalError': props.get('horizontalError') or 0,
                        'DepthError': props.get('depthError') or 0,
                        'MagError': props.get('magError') or 0,
                        'MagNst': props.get('magNst') or 0,
                        'Updated': datetime.fromtimestamp(props['updated'] / 1000, tz=timezone.utc).replace(tzinfo=None) if props.get('updated') else None,
                    })
                all_events.extend(month_events)
                print(f"  {year}-{month:02d}: {len(month_events)} 条")
            except Exception as e:
                print(f"  {year}-{month:02d}: 请求失败 ({e})")
    return all_events


def import_from_dir(csv_dir, dry_run=False):
    """批量导入目录下所有 CSV 文件（去重）"""
    import glob
    csv_files = sorted(glob.glob(os.path.join(csv_dir, '*.csv')))
    if not csv_files:
        print(f"\n[错误] 目录 {csv_dir} 下未找到 CSV 文件")
        return

    all_events = []
    for fpath in csv_files:
        print(f"\n[读取] {os.path.basename(fpath)}")
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            events = read_events_from_csv(f)
        valid = [e for e in events if e['DateTime'] is not None]
        print(f"  总: {len(events)}, 有效: {len(valid)}")
        all_events.extend(valid)

    # 去重（按 EventID）
    seen = set()
    deduped = []
    for e in all_events:
        if e['EventID'] not in seen:
            seen.add(e['EventID'])
            deduped.append(e)

    print(f"\n  全部文件: {len(all_events)} 条, 去重后: {len(deduped)} 条")

    if dry_run:
        _dry_run_preview(deduped)
        return

    _write_to_db(deduped)


def import_csv(csv_path=None, dry_run=False, api=False, start_year=None, end_year=None):
    """主导入流程"""
    if api:
        print(f"\n[API] 从 USGS GeoJSON API 拉取地震数据（{start_year}-{end_year}）...")
        events = fetch_from_usgs_geojson(start_year, end_year)
    else:
        print(f"\n[读取] {csv_path}")
        with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
            events = read_events_from_csv(f)

    # 过滤无时间的无效记录
    valid_events = [e for e in events if e['DateTime'] is not None]
    skip_no_time = len(events) - len(valid_events)

    print(f"  总记录: {len(events)}, 跳过(无时间): {skip_no_time}, 有效: {len(valid_events)}")

    if dry_run:
        _dry_run_preview(valid_events)
        return

    _write_to_db(valid_events)


def _write_to_db(events):
    """写入 EarthquakeInfo 表（不清空，追加模式；如需全量替换请先手动清库）"""
    conn = pymysql.connect(**Config.DB_CONFIG)
    cur = conn.cursor()

    print(f"\n[写入] {len(events)} 条 → EarthquakeInfo ...")
    sql = """
        INSERT INTO EarthquakeInfo
        (EventID, DateTime, Latitude, Longitude, Depth, Magnitude, MagType, Place,
         Status, Tsunami, Alert, Significance, Gap, Dmin, Rms, Nst,
         HorizontalError, DepthError, MagError, MagNst, Updated)
        VALUES (%(EventID)s, %(DateTime)s, %(Latitude)s, %(Longitude)s, %(Depth)s,
                %(Magnitude)s, %(MagType)s, %(Place)s,
                %(Status)s, %(Tsunami)s, %(Alert)s, %(Significance)s,
                %(Gap)s, %(Dmin)s, %(Rms)s, %(Nst)s,
                %(HorizontalError)s, %(DepthError)s, %(MagError)s, %(MagNst)s,
                %(Updated)s)
    """

    batch = []
    for e in valid_events:
        batch.append(e)
        if len(batch) >= 500:
            cur.executemany(sql, batch)
            conn.commit()
            batch = []

    if batch:
        cur.executemany(sql, batch)
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM EarthquakeInfo")
    total = cur.fetchone()[0]

    cur.execute("SELECT MIN(YEAR(DateTime)), MAX(YEAR(DateTime)) FROM EarthquakeInfo")
    yr_range = cur.fetchone()
    cur.execute("""
        SELECT MAX(Magnitude),
               COUNT(CASE WHEN Magnitude >= 6.0 THEN 1 END),
               COUNT(CASE WHEN Magnitude >= 7.0 THEN 1 END)
        FROM EarthquakeInfo
    """)
    mag_stats = cur.fetchone()

    print(f"\n[完成] 导入 {total} 条地震记录")
    if yr_range and yr_range[0] is not None:
        print(f"  时间范围: {yr_range[0]} - {yr_range[1]}")
    if mag_stats:
        print(f"  最大震级: M{mag_stats[0]},  M≥6.0: {mag_stats[1]} 次,  M≥7.0: {mag_stats[2]} 次")
    cur.close()
    conn.close()


def _dry_run_preview(events):
    """预览前 5 条记录和统计"""
    print(f"\n[Dry Run] 预览前 5 条:")
    for e in events[:5]:
        dt = e['DateTime'].strftime('%Y-%m-%d %H:%M:%S') if e['DateTime'] else 'N/A'
        tsunami = ' 🌊' if e['Tsunami'] else ''
        print(f"  M{e['Magnitude']:.1f}  {e['Place']}  ({dt})  depth={e['Depth']}km{tsunami}")

    mags = [e['Magnitude'] for e in events if e['Magnitude'] > 0]
    if mags:
        print(f"\n  震级范围: M{min(mags):.1f} - M{max(mags):.1f}")
    print(f"  M≥6.0: {sum(1 for e in events if e['Magnitude'] >= 6.0)} 次")
    print(f"  M≥7.0: {sum(1 for e in events if e['Magnitude'] >= 7.0)} 次")
    print(f"  含海啸预警: {sum(1 for e in events if e['Tsunami'] > 0)} 次")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='USGS 地震 CSV/API 导入脚本')
    parser.add_argument('--file', '-f', help='USGS CSV 文件路径')
    parser.add_argument('--dir', help='包含多个 CSV 文件的目录路径（批量导入并去重）')
    parser.add_argument('--api', '-a', action='store_true', help='通过 USGS GeoJSON API 拉取数据')
    parser.add_argument('--start-year', type=int, default=2000, help='API 拉取起始年份（默认 2000）')
    parser.add_argument('--end-year', type=int, default=2025, help='API 拉取结束年份（默认 2025）')
    parser.add_argument('--dry-run', '-d', action='store_true', help='只解析不写库')
    args = parser.parse_args()

    if args.api:
        import_csv(api=True, start_year=args.start_year, end_year=args.end_year, dry_run=args.dry_run)
    elif args.dir:
        import_from_dir(args.dir, dry_run=args.dry_run)
    elif args.file:
        import_csv(csv_path=args.file, dry_run=args.dry_run)
    else:
        parser.error("必须指定 --file、--dir 或 --api")
