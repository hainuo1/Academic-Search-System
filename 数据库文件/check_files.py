#!/usr/bin/env python3
"""批量处理 DB 文件编码修复脚本"""
import glob, os, sys

db_dir = r'C:\Users\hainuo\Desktop\检索系统\6.1版本\数据库文件'

# 检查所有 .sql 文件编码
for sql_file in glob.glob(os.path.join(db_dir, '*.sql')):
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            f.read(100)
        print(f'[OK] {os.path.basename(sql_file)}')
    except UnicodeDecodeError:
        print(f'[ERROR] {os.path.basename(sql_file)} - encoding issue')
