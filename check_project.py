#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目状态检查脚本
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("Python版本检查...")
    version = sys.version_info
    print(f"当前版本: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[FAIL] Python版本过低，需要3.8或更高版本")
        return False
    else:
        print("[OK] Python版本符合要求")
        return True

def check_dependencies():
    """检查依赖库"""
    print("\n依赖库检查...")

    required_libs = {
        'playwright': '网页自动化',
        'Pillow': 'PDF生成',
        'requests': 'HTTP请求'
    }

    all_ok = True
    for lib, desc in required_libs.items():
        try:
            if lib == 'Pillow':
                import PIL
                version = PIL.__version__
            else:
                module = importlib.import_module(lib)
                version = getattr(module, '__version__', '未知')
            print(f"[OK] {lib} ({desc}): {version}")
        except ImportError:
            print(f"[FAIL] {lib} ({desc}): 未安装")
            all_ok = False

    return all_ok

def check_browser():
    """检查浏览器"""
    print("\n浏览器检查...")
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            try:
                browser = p.chromium
                print("[OK] Chromium浏览器: 已安装")
                return True
            except Exception as e:
                print(f"[FAIL] Chromium浏览器: {e}")
                return False
    except ImportError:
        print("[FAIL] Playwright未安装，无法检查浏览器")
        return False

def check_project_structure():
    """检查项目结构"""
    print("\n项目结构检查...")

    required_files = [
        'start_enhanced_extractor.py',
        'run_extractor.bat',
        'requirements.txt',
        'config.json',
        'utils/config.py',
        'utils/logger.py',
        '工具脚本/enhanced_extractor.py'
    ]

    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path}: 缺失")
            all_ok = False

    return all_ok

def check_directories():
    """检查目录权限"""
    print("\n目录权限检查...")

    dirs_to_check = ['logs', 'docs']
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        try:
            dir_path.mkdir(exist_ok=True)
            print(f"[OK] {dir_name}/ 目录可创建")
        except Exception as e:
            print(f"[FAIL] {dir_name}/ 目录创建失败: {e}")
            return False

    # 检查输出目录创建权限
    try:
        test_dir = Path("test_output_check")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test.txt"
        test_file.write_text("test", encoding='utf-8')
        test_file.unlink()
        test_dir.rmdir()
        print("[OK] 输出目录权限正常")
    except Exception as e:
        print(f"[FAIL] 输出目录权限异常: {e}")
        return False

    return True

def check_recent_outputs():
    """检查最近的输出结果"""
    print("\n最近输出检查...")

    # 检查提取结果目录
    output_dirs = [d for d in Path('.').iterdir() if d.is_dir() and d.name.startswith('提取结果_')]
    if output_dirs:
        latest_dir = max(output_dirs, key=lambda x: x.stat().st_ctime)
        print(f"[OK] 最新输出目录: {latest_dir.name}")

        # 检查PDF文件
        pdf_files = list(latest_dir.glob("*.pdf"))
        if pdf_files:
            pdf_file = pdf_files[0]
            size = pdf_file.stat().st_size
            print(f"[OK] PDF文件: {pdf_file.name} ({size:,} bytes)")
        else:
            print("[WARNING] 未找到PDF文件")

        # 检查图片文件
        png_files = list(latest_dir.glob("*.png"))
        print(f"[OK] PNG图片: {len(png_files)} 个")
    else:
        print("[WARNING] 未找到输出目录")

def main():
    """主检查函数"""
    print("=" * 50)
    print("增强版文档提取器 - 项目状态检查")
    print("=" * 50)

    results = []

    # 第一阶段：结构检查
    print("\n" + "=" * 20 + " 第一阶段：结构检查 " + "=" * 20)
    results.append(("项目结构", check_project_structure()))
    results.append(("目录权限", check_directories()))

    # 第二阶段：环境检测
    print("\n" + "=" * 20 + " 第二阶段：环境检测 " + "=" * 20)
    results.append(("Python版本", check_python_version()))
    results.append(("依赖库", check_dependencies()))
    results.append(("浏览器", check_browser()))

    # 显示检查结果
    print("\n" + "=" * 50)
    print("检查结果汇总")
    print("=" * 50)

    passed = 0
    total = len(results)

    # 按阶段显示结果
    print("\n[结构检查]")
    structure_results = [r for r in results if r[0] in ["项目结构", "目录权限"]]
    for check_name, result in structure_results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"  {check_name:12} {status}")
        if result:
            passed += 1

    print("\n[环境检测]")
    environment_results = [r for r in results if r[0] in ["Python版本", "依赖库", "浏览器"]]
    for check_name, result in environment_results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"  {check_name:12} {status}")
        if result:
            passed += 1

    print(f"\n总体结果: {passed}/{total} 项检查通过")

    if passed == total:
        print("[SUCCESS] 项目状态良好，可以正常运行！")
    else:
        print("[WARNING] 发现问题，请根据上述提示修复")

        print("\n[INFO] 修复建议:")
        # 找到环境检测中的失败项
        env_failed = [r[0] for r in environment_results if not r[1]]
        if "依赖库" in env_failed:
            print("  安装依赖: pip install -r requirements.txt")
        if "浏览器" in env_failed:
            print("  安装浏览器: python -m playwright install chromium")

    # 检查最近输出
    check_recent_outputs()

    print("\n" + "=" * 50)
    print("结构检查 -- 完成！")

    return passed == total

if __name__ == "__main__":
    try:
        success = main()
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
    except Exception as e:
        print(f"\n\n检查过程中发生错误: {e}")