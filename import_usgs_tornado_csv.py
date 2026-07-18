"""
NOAA SPC 龙卷风 CSV 数据导入脚本

数据来源：https://www.spc.noaa.gov/wcm/data/1950-2024_actual_tornadoes.csv

SPC 数据是全美龙卷风，不包含中国数据！因此本脚本：
  1. 全量导入美国龙卷风数据（仅作示例，数据库表已就绪）
  2. 如需中国龙卷风数据，请从清华/北大 PKU 开放数据库下载后用类似脚本导入

使用方式：
  python import_usgs_tornado_csv.py --file "龙卷风数据/1950-2024_actual_tornadoes.csv"
  python import_usgs_tornado_csv.py --file tornado.csv --dry-run
"""

import csv
import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
import pymysql
from config import Config

# SPC 数据集 EF 等级映射
MAG_TO_EF = {0: 'EF0', 1: 'EF1', 2: 'EF2', 3: 'EF3', 4: 'EF4', 5: 'EF5'}
# SPC 州代码 → 州名
STATE_NAMES = {
    'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California',
    'CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia',
    'HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas',
    'KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts',
    'MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana',
    'NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico',
    'NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma',
    'OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina',
    'SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont',
    'VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming',
    'DC':'District of Columbia','PR':'Puerto Rico',
}


def parse_float(v, d=0.0):
    try: return float(v)
    except: return d


def parse_int(v, d=0):
    try: return int(float(v))
    except: return d


def import_csv(csv_path, dry_run=False):
    events = []
    total, skip_no_coord, skip_err = 0, 0, 0

    print(f"\n[读取] {csv_path}")
    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            if total % 100000 == 0:
                print(f"  已读取 {total} 行...")

            try:
                slat = parse_float(row.get('slat'))
                slon = parse_float(row.get('slon'))
                if slat == 0 and slon == 0:
                    skip_no_coord += 1
                    continue
                if slon > 180:
                    slon -= 360

                yr = int(row.get('yr', 0))
                mo = int(row.get('mo', 1))
                dy = int(row.get('dy', 1))
                tim = row.get('time', '00:00:00').strip()
                dt_str = f"{yr:04d}-{mo:02d}-{dy:02d} {tim}"
                dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S') if yr > 0 else None

                mag = int(row.get('mag', 0))
                ef = MAG_TO_EF.get(mag, f'EF{mag}')
                st = row.get('st', '').strip()
                st_name = STATE_NAMES.get(st, st)

                events.append({
                    'DateTime':    dt,
                    'Latitude':    slat,
                    'Longitude':   slon,
                    'Place':       f"{st_name}, FIPS:{row.get('stn','')}",
                    'Province':    st_name,
                    'EFScale':     ef,
                    'Magnitude':   mag,
                    'Casualties':  int(row.get('inj', 0)) + int(row.get('fat', 0)),
                    'Deaths':      int(row.get('fat', 0)),
                    'Injuries':    int(row.get('inj', 0)),
                })
            except Exception:
                skip_err += 1
                continue

    print(f"  总行数: {total}, 跳过(无坐标): {skip_no_coord}, 解析错误: {skip_err}, 有效: {len(events)}")

    if dry_run:
        for e in events[:5]:
            print(f"  {e['EFScale']} {e['Place']} ({e['DateTime']}) 伤{e['Injuries']} 亡{e['Deaths']}")
        return

    conn = pymysql.connect(**Config.DB_CONFIG)
    cur = conn.cursor()

    print("[清理] 删除旧数据...")
    cur.execute("DELETE FROM TornadoAIAnalysis")
    cur.execute("DELETE FROM TornadoInfo")
    conn.commit()

    sql = """
        INSERT INTO TornadoInfo
        (DateTime, Latitude, Longitude, Place, Province,
         EFScale, Magnitude, Casualties, Deaths, Injuries)
        VALUES (%(DateTime)s, %(Latitude)s, %(Longitude)s, %(Place)s, %(Province)s,
                %(EFScale)s, %(Magnitude)s, %(Casualties)s, %(Deaths)s, %(Injuries)s)
    """
    batch = []
    for e in events:
        batch.append(e)
        if len(batch) >= 500:
            cur.executemany(sql, batch)
            conn.commit()
            batch = []
    if batch:
        cur.executemany(sql, batch)
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM TornadoInfo")
    print(f"\n[完成] 导入 {len(events)} 条，TornadoInfo 表总记录: {cur.fetchone()[0]}")
    cur.close()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NOAA SPC 龙卷风 CSV 导入脚本')
    parser.add_argument('--file', '-f', required=True, help='SPC CSV 文件路径')
    parser.add_argument('--dry-run', '-d', action='store_true', help='只解析不写库')
    args = parser.parse_args()
    import_csv(args.file, dry_run=args.dry_run)
