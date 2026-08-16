import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QTextCursor, QTextCharFormat, QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QCheckBox, QHBoxLayout, QVBoxLayout, QGridLayout
)


def resource_path(rel: str) -> str:
    """兼容开发环境 & PyInstaller"""
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
        files = sorted(base_dir.glob(pattern))
    except Exception as e:
        return 0, [], [], [f"[错误] 文件模式无效: {pattern} ({e})"]

    total_hits = 0
    kw_lower = keyword.lower()

    matched_files = []
    line_results = []
    error_msgs = []

    for file_path in files:
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


def build_output_text(keyword, base_dir, files_only, total_hits, matched_files, line_results, error_msgs):
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


class LogSearcherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.last_output_text = ""
        self.theme_mode = "glass"  # light / glass / ultra

        self.setWindowTitle("关键词检索器（Qt版）")
        self.resize(1100, 720)
        self.setMinimumSize(920, 600)

        # 图标
        ico_path = resource_path("app.ico")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        # 背景图
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_pixmap = None
        bg_path = resource_path("bg.jpg")
        if os.path.exists(bg_path):
            self.bg_pixmap = QPixmap(bg_path)

        # 前景容器
        self.panel = QWidget(self)
        self.panel.setObjectName("panel")

        # 控件
        self.dir_edit = QLineEdit(r"")
        self.kw_edit = QLineEdit("")
        self.pattern_edit = QLineEdit("*.md")
        self.files_only_ck = QCheckBox("仅显示命中文件名（files-only）")
        self.hint_label = QLabel("例如: day*.md / *.md / *.txt")
        self.hint_label.setObjectName("hint")

        self.btn_choose = QPushButton("选择目录")
        self.btn_search = QPushButton("开始搜索")
        self.btn_copy = QPushButton("复制结果")
        self.btn_export = QPushButton("导出结果到TXT")
        self.btn_theme = QPushButton("透明度：Glass")

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(False)
        self.output_box.setPlaceholderText("搜索结果将显示在这里...")

        self._build_layout()
        self._bind_events()
        self._apply_style()

    def _build_layout(self):
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        # 第0行：目录
        grid.addWidget(QLabel("日志目录:"), 0, 0)
        grid.addWidget(self.dir_edit, 0, 1, 1, 2)
        grid.addWidget(self.btn_choose, 0, 3)

        # 第1行：关键词 + files-only
        grid.addWidget(QLabel("关键词:"), 1, 0)
        grid.addWidget(self.kw_edit, 1, 1)

        row1_right = QHBoxLayout()
        row1_right.setContentsMargins(0, 0, 0, 0)
        row1_right.setSpacing(8)
        row1_right.addWidget(self.files_only_ck)
        row1_right.addStretch(1)
        grid.addLayout(row1_right, 1, 2, 1, 2)

        # 第2行：文件模式 + 示例
        grid.addWidget(QLabel("文件模式:"), 2, 0)
        grid.addWidget(self.pattern_edit, 2, 1)

        row2_right = QHBoxLayout()
        row2_right.setContentsMargins(0, 0, 0, 0)
        row2_right.setSpacing(8)
        row2_right.addWidget(self.hint_label)
        row2_right.addStretch(1)
        grid.addLayout(row2_right, 2, 2, 1, 2)

        # 列伸缩
        grid.setColumnStretch(0, 0)  # 标签
        grid.setColumnStretch(1, 3)  # 输入框
        grid.setColumnStretch(2, 2)  # 右侧说明
        grid.setColumnStretch(3, 0)  # 按钮

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_search)
        btn_row.addWidget(self.btn_copy)
        btn_row.addWidget(self.btn_export)
        btn_row.addWidget(self.btn_theme)
        btn_row.addStretch(1)

        main_layout = QVBoxLayout(self.panel)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)
        main_layout.addLayout(grid)
        main_layout.addLayout(btn_row)
        main_layout.addWidget(self.output_box, 1)

        # 外层布局：让 panel 填满窗口
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(0)
        outer.addWidget(self.panel, 1)

    def _bind_events(self):
        self.btn_choose.clicked.connect(self.choose_dir)
        self.btn_search.clicked.connect(self.run_search)
        self.btn_copy.clicked.connect(self.copy_output)
        self.btn_export.clicked.connect(self.export_output)
        self.btn_theme.clicked.connect(self.cycle_theme)

    def _apply_style(self):
        themes = {
            "light": {
                "panel": 205,
                "input": 220,
                "button": 210,
                "button_hover": 225,
                "button_press": 235,
                "border": 150,
                "hint": "#64748b",
                "btn_text": "透明度：Light",
            },
            "glass": {
                "panel": 130,
                "input": 120,
                "button": 155,
                "button_hover": 180,
                "button_press": 195,
                "border": 140,
                "hint": "#475569",
                "btn_text": "透明度：Glass",
            },
            "ultra": {
                "panel": 90,
                "input": 85,
                "button": 120,
                "button_hover": 150,
                "button_press": 170,
                "border": 130,
                "hint": "#334155",
                "btn_text": "透明度：Ultra",
            },
        }

        t = themes.get(self.theme_mode, themes["glass"])

        self.setStyleSheet(f"""
            QWidget {{
                font-family: "Microsoft YaHei UI", "Segoe UI";
                font-size: 14px;
                color: #1f2937;
            }}

            #panel {{
                background-color: rgba(248, 250, 252, {t["panel"]});
                border: 1px solid rgba(148, 163, 184, {t["border"]});
                border-radius: 12px;
            }}

            QLineEdit, QTextEdit {{
                background: rgba(255, 255, 255, {t["input"]});
                border: 1px solid rgba(203, 213, 225, {t["border"]});
                border-radius: 8px;
                padding: 8px;
                selection-background-color: #93c5fd;
            }}

            QPushButton {{
                background: rgba(226, 232, 240, {t["button"]});
                border: 1px solid rgba(203, 213, 225, {t["border"]});
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: rgba(219, 234, 254, {t["button_hover"]});
            }}
            QPushButton:pressed {{
                background: rgba(191, 219, 254, {t["button_press"]});
            }}

            QCheckBox {{
                spacing: 6px;
            }}

            QLabel#hint {{
                color: {t["hint"]};
            }}
        """)

        self.btn_theme.setText(t["btn_text"])

    def cycle_theme(self):
        order = ["light", "glass", "ultra"]
        i = order.index(self.theme_mode)
        self.theme_mode = order[(i + 1) % len(order)]
        self._apply_style()

    def set_theme(self, mode: str):
        if mode in ("light", "glass", "ultra"):
            self.theme_mode = mode
            self._apply_style()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_label.setGeometry(self.rect())
        if self.bg_pixmap:
            scaled = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled)
        self.bg_label.lower()

    def choose_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "选择目录")
        if folder:
            self.dir_edit.setText(folder)

    def run_search(self):
        self.output_box.clear()

        dir_text = self.dir_edit.text().strip().strip('"')
        keyword = self.kw_edit.text().strip()
        pattern = self.pattern_edit.text().strip()
        files_only = self.files_only_ck.isChecked()

        if not dir_text:
            QMessageBox.warning(self, "提示", "请先输入或选择目录")
            return
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入关键词")
            return
        if not pattern:
            QMessageBox.warning(self, "提示", "请输入文件名模式（例如 day*.md）")
            return

        base_dir = Path(dir_text)

        if base_dir.exists() and base_dir.is_file():
            base_dir = base_dir.parent

        if not base_dir.exists():
            QMessageBox.critical(self, "错误", f"目录不存在：\n{base_dir}")
            return
        if not base_dir.is_dir():
            QMessageBox.critical(self, "错误", f"这不是目录：\n{base_dir}")
            return

        total_hits, matched_files, line_results, error_msgs = collect_matches(base_dir, keyword, pattern)

        self.last_output_text = build_output_text(
            keyword=keyword,
            base_dir=base_dir,
            files_only=files_only,
            total_hits=total_hits,
            matched_files=matched_files,
            line_results=line_results,
            error_msgs=error_msgs
        )

        self.output_box.setPlainText(self.last_output_text)
        self.highlight_keyword(keyword)

    def highlight_keyword(self, keyword: str):
        if not keyword.strip():
            return

        cursor = self.output_box.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        default_fmt = QTextCharFormat()
        default_fmt.setBackground(QColor(0, 0, 0, 0))
        default_fmt.setForeground(QColor("#111827"))
        cursor.mergeCharFormat(default_fmt)
        cursor.clearSelection()
        self.output_box.setTextCursor(cursor)

        text = self.output_box.toPlainText()
        lower_text = text.lower()
        key = keyword.lower()
        pos = 0

        while True:
            idx = lower_text.find(key, pos)
            if idx == -1:
                break

            c = self.output_box.textCursor()
            c.setPosition(idx)
            c.setPosition(idx + len(keyword), QTextCursor.MoveMode.KeepAnchor)

            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#fff59d"))
            fmt.setForeground(QColor("#000000"))
            c.mergeCharFormat(fmt)

            pos = idx + len(keyword)

    def copy_output(self):
        text = self.output_box.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "提示", "当前没有可复制的结果")
            return

        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "完成", "结果已复制到剪贴板")

    def export_output(self):
        text = self.last_output_text.strip()
        if not text:
            QMessageBox.information(self, "提示", "当前没有可导出的结果，请先搜索")
            return

        default_name = f"search_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出搜索结果",
            default_name,
            "Text Files (*.txt);;All Files (*.*)"
        )

        if not file_path:
            return

        try:
            Path(file_path).write_text(text, encoding="utf-8")
            QMessageBox.information(self, "完成", f"导出成功：\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败：{e}")


def main():
    app = QApplication(sys.argv)
    w = LogSearcherWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()