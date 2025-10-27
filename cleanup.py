#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def cleanup_project():
    """清理项目"""
    print("文档提取器 - 项目清理")
    print("=" * 40)

    # 清理多余的提取结果目录
    project_root = Path(__file__).parent
    output_dirs = [d for d in project_root.iterdir() if d.is_dir() and d.name.startswith('提取结果_')]

    if output_dirs:
        print(f"发现 {len(output_dirs)} 个提取结果目录:")
        for i, d in enumerate(sorted(output_dirs), 1):
            print(f"  {i}. {d.name} (创建时间: {datetime.fromtimestamp(d.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S')})")

        # 保留最新的2个目录
        if len(output_dirs) > 2:
            print(f"\n将保留最新的2个目录，清理其余 {len(output_dirs) - 2} 个目录...")

            # 按时间排序，删除最旧的
            sorted_dirs = sorted(output_dirs, key=lambda x: x.stat().st_ctime, reverse=True)
            for old_dir in sorted_dirs[2:]:
                try:
                    shutil.rmtree(old_dir)
                    print(f"✅ 已删除: {old_dir.name}")
                except Exception as e:
                    print(f"❌ 删除失败 {old_dir.name}: {e}")
        else:
            print("提取结果目录数量合理，无需清理。")
    else:
        print("未找到提取结果目录。")

    # 清理旧的日志文件
    log_dir = project_root / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            print(f"\n发现 {len(log_files)} 个日志文件:")
            for i, f in enumerate(sorted(log_files), 1):
                print(f"  {i}. {f.name}")

            # 保留最新的5个日志文件
            if len(log_files) > 5:
                print(f"\n将保留最新的5个日志文件，清理其余 {len(log_files) - 5} 个...")

                sorted_files = sorted(log_files, key=lambda x: x.stat().st_ctime, reverse=True)
                for old_file in sorted_files[5:]:
                    try:
                        old_file.unlink()
                        print(f"✅ 已删除: {old_file.name}")
                    except Exception as e:
                        print(f"❌ 删除失败 {old_file.name}: {e}")
            else:
                print("日志文件数量合理，无需清理。")
        else:
            print("未找到日志文件。")

    print("\n清理完成！")

if __name__ == "__main__":
    cleanup_project()