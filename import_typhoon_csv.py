"""
IBTrACS 台风最佳路径 CSV 数据导入脚本

数据来源：IBTrACS（International Best Track Archive for Climate Stewardship）v04r01
  下载地址：https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/
  推荐文件：IBTrACS.since1980.list.v04r01.csv（西北太平洋区域用 IBTrACS.WP.list.v04r01.csv 更快）

范围约束：太平洋区域，经度 100°E–180°E，纬度 0°–60°N（面向中国沿海及南海台风）
导入内容：TyphoonInfo（台风汇总表）+ TyphoonTrack（路径点表）

CSV 格式说明（IBTrACS v4）：
  - 第1行 = 列名 (header): SID, SEASON, NAME, ISO_TIME, LAT, LON, USA_WIND, WMO_WIND, ...
  - 第2行 = 单位行 (units): 如 "year", "degrees_north", "kts" 等说明文字，非数据
  - 第3行起 = 实际路径点数据，每行一个观测点
  - 共 174 列，按机构（USA/TOKYO/CMA/REUNION/...）分块排列

使用方式：
  python import_typhoon_csv.py --file "IBTrACS.WP.list.v04r01.csv"
  python import_typhoon_csv.py --file ibtracs.csv --dry-run
  python import_typhoon_csv.py --file ibtracs.csv --no-track     # 只导汇总，不导路径点
"""

import csv
import sys
import os
import argparse
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
import pymysql
from config import Config

# ═══════════════════════════════════════════════════════════
# 区域过滤：西北太平洋（中国沿海 + 南海 + 菲律宾海）
# IBTrACS 经度为 0–360°，100–180 覆盖经度 100°E 到 180°E
# ═══════════════════════════════════════════════════════════
LON_MIN, LON_MAX = 100, 180
LAT_MIN, LAT_MAX = 0, 60

# 风暴等级映射（Saffir-Simpson 风速阈值，单位 knots）
def classify_storm(wind_kts):
    if wind_kts <= 0:
        return ''
    if wind_kts < 34:
        return 'TD'       # 热带低压
    elif wind_kts < 64:
        return 'TS'       # 热带风暴
    elif wind_kts < 83:
        return 'C1'       # 一级飓风
    elif wind_kts < 96:
        return 'C2'
    elif wind_kts < 113:
        return 'C3'
    elif wind_kts < 137:
        return 'C4'
    else:
        return 'C5'       # 超强台风


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


def in_region(lat, lon):
    return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX


def _is_units_row(row):
    """检测是否为 IBTrACS 的单位说明行（第2行: degrees_north, kts 等）"""
    sid = (row.get('SID') or '').strip()
    if not sid or len(sid) < 5:
        return True
    # 单位行可能把 SID 写成 "SID" 或其他元数据
    if sid.lower() in ('sid', 'year', 'storm'):
        return True
    # 单位行 LAT 字段为 "degrees_north"
    lat_val = (row.get('LAT') or '').strip()
    if not lat_val.replace('.', '').replace('-', '').isdigit():
        return True
    return False


