# -*- coding: utf-8 -*-
"""
增强版文档提取器启动脚本
提供简化的启动接口和配置选项
"""

import sys
import os
import argparse
from pathlib import Path

# 修复Windows控制台编码问题
def setup_console_encoding():
    """设置控制台编码，避免闪退"""
    if sys.platform == 'win32':
        try:
            # 设置控制台编码为UTF-8
            os.system('chcp 65001 >nul 2>&1')

            # 尝试替换stdout以支持UTF-8，如果失败则忽略
            try:
                import codecs
                sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
                sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
            except:
                pass

        except Exception as e:
            # 如果编码设置失败，继续运行但记录警告
            print(f"Warning: Console encoding setup failed: {e}")

# 设置控制台编码
setup_console_encoding()

# 添加项目根目录到Python路径
try:
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # 尝试导入提取器，如果失败则提供友好的错误信息
    from 工具脚本.enhanced_extractor import EnhancedDocumentExtractor
except ImportError as e:
    print(f"Error: Cannot import EnhancedDocumentExtractor: {e}")
    print("Please ensure the '工具脚本' directory exists and contains enhanced_extractor.py")
    input("Press Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"Error: Failed to initialize the extractor: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

def safe_input(prompt=""):
    """安全的输入函数，处理批处理环境"""
    try:
        return input(prompt)
    except EOFError:
        # 如果是EOF错误（批处理环境），提供特殊处理
        print("检测到批处理环境，请使用 --url 参数提供URL")
        print("使用示例: python start_enhanced_extractor.py --url \"https://example.com\"")
        return None
    except KeyboardInterrupt:
        print("\n")
        return None

def get_url_interactive():
    """交互式获取URL输入"""
    print("=" * 60)
    print("使用方法:")
    print("  • 根据提示输入网址")
    print("  • 等待程序启动打开网页")
    print("  • 点击网页顶部放大按钮，文件放大到最大")
    print("  • 下拉网页，直到‘继续阅读全文’按钮出现")
    print("  • 滑动或点击按钮，加载全部文件内容，等待程序自动提取")
    print("=" * 60)

    print("\n请输入要提取的文档URL:")
    print("格式示例: https://www.doc88.com/p-74287148231067.html")

    while True:
        url = safe_input("URL: ")
        if url is None:
            return None

        url = url.strip()
        if not url:
            print("错误: URL不能为空，请重新输入")
            continue

        # 简单的URL格式验证
        if not (url.startswith('http://') or url.startswith('https://')):
            print("错误: URL必须以http://或https://开头")
            continue

        if 'doc88.com' not in url:
            print("警告: 当前工具主要支持doc88.com的文档")
            confirm = safe_input("是否继续? (y/n): ")
            if confirm is None:
                return None
            if confirm.strip().lower() != 'y':
                continue

        return url

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="增强版文档提取器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python start_enhanced_extractor.py --url "https://example.com"                    # 基本使用
  python start_enhanced_extractor.py --url "https://example.com" --headless        # 无头模式
  python start_enhanced_extractor.py --url "https://example.com" --debug           # 调试模式
  python start_enhanced_extractor.py                                             # 交互式输入URL
        """
    )

    parser.add_argument(
        '--url',
        type=str,
        required=False,
        help='目标文档URL (如果不提供，将交互式输入)'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='无头模式运行 (不显示浏览器界面)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别 (默认: INFO)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        help='自定义输出目录'
    )

    return parser.parse_args()

async def main():
    """主函数"""
    # 显示标题
    print("增强版文档提取器")
    print("=" * 60)

    # 解析参数
    args = parse_arguments()

    # 获取URL
    url = args.url
    if not url:
        url = get_url_interactive()
        if not url:
            print("未提供有效的URL，程序退出")
            print("请使用 --url 参数提供有效的URL地址")
            return

    # 显示启动信息
    print(f"\n目标URL: {url}")
    print(f"运行模式: {'无头模式' if args.headless else '有头模式'}")
    print(f"日志级别: {args.log_level}")
    if args.debug:
        print("调试模式: 已启用")
    if args.config:
        print(f"配置文件: {args.config}")
    print("=" * 60)

    try:
        # 创建提取器
        extractor = EnhancedDocumentExtractor(config_file=args.config)

        # 应用命令行参数
        if args.headless:
            extractor.browser_config.headless = True
            print("已启用无头模式")

        if args.debug:
            extractor.config_manager.config.debug_mode = True
            extractor.logger.set_level('DEBUG')
            print("已启用调试模式")

        if args.log_level != 'INFO':
            extractor.logger.set_level(args.log_level)
            print(f"日志级别已设置为: {args.log_level}")

        if args.output_dir:
            extractor.config_manager.config.output_base_dir = args.output_dir
            print(f"输出目录已设置为: {args.output_dir}")

        # 运行提取器
        print("\n开始执行文档提取任务...")
        result = await extractor.run(url)

        # 显示最终结果
        print("\n" + "=" * 60, flush=True)
        if result:
            print(f"✅ 任务执行成功！", flush=True)
            print(f"📄 输出文件: {result}", flush=True)
            if extractor.output_dir:
                print(f"📁 输出目录: {extractor.output_dir}", flush=True)
            print(f"\n🎉 文档提取已完成！您可以在上述目录中找到提取的PDF文件。", flush=True)
        else:
            print("❌ 任务执行失败", flush=True)
            print("请查看日志文件了解详细错误信息。", flush=True)
        print("=" * 60, flush=True)

        # 强制刷新输出缓冲区
        import sys
        sys.stdout.flush()
        sys.stderr.flush()

        # 等待用户确认后再退出
        print("\n按任意键退出程序...", flush=True)

        # 添加延时确保提示信息显示
        import time
        time.sleep(0.5)

        try:
            import msvcrt
            print("使用 msvcrt 等待按键...", flush=True)
            msvcrt.getch()  # Windows下等待按键
        except:
            # 如果msvcrt不可用，使用input作为备选
            try:
                print("msvcrt不可用，使用input等待...", flush=True)
                input("按回车键退出...")
            except EOFError:
                # 如果input也失败，等待3秒后自动退出
                print("input不可用，等待3秒后自动退出...", flush=True)
                time.sleep(3)
            except Exception as input_error:
                print(f"input也失败: {input_error}，等待3秒后自动退出...", flush=True)
                time.sleep(3)

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序", flush=True)
        print("提取过程已被用户取消。", flush=True)
        try:
            input("\n按回车键退出...")
        except EOFError:
            import time
            time.sleep(3)
    except Exception as e:
        print(f"\n❌ 程序执行错误: {e}", flush=True)
        print("详细错误信息:", flush=True)
        import traceback
        traceback.print_exc()
        print("\n💡 提示: 请查看上述错误信息，或使用调试模式重新运行。", flush=True)
        try:
            input("\n按回车键退出...")
        except EOFError:
            import time
            time.sleep(3)

if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 程序被用户中断", flush=True)
        try:
            input("按回车键退出...")
        except EOFError:
            import time
            time.sleep(3)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}", flush=True)
        print("详细错误信息:", flush=True)
        import traceback
        traceback.print_exc()
        print("\n💡 提示: 请检查环境配置或查看修复指南文档。", flush=True)
        try:
            input("按回车键退出...")
        except EOFError:
            import time
            time.sleep(3)