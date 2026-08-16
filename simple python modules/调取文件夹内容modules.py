# pathlib 文件夹/目录操作模块
'''
from pathlib import Path

p = Path("daily")                  # 创建路径对象
p.exists()                         # 是否存在
p.is_dir()                         # 是否目录
files = p.glob("day*.md")          # 按模式找文件
text = Path("a.txt").read_text(encoding="utf-8")   # 读文本
Path("a.txt").write_text("hello", encoding="utf-8") # 写文本
'''
import argparse
from pathlib import Path


def search_keyword(base_dir: Path, keyword: str) -> int:    # 这里的str -> int只是一种方便看懂的写法
    """
    在 base_dir 下搜索 day*.md 中包含 keyword 的行。
    返回命中总行数。
    """
    md_files = sorted(base_dir.glob("day*.md"))
    # 这里的p.glob是按照通配符匹配该项目下的文件
    # sort是一个python内置的排列方式，是给括号内的变量进行排序，比如day01,day03,day02会按照从小到大的方式排序
    # 不同的是sorted不会改变原来的变量，sort会改变。
    if not md_files:
        # 当md_files中没有内容时，就会变成false,if not md_files就会等价于if ture开始执行
        print(f"[提示] 在目录 {base_dir} 下没有找到 day*.md 文件")
        return 0

    hit_count = 0
    kw_lower = keyword.lower()

    for file_path in md_files:
        # 打开md_files中的每一个路径file_path去执行如下的内容
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            print(f"[跳过] 读取失败：{file_path.name} ({e})")
            continue

        for line_no, line in enumerate(lines, start=1):
            # enumerate 相当于对于lines这个装着字符串的表格，在用line去遍历的同时用line_no去标注在第几行。
            if kw_lower in line.lower():
                # 当检测到keyword在line中存在的时候，视为找到
                if hit_count == 0:
                    print(f"关键词: {keyword}\n")
                print(f"{file_path.name}:{line_no} | {line}")
                hit_count += 1

    return hit_count


def main():
    parser = argparse.ArgumentParser(
        description="在 day*.md 学习日志中搜索关键词"
    )
    # 这里的argparse.ArgumentParser是创造解析器对象，description是对这个解析器的以用途说明
    parser.add_argument("--kw", required=True, help="要搜索的关键词，例如 set")
    # .add_argument是通用的方法名，根据方法名括号内的内容不同决定了它不同的作用，这里是设置必要的参数--kw,这里的required = Ture是指必须要有参数
    parser.add_argument(
        "--dir",
        default=r"D:\PycharmProjects\summer-30day-python-learn-log\daily",
        help="日志目录，默认是你的 daily 绝对路径"
    )
    # 这里的add_argument括号内接的词是--dir，但是跟上面相比没有required = True，所以这里的参数不是必要的，所以设置了default 这个默认值。
    args = parser.parse_args()
    # 这里的parser.parse_args()联系前面设置的必要参数和非必要参数，作用是调用输入的两个参数
    base_dir = Path(args.dir)
    # 这里依旧是创造路径对象
    if not base_dir.exists():
        print(f"[错误] 目录不存在：{base_dir}")
        return
    if not base_dir.is_dir():
        print(f"[错误] 这不是目录：{base_dir}")
        return

    total = search_keyword(base_dir, args.kw)
    if total == 0:
        print(f"[结果] 没有找到关键词：{args.kw}")
    else:
        print(f"\n[完成] 共命中 {total} 行")


if __name__ == "__main__":
    main()


# python "D:\PycharmProjects\summer-30day-python-learn-log\practice\day09_log_search.py" --kw set --dir "D:\PycharmProjects\summer-30day-python-learn-log\daily"