def import_csv(csv_path, dry_run=False, no_track=False):
    """主导入流程"""
    tracks_by_sid = defaultdict(list)
    total_rows, skip_region, skip_units, skip_err = 0, 0, 0, 0

    print(f"\n[读取] {csv_path}")
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            if total_rows % 100000 == 0:
                print(f"  已读取 {total_rows} 行...")

            # 跳过单位说明行（第2行）
            if total_rows == 1 and _is_units_row(row):
                skip_units += 1
                continue

            try:
                sid = row.get('SID', '').strip()
                if not sid:
                    skip_units += 1
                    continue

                lat = parse_float(row.get('LAT'))
                lon = parse_float(row.get('LON'))
                if not in_region(lat, lon):
                    skip_region += 1
                    continue

                # 时间解析（IBTrACS ISO_TIME 格式 "1984-01-01 00:00:00"）
                iso_time = (row.get('ISO_TIME') or '').strip()
                dt = datetime.strptime(iso_time, '%Y-%m-%d %H:%M:%S') if iso_time else None

                # 风速/气压：逐个机构尝试，取第一个有效值（>0），空值跳过
                # IBTrACS 空值存为 ""，parse_float 返回 0，0 被跳过继续下一个机构
                wind = (parse_float(row.get('USA_WIND'))
                        or parse_float(row.get('WMO_WIND'))
                        or parse_float(row.get('TOKYO_WIND'))
                        or parse_float(row.get('CMA_WIND')))
                # 气压不能用 or 链：USA_PRES 为空时 parse_float 返回默认值 9999（truthy），
                # or 短路导致 WMO/TOKYO/CMA 数据永远读不到 → 改为逐一判断是否 >0
                pres = 9999
                for src in ('USA_PRES', 'WMO_PRES', 'TOKYO_PRES', 'CMA_PRES'):
                    v = (row.get(src) or '').strip()
                    if v:
                        pres = parse_float(v, 9999)
                        if 0 < pres < 9999:
                            break
                        pres = 9999  # 解析失败，重置哨兵值

                # 风圈半径：USA 机构（JTWC）的 34kt/50kt 四象限数据，单位海里
                # 回退到 REUNION/TOKYO 等其他有风圈数据的机构
                r34_ne = parse_float(row.get('USA_R34_NE') or row.get('REUNION_R34_NE'))
                r34_se = parse_float(row.get('USA_R34_SE') or row.get('REUNION_R34_SE'))
                r34_sw = parse_float(row.get('USA_R34_SW') or row.get('REUNION_R34_SW'))
                r34_nw = parse_float(row.get('USA_R34_NW') or row.get('REUNION_R34_NW'))
                r50_ne = parse_float(row.get('USA_R50_NE') or row.get('REUNION_R50_NE'))
                r50_se = parse_float(row.get('USA_R50_SE') or row.get('REUNION_R50_SE'))
                r50_sw = parse_float(row.get('USA_R50_SW') or row.get('REUNION_R50_SW'))
                r50_nw = parse_float(row.get('USA_R50_NW') or row.get('REUNION_R50_NW'))

                tracks_by_sid[sid].append({
                    'datetime': dt,
                    'latitude': lat,
                    'longitude': lon,
                    'wind': wind,
                    'pres': pres,
                    'r34_ne': r34_ne, 'r34_se': r34_se, 'r34_sw': r34_sw, 'r34_nw': r34_nw,
                    'r50_ne': r50_ne, 'r50_se': r50_se, 'r50_sw': r50_sw, 'r50_nw': r50_nw,
                })
            except Exception:
                skip_err += 1
                continue

    print(f"  总行数: {total_rows}, 跳过(单位行): {skip_units}, 跳过(不在区域): {skip_region}, 解析错误: {skip_err}")
    print(f"  区域内风暴数: {len(tracks_by_sid)}, 路径点总数: {sum(len(v) for v in tracks_by_sid.values())}")

    if dry_run:
        _dry_run_preview(tracks_by_sid)
        return

    # ═══════════════════════════════════════════════
    # 写入数据库
    # ═══════════════════════════════════════════════
    conn = pymysql.connect(**Config.DB_CONFIG)
    cur = conn.cursor()

    print("[清理] 删除旧台风数据...")
    cur.execute("DELETE FROM TyphoonAIAnalysis")
    cur.execute("DELETE FROM TyphoonTrack")
    cur.execute("DELETE FROM TyphoonInfo")
    conn.commit()

    # 重新遍历 CSV 提取元数据（NAME/SEASON/BASIN，这些是每个 SID 不变的字段）
    print("[解析] 读取元数据（NAME/SEASON/BASIN）...")
    sid_meta = {}
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            row_count += 1
            if row_count == 1 and _is_units_row(row):
                continue
            sid = row.get('SID', '').strip()
            if sid and sid not in sid_meta and sid in tracks_by_sid:
                sid_meta[sid] = {
                    'name': row.get('NAME', '').strip() or sid,
                    'season': parse_int(row.get('SEASON'), 0),
                    'basin': row.get('BASIN', 'WP').strip(),
                }

    info_sql = """
        INSERT INTO TyphoonInfo
        (TyphoonID, TyphoonName, Season, Basin, MaxWind, MinPressure,
         TotalPoints, StartTime, EndTime)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    track_sql = """
        INSERT INTO TyphoonTrack
        (TyphoonID, DateTime, Latitude, Longitude, MaxSustainedWind, MinPressure,
         StormCategory, WindRadius7NE, WindRadius7SE, WindRadius7SW, WindRadius7NW,
         WindRadius10NE, WindRadius10SE, WindRadius10SW, WindRadius10NW)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    typhoon_count, track_count = 0, 0
    five_min = datetime.min

    for sid, points in tracks_by_sid.items():
        # 按时间排序，过滤掉无时间的点
        points.sort(key=lambda p: p['datetime'] or five_min)

        # 汇总 TyphoonInfo
        max_wind = max(p['wind'] for p in points)
        # MinPressure 空值存 NULL（数据库中可 NULL），而非 9999
        valid_pres = [p['pres'] for p in points if p['pres'] < 9999]
        min_pres = min(valid_pres) if valid_pres else None
        start_time = points[0]['datetime']
        end_time = points[-1]['datetime']
        meta = sid_meta.get(sid, {'name': sid, 'season': 0, 'basin': 'WP'})

        cur.execute(info_sql, (
            sid, meta['name'], meta['season'], meta['basin'],
            max_wind, min_pres, len(points), start_time, end_time,
        ))
        typhoon_count += 1

        if not no_track:
            batch = []
            for p in points:
                if p['datetime'] is None:
                    continue
                batch.append((
                    sid, p['datetime'], p['latitude'], p['longitude'],
                    p['wind'], p['pres'] if p['pres'] < 9999 else None,
                    classify_storm(p['wind']),
                    p['r34_ne'], p['r34_se'], p['r34_sw'], p['r34_nw'],
                    p['r50_ne'], p['r50_se'], p['r50_sw'], p['r50_nw'],
                ))
                track_count += 1
                if len(batch) >= 1000:
                    cur.executemany(track_sql, batch)
                    conn.commit()
                    batch = []
            if batch:
                cur.executemany(track_sql, batch)
                conn.commit()

        if typhoon_count % 100 == 0:
            print(f"  已导入 {typhoon_count} 个台风...")

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM TyphoonInfo")
    info_cnt = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM TyphoonTrack")
    track_cnt = cur.fetchone()[0]

    print(f"\n[完成] TyphoonInfo: {info_cnt} 条, TyphoonTrack: {track_cnt} 条")
    cur.close()
    conn.close()


def _dry_run_preview(tracks_by_sid):
    """预览前 5 个风暴的基本信息"""
    print("\n[Dry Run] 预览前 5 个风暴:")
    for i, (sid, points) in enumerate(list(tracks_by_sid.items())[:5]):
        points.sort(key=lambda p: p['datetime'] or datetime.min)
        max_w = max(p['wind'] for p in points)
        print(f"  {sid}  {points[0]['datetime']} ~ {points[-1]['datetime']}  "
              f"最大风速 {max_w}kts  路径点 {len(points)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IBTrACS 台风 CSV 导入脚本')
    parser.add_argument('--file', '-f', required=True, help='IBTrACS CSV 文件路径')
    parser.add_argument('--dry-run', '-d', action='store_true', help='只解析不写库')
    parser.add_argument('--no-track', action='store_true', help='只导入 TyphoonInfo，跳过路径点')
    args = parser.parse_args()
    import_csv(args.file, dry_run=args.dry_run, no_track=args.no_track)
