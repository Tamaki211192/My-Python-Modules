import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os
import sys


# 全局保存：最近一次纯文本结果（用于复制/导出）
last_output_text = ""


def resource_path(rel: str) -> str:
    """
    兼容开发环境 & PyInstaller 打包环境
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    return os.path.join(base_dir, rel)


def collect_matches(base_dir: Path, keyword: str, pattern: str):
    """
    返回:
    total_hits: int
    matched_files: list[(file_name, hit_count)]
    line_results: list[(file_name, line_no, line_text)]
    error_msgs: list[str]
    """
    try:
        md_files = sorted(base_dir.glob(pattern))
    except Exception as e:
        return 0, [], [], [f"[错误] 文件模式无效: {pattern} ({e})"]

    total_hits = 0
    kw_lower = keyword.lower()

    matched_files = []
    line_results = []
    error_msgs = []

    for file_path in md_files:
        if not file_path.is_file():
            continue

        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            error_msgs.append(f"[跳过] 读取失败：{file_path.name} ({e})")
            continue

        file_hit_count = 0

        for line_no, line in enumerate(lines, start=1):
            if kw_lower in line.lower():
                total_hits += 1
                file_hit_count += 1
                line_results.append((file_path.name, line_no, line))

        if file_hit_count > 0:
            matched_files.append((file_path.name, file_hit_count))

    return total_hits, matched_files, line_results, error_msgs


def choose_dir():
    folder = filedialog.askdirectory()
    if folder:
        dir_var.set(folder)


def append_text(text: str):
    output_box.insert(tk.END, text)


def highlight_keyword_in_output(keyword: str):
    """
    在 Text 组件中高亮所有关键词（不区分大小写）
    """
    output_box.tag_remove("kw_highlight", "1.0", tk.END)

    if not keyword.strip():
        return

    key_lower = keyword.lower()
    all_text = output_box.get("1.0", tk.END)
    search_from = 0

    while True:
        idx = all_text.lower().find(key_lower, search_from)
        if idx == -1:
            break

        start_index = f"1.0+{idx}c"
        end_index = f"1.0+{idx + len(keyword)}c"
        output_box.tag_add("kw_highlight", start_index, end_index)

        search_from = idx + len(keyword)

    output_box.tag_config("kw_highlight", background="#fff59d", foreground="#000000")


def build_output_text(keyword, base_dir, files_only, total_hits, matched_files, line_results, error_msgs):
    """
    组装纯文本输出，供显示/复制/导出统一复用
    """
    parts = []
    parts.append(f"关键词: {keyword}")
    parts.append(f"目录: {base_dir}")
    parts.append("")

    if error_msgs:
        parts.extend(error_msgs)
        parts.append("")

    if total_hits == 0:
        parts.append(f"[结果] 没有找到关键词：{keyword}")
        return "\n".join(parts)

    if files_only:
        parts.append("[命中文件]")
        for file_name, _ in matched_files:
            parts.append(file_name)
    else:
        parts.append("[命中行]")
        for file_name, line_no, line in line_results:
            parts.append(f"{file_name}:{line_no} | {line}")

    parts.append("")
    parts.append("[每个文件命中次数]")
    for file_name, count in matched_files:
        parts.append(f"{file_name}: {count}")

    parts.append("")
    parts.append(f"[完成] 共命中 {total_hits} 行")

    return "\n".join(parts)


def run_search():
    global last_output_text

    output_box.delete("1.0", tk.END)

    # 去掉你之前可能粘进去的双引号
    dir_text = dir_var.get().strip().strip('"')
    keyword = kw_var.get().strip()
    pattern = pattern_var.get().strip()
    files_only = files_only_var.get()

    if not dir_text:
        messagebox.showwarning("提示", "请先输入或选择目录")
        return
    if not keyword:
        messagebox.showwarning("提示", "请输入关键词")
        return
    if not pattern:
        messagebox.showwarning("提示", "请输入文件名模式（例如 day*.md）")
        return

    base_dir = Path(dir_text)

    # 如果用户误填了文件路径，自动切到父目录
    if base_dir.exists() and base_dir.is_file():
        base_dir = base_dir.parent

    if not base_dir.exists():
        messagebox.showerror("错误", f"目录不存在：\n{base_dir}")
        return
    if not base_dir.is_dir():
        messagebox.showerror("错误", f"这不是目录：\n{base_dir}")
        return

    total_hits, matched_files, line_results, error_msgs = collect_matches(base_dir, keyword, pattern)

    last_output_text = build_output_text(
        keyword=keyword,
        base_dir=base_dir,
        files_only=files_only,
        total_hits=total_hits,
        matched_files=matched_files,
        line_results=line_results,
        error_msgs=error_msgs
    )

    append_text(last_output_text)
    highlight_keyword_in_output(keyword)


def copy_output():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("提示", "当前没有可复制的结果")
        return

    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    messagebox.showinfo("完成", "结果已复制到剪贴板")


def export_output():
    global last_output_text

    text = last_output_text.strip()
    if not text:
        messagebox.showinfo("提示", "当前没有可导出的结果，请先搜索")
        return

    default_name = f"search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    file_path = filedialog.asksaveasfilename(
        title="导出搜索结果",
        defaultextension=".txt",
        initialfile=default_name,
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    if not file_path:
        return

    try:
        Path(file_path).write_text(text, encoding="utf-8")
        messagebox.showinfo("完成", f"导出成功：\n{file_path}")
    except Exception as e:
        messagebox.showerror("错误", f"导出失败：{e}")


# ===== GUI =====
root = tk.Tk()
root.title("日志关键词检索器（最终版）")
root.geometry("1100x720")
root.minsize(900, 560)

# 窗口图标（开发环境有 app.ico 就显示；没有也不崩）
try:
    ico_path = resource_path("app.ico")
    if os.path.exists(ico_path):
        root.iconbitmap(ico_path)
except Exception:
    pass

#
# 背景图层
bg_label = tk.Label(root)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
bg_label.lower()   # 放到最底层


def refresh_bg():
    global _bg_imgtk
    if _bg_pil is None:
        return
    w = max(root.winfo_width(), 1)
    h = max(root.winfo_height(), 1)

    img = _bg_pil.resize((w, h), Image.LANCZOS)

    # 关键：做“伪半透明”效果
    img = img.filter(ImageFilter.GaussianBlur(radius=3))      # 轻微模糊
    img = ImageEnhance.Brightness(img).enhance(1.10)          # 稍微提亮
    img = ImageEnhance.Color(img).enhance(0.85)               # 略降饱和，减少花哨

    _bg_imgtk = ImageTk.PhotoImage(img)
    bg_label.configure(image=_bg_imgtk)


# 你给的背景图路径
bg_path = r"D:\PycharmProjects\My Python Modules\bg.jpg"
if os.path.exists(bg_path):
    try:
        _bg_pil = Image.open(bg_path).convert("RGB")
        refresh_bg()
    except Exception:
        pass

root.bind("<Configure>", lambda e: refresh_bg() if e.widget == root else None)

# 前景主容器（不要纯白）
main = tk.Frame(root, bg="#f0f0f0")   # 这里别用 #FFFFFF
main.place(x=40, y=40, relwidth=0.93, relheight=0.90)

# 顶部输入区域
top_frame = tk.Frame(main, bg="#F7F9FC")
top_frame.pack(fill="x", padx=12, pady=10)

dir_var = tk.StringVar(value=r"D:\PycharmProjects\summer-30day-python-learn-log\daily")
kw_var = tk.StringVar(value="set")
pattern_var = tk.StringVar(value="day*.md")
files_only_var = tk.BooleanVar(value=False)

tk.Label(top_frame, text="日志目录:", bg="#F7F9FC").grid(row=0, column=0, sticky="w")
tk.Entry(top_frame, textvariable=dir_var, width=92).grid(row=0, column=1, padx=8, sticky="w")
tk.Button(top_frame, text="选择目录", command=choose_dir).grid(row=0, column=2, padx=6)

tk.Label(top_frame, text="关键词:", bg="#F7F9FC").grid(row=1, column=0, sticky="w", pady=8)
tk.Entry(top_frame, textvariable=kw_var, width=25).grid(row=1, column=1, sticky="w", padx=8, pady=8)

tk.Label(top_frame, text="文件模式:", bg="#F7F9FC").grid(row=2, column=0, sticky="w")
tk.Entry(top_frame, textvariable=pattern_var, width=25).grid(row=2, column=1, sticky="w", padx=8)
tk.Label(top_frame, text='例如: day*.md / *.md / *.txt', fg="gray", bg="#F7F9FC").grid(row=2, column=1, padx=190, sticky="w")

tk.Checkbutton(
    top_frame,
    text="仅显示命中文件名（files-only）",
    variable=files_only_var,
    bg="#F7F9FC"
).grid(row=1, column=1, padx=230, sticky="w")

# 按钮区
btn_frame = tk.Frame(main, bg="#F7F9FC")
btn_frame.pack(fill="x", padx=12, pady=4)

tk.Button(btn_frame, text="开始搜索", command=run_search, width=12).pack(side="left", padx=4)
tk.Button(btn_frame, text="复制结果", command=copy_output, width=12).pack(side="left", padx=4)
tk.Button(btn_frame, text="导出结果到TXT", command=export_output, width=14).pack(side="left", padx=4)

# 输出区（不要纯白，避免整块遮挡）
output_box = tk.Text(main, wrap="word", font=("Consolas", 11), bg="#f7f7f7")
output_box.pack(fill="both", expand=True, padx=12, pady=10)

root.mainloop()