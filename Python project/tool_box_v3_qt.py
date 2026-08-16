# File Converter.py  — 从 Tkinter 移植到 PySide6（Qt），支持自定义背景图
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QFileDialog, QMessageBox, QCheckBox, QSpinBox, QListWidget,
    QTabWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QGridLayout
)

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


# ==================== 常量 ====================
APP_TITLE = "实用工具箱 V3（ICO / 文本PDF / 图片PDF）"
CONFIG_FILE = "toolbox_config.json"    # 跟检索器用不同的文件名，避免冲突
ICON_SIZES = [16, 24, 32, 48, 64, 128, 256]
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def resource_path(rel: str) -> str:
    """兼容开发环境 & PyInstaller"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    return os.path.join(base_dir, rel)


# ==================== 主窗口 ====================
class ToolBoxV3(QWidget):
    """Qt 版工具箱，替代原 Tkinter 版本"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1200, 820)
        self.setMinimumSize(1000, 680)

        # ----- 读取/恢复配置 -----
        self.config = self._load_config()
        self.last_open_dir = self.config.get("last_open_dir", str(Path.cwd()))
        self.theme_mode = self.config.get("theme_mode", "glass")  # light / glass / ultra

        # ----- 背景图（三级回退：自定义路径 → 内置 bg.jpg → 无） -----
        self.bg_image_path = self.config.get("bg_image_path", "")
        self._load_bg_pixmap()

        # ----- 窗口图标 -----
        ico_path = self.config.get("ico_path", "") or resource_path("app.ico")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        # ----- 背景图层（必须最先创建，放在所有控件下面） -----
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        # ----- 前景容器 -----
        self.panel = QWidget(self)
        self.panel.setObjectName("panel")

        # ----- 顶部：输出目录 + 背景图按钮 -----
        self.output_dir_edit = QLineEdit(self.config.get("output_dir", str(Path.cwd())))
        self.output_dir_edit.setMinimumWidth(400)
        btn_choose_dir = QPushButton("选择输出目录")
        btn_choose_dir.clicked.connect(self.choose_output_dir)

        self.btn_bg = QPushButton("选择背景图")
        self.btn_bg.clicked.connect(self.choose_bg_image)
        self.btn_reset_bg = QPushButton("重置背景")
        self.btn_reset_bg.clicked.connect(self.reset_bg_image)

        self.btn_theme = QPushButton("透明度：Glass")
        self.btn_theme.clicked.connect(self.cycle_theme)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("输出目录:"))
        top_row.addWidget(self.output_dir_edit, 1)
        top_row.addWidget(btn_choose_dir)
        top_row.addSpacing(12)
        top_row.addWidget(self.btn_bg)
        top_row.addWidget(self.btn_reset_bg)
        top_row.addWidget(self.btn_theme)

        # ----- 中间：TabWidget -----
        self.tabs = QTabWidget()

        self.tab_ico = QWidget()
        self.tab_text_pdf = QWidget()
        self.tab_img_pdf = QWidget()

        self.tabs.addTab(self.tab_ico, "图片 → ICO")
        self.tabs.addTab(self.tab_text_pdf, "文本/Markdown → PDF")
        self.tabs.addTab(self.tab_img_pdf, "图片 → PDF")

        self._build_tab_ico()
        self._build_tab_text_pdf()
        self._build_tab_img_pdf()

        # ----- 底部：日志 -----
        log_group = QGroupBox("日志")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(160)
        self.log_text.setPlaceholderText("操作日志将显示在这里...")
        log_layout = QVBoxLayout(log_group)
        log_layout.addWidget(self.log_text)

        # ----- 组装：panel 内是业务 UI，外层放背景 -----
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.addLayout(top_row)
        panel_layout.addWidget(self.tabs, 1)
        panel_layout.addWidget(log_group)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.addWidget(self.panel, 1)

        # 应用半透明样式
        self._apply_style()

        self.log("工具箱启动完成。")

    # ==================== 配置读写 ====================
    def _load_config(self):
        p = Path(CONFIG_FILE)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_config(self):
        data = {
            "output_dir": self.output_dir_edit.text().strip() or str(Path.cwd()),
            "last_open_dir": self.last_open_dir,
            "bg_image_path": str(Path(self.bg_image_path)) if self.bg_image_path else "",
            "theme_mode": self.theme_mode,
        }
        Path(CONFIG_FILE).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ==================== 背景图 ====================
    def _load_bg_pixmap(self):
        """三级回退加载背景图"""
        if self.bg_image_path and os.path.exists(self.bg_image_path):
            self.bg_pixmap = QPixmap(self.bg_image_path)
            return
        builtin = resource_path("bg.jpg")
        if os.path.exists(builtin):
            self.bg_pixmap = QPixmap(builtin)
            self.bg_image_path = ""
            return
        self.bg_pixmap = None
        self.bg_image_path = ""

    def _update_bg_display(self):
        """刷新背景图（窗口大小改变时也调用）"""
        self.bg_label.setGeometry(self.rect())
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(scaled)
        else:
            self.bg_label.clear()
        self.bg_label.lower()

    def choose_bg_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", "",
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*.*)"
        )
        if not file_path:
            return
        self.bg_image_path = file_path
        self._load_bg_pixmap()
        self._update_bg_display()
        self._save_config()
        self.log(f"背景图已更换: {file_path}")

    def reset_bg_image(self):
        self.bg_image_path = ""
        self._load_bg_pixmap()
        self._update_bg_display()
        self._save_config()
        self.log("背景图已重置为默认")

    # ==================== 主题（半透明面板） ====================
    def _apply_style(self):
        themes = {
            "light": {
                "panel": 205,
                "input": 220,
                "button": 210,
                "button_hover": 225,
                "button_press": 235,
                "border": 150,
                "tab_pane": 180,
                "tab_bar": 200,
                "tab_selected": 240,
                "groupbox": 180,
                "list_widget": 200,
                "btn_text": "透明度：Light",
            },
            "glass": {
                "panel": 130,
                "input": 120,
                "button": 155,
                "button_hover": 180,
                "button_press": 195,
                "border": 140,
                "tab_pane": 120,
                "tab_bar": 130,
                "tab_selected": 180,
                "groupbox": 120,
                "list_widget": 140,
                "btn_text": "透明度：Glass",
            },
            "ultra": {
                "panel": 90,
                "input": 85,
                "button": 120,
                "button_hover": 150,
                "button_press": 170,
                "border": 130,
                "tab_pane": 85,
                "tab_bar": 100,
                "tab_selected": 150,
                "groupbox": 85,
                "list_widget": 100,
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
            QTabWidget::pane {{
                background: rgba(255, 255, 255, {t["tab_pane"]});
                border: 1px solid rgba(203, 213, 225, {t["border"]});
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: rgba(226, 232, 240, {t["tab_bar"]});
                border: 1px solid rgba(203, 213, 225, 120);
                padding: 8px 18px;
                border-radius: 6px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background: rgba(255, 255, 255, {t["tab_selected"]});
                font-weight: bold;
            }}
            QGroupBox {{
                background: rgba(255, 255, 255, {t["groupbox"]});
                border: 1px solid rgba(203, 213, 225, {t["border"]});
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
            QListWidget {{
                background: rgba(255, 255, 255, {t["list_widget"]});
                border: 1px solid rgba(203, 213, 225, 120);
                border-radius: 6px;
            }}
            QCheckBox {{ spacing: 6px; }}
        """)

        self.btn_theme.setText(t["btn_text"])

    def cycle_theme(self):
        order = ["light", "glass", "ultra"]
        i = order.index(self.theme_mode)
        self.theme_mode = order[(i + 1) % len(order)]
        self._apply_style()
        self._save_config()

    # ==================== 窗口缩放 ====================
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_bg_display()

    def closeEvent(self, event):
        self._save_config()
        event.accept()

    # ==================== 公共工具 ====================
    def log(self, msg: str):
        self.log_text.append(f"[{now_str()}] {msg}")

    def choose_output_dir(self):
        folder = QFileDialog.getExistingDirectory(
            self, "选择输出目录",
            self.output_dir_edit.text().strip() or str(Path.cwd())
        )
        if folder:
            self.output_dir_edit.setText(folder)
            self.last_open_dir = folder
            self.log(f"输出目录已设置为: {folder}")

    def _ensure_output_dir(self) -> Path:
        out = Path(self.output_dir_edit.text().strip() or Path.cwd())
        out.mkdir(parents=True, exist_ok=True)
        return out

    # ==================== Tab1: 图片 → ICO ====================
    def _build_tab_ico(self):
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.ico_img_edit = QLineEdit()
        self.ico_img_edit.setPlaceholderText("请选择图片文件...")
        grid.addWidget(QLabel("图片文件:"), 0, 0)
        grid.addWidget(self.ico_img_edit, 0, 1)
        btn_pick_img = QPushButton("选择图片")
        btn_pick_img.clicked.connect(self._pick_ico_image)
        grid.addWidget(btn_pick_img, 0, 2)

        self.ico_name_edit = QLineEdit("app.ico")
        grid.addWidget(QLabel("输出文件名:"), 1, 0)
        grid.addWidget(self.ico_name_edit, 1, 1)

        self.ico_crop_cb = QCheckBox("自动居中裁切为正方形")
        self.ico_crop_cb.setChecked(True)
        grid.addWidget(self.ico_crop_cb, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)

        btn_convert_ico = QPushButton("开始转换 ICO")
        btn_convert_ico.clicked.connect(self._convert_to_ico)
        grid.addWidget(btn_convert_ico, 1, 2)

        grid.setColumnStretch(1, 1)

        preview_label = QLabel("预览")
        preview_label.setStyleSheet("font-weight: 600; color: #374151; padding: 4px 0;")
        self.ico_preview_label = QLabel("请选择图片")
        self.ico_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ico_preview_label.setMinimumHeight(320)
        self.ico_preview_label.setStyleSheet(
            "background-color: rgba(255,255,255,180); border: 1px solid rgba(203,213,225,140); border-radius: 8px;"
        )

        layout = QVBoxLayout(self.tab_ico)
        layout.addLayout(grid)
        layout.addWidget(preview_label)
        layout.addWidget(self.ico_preview_label, 1)

    def _pick_ico_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片",
            self.last_open_dir,
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*.*)"
        )
        if not file_path:
            return
        self.ico_img_edit.setText(file_path)
        self.last_open_dir = str(Path(file_path).parent)
        self._show_ico_preview(Path(file_path))
        self.log(f"已选择图片: {file_path}")

    def _show_ico_preview(self, image_path: Path):
        try:
            img = Image.open(image_path).convert("RGBA")
            preview = img.copy()
            preview.thumbnail((820, 380), Image.LANCZOS)
            data = preview.tobytes("raw", "RGBA")
            qimg = QImage(data, preview.width, preview.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg)
            self.ico_preview_label.setPixmap(pixmap)
            self.ico_preview_label.setText("")
        except Exception as e:
            self.ico_preview_label.setText(f"预览失败: {e}")
            self.ico_preview_label.setPixmap(QPixmap())

    @staticmethod
    def _center_crop_square(img: Image.Image) -> Image.Image:
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        return img.crop((left, top, left + side, top + side))

    def _convert_to_ico(self):
        img_path = self.ico_img_edit.text().strip()
        if not img_path:
            QMessageBox.warning(self, "提示", "请先选择图片")
            return
        p = Path(img_path)
        if not p.exists():
            QMessageBox.critical(self, "错误", f"图片不存在:\n{p}")
            return
        out_dir = self._ensure_output_dir()
        out_name = self.ico_name_edit.text().strip() or "app.ico"
        if not out_name.lower().endswith(".ico"):
            out_name += ".ico"
        out_path = out_dir / out_name
        sizes = [16, 24, 32, 48, 64, 128, 256]
        try:
            img = Image.open(p).convert("RGBA")
            if self.ico_crop_cb.isChecked():
                img = self._center_crop_square(img)
            base_side = max(img.size[0], img.size[1])
            if base_side < 256:
                scale = 256 / base_side
                img = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)), Image.LANCZOS)
            img = self._center_crop_square(img)
            icon_frames = [img.resize((s, s), Image.LANCZOS) for s in sizes]
            icon_frames[-1].save(out_path, format="ICO", sizes=[(s, s) for s in sizes])
            self.log(f"ICO 导出成功: {out_path} (sizes={sizes})")
            QMessageBox.information(self, "完成", f"ICO 导出成功：\n{out_path}\n尺寸：{sizes}")
        except Exception as e:
            self.log(f"ICO 导出失败: {e}")
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    # ==================== Tab2: 文本/Markdown → PDF ====================
    def _build_tab_text_pdf(self):
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        self.txt_file_edit = QLineEdit()
        self.txt_file_edit.setPlaceholderText("请选择 .txt 或 .md 文件...")
        grid.addWidget(QLabel("文本文件:"), 0, 0)
        grid.addWidget(self.txt_file_edit, 0, 1)
        btn_pick_txt = QPushButton("选择 .txt/.md")
        btn_pick_txt.clicked.connect(self._pick_text_file)
        grid.addWidget(btn_pick_txt, 0, 2)

        self.txt_pdf_name_edit = QLineEdit("text_output.pdf")
        grid.addWidget(QLabel("PDF 文件名:"), 1, 0)
        grid.addWidget(self.txt_pdf_name_edit, 1, 1)

        grid.addWidget(QLabel("字号:"), 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 20)
        self.font_size_spin.setValue(12)
        self.font_size_spin.setFixedWidth(60)
        grid.addWidget(self.font_size_spin, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)

        btn_convert_txt = QPushButton("开始转换 PDF")
        btn_convert_txt.clicked.connect(self._convert_text_to_pdf)
        grid.addWidget(btn_convert_txt, 1, 2)

        grid.setColumnStretch(1, 1)

        tips = QLabel(
            "说明：\n1) 支持 UTF-8 的 .txt / .md。\n"
            "2) Markdown 会按普通文本写入，不做样式渲染。\n3) 自动换页。"
        )
        tips.setStyleSheet("color: #555;")

        layout = QVBoxLayout(self.tab_text_pdf)
        layout.addLayout(grid)
        layout.addWidget(tips)
        layout.addStretch(1)

    def _pick_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文本文件",
            self.last_open_dir,
            "Text Files (*.txt *.md);;All Files (*.*)"
        )
        if not file_path:
            return
        self.txt_file_edit.setText(file_path)
        self.last_open_dir = str(Path(file_path).parent)
        self.log(f"已选择文本文件: {file_path}")

    def _convert_text_to_pdf(self):
        src = self.txt_file_edit.text().strip()
        if not src:
            QMessageBox.warning(self, "提示", "请先选择文本文件")
            return
        src_path = Path(src)
        if not src_path.exists():
            QMessageBox.critical(self, "错误", f"文件不存在:\n{src_path}")
            return
        out_dir = self._ensure_output_dir()
        pdf_name = self.txt_pdf_name_edit.text().strip() or "text_output.pdf"
        if not pdf_name.lower().endswith(".pdf"):
            pdf_name += ".pdf"
        out_pdf = out_dir / pdf_name
        fs = self.font_size_spin.value()
        try:
            content = src_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            c = canvas.Canvas(str(out_pdf), pagesize=A4)
            width, height = A4
            try:
                pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
                font_name = "STSong-Light"
            except Exception:
                font_name = "Helvetica"
            c.setFont(font_name, fs)
            left_margin = 40
            top_margin = 40
            line_height = fs + 4
            y = height - top_margin
            for line in lines:
                text_line = line
                max_chars = 95
                while len(text_line) > max_chars:
                    c.drawString(left_margin, y, text_line[:max_chars])
                    y -= line_height
                    text_line = text_line[max_chars:]
                    if y < 50:
                        c.showPage()
                        c.setFont(font_name, fs)
                        y = height - top_margin
                c.drawString(left_margin, y, text_line)
                y -= line_height
                if y < 50:
                    c.showPage()
                    c.setFont(font_name, fs)
                    y = height - top_margin
            c.save()
            self.log(f"文本转 PDF 成功: {out_pdf}")
            QMessageBox.information(self, "完成", f"PDF 导出成功:\n{out_pdf}")
        except Exception as e:
            self.log(f"文本转 PDF 失败: {e}")
            QMessageBox.critical(self, "错误", f"转换失败: {e}")

    # ==================== Tab3: 图片 → PDF ====================
    def _build_tab_img_pdf(self):
        self.img_list = []

        btn_row = QHBoxLayout()
        btn_add = QPushButton("添加图片")
        btn_add.clicked.connect(self._add_images)
        btn_clear = QPushButton("清空列表")
        btn_clear.clicked.connect(self._clear_images)
        btn_up = QPushButton("上移")
        btn_up.clicked.connect(self._move_up)
        btn_down = QPushButton("下移")
        btn_down.clicked.connect(self._move_down)

        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_clear)
        btn_row.addWidget(btn_up)
        btn_row.addWidget(btn_down)
        btn_row.addSpacing(20)

        self.img_pdf_name_edit = QLineEdit("images_output.pdf")
        btn_row.addWidget(QLabel("PDF 文件名:"))
        btn_row.addWidget(self.img_pdf_name_edit, 1)

        btn_convert_img = QPushButton("开始合并为 PDF")
        btn_convert_img.clicked.connect(self._convert_images_to_pdf)
        btn_row.addWidget(btn_convert_img)

        list_group = QGroupBox("图片列表（顺序即 PDF 页顺序）")
        self.img_listbox = QListWidget()
        list_layout = QVBoxLayout(list_group)
        list_layout.addWidget(self.img_listbox)

        layout = QVBoxLayout(self.tab_img_pdf)
        layout.addLayout(btn_row)
        layout.addWidget(list_group, 1)

    def _add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片（可多选）",
            self.last_open_dir,
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp);;All Files (*.*)"
        )
        if not files:
            return
        for f in files:
            p = Path(f)
            if p.suffix.lower() in IMG_EXTS:
                self.img_list.append(p)
        if files:
            self.last_open_dir = str(Path(files[0]).parent)
        self._refresh_img_listbox()
        self.log(f"已添加图片 {len(files)} 张。")

    def _clear_images(self):
        self.img_list.clear()
        self._refresh_img_listbox()
        self.log("图片列表已清空。")

    def _refresh_img_listbox(self):
        self.img_listbox.clear()
        for i, p in enumerate(self.img_list, start=1):
            self.img_listbox.addItem(f"{i:02d}. {p}")

    def _move_up(self):
        i = self.img_listbox.currentRow()
        if i < 0 or i == 0:
            return
        self.img_list[i - 1], self.img_list[i] = self.img_list[i], self.img_list[i - 1]
        self._refresh_img_listbox()
        self.img_listbox.setCurrentRow(i - 1)

    def _move_down(self):
        i = self.img_listbox.currentRow()
        if i < 0 or i >= len(self.img_list) - 1:
            return
        self.img_list[i + 1], self.img_list[i] = self.img_list[i], self.img_list[i + 1]
        self._refresh_img_listbox()
        self.img_listbox.setCurrentRow(i + 1)

    def _convert_images_to_pdf(self):
        if not self.img_list:
            QMessageBox.warning(self, "提示", "请先添加至少一张图片")
            return
        out_dir = self._ensure_output_dir()
        pdf_name = self.img_pdf_name_edit.text().strip() or "images_output.pdf"
        if not pdf_name.lower().endswith(".pdf"):
            pdf_name += ".pdf"
        out_pdf = out_dir / pdf_name
        try:
            pil_images = [Image.open(p).convert("RGB") for p in self.img_list]
            first = pil_images[0]
            rest = pil_images[1:]
            first.save(out_pdf, save_all=True, append_images=rest)
            self.log(f"图片合并 PDF 成功: {out_pdf}（共 {len(pil_images)} 页）")
            QMessageBox.information(self, "完成", f"PDF 导出成功:\n{out_pdf}")
        except Exception as e:
            self.log(f"图片转 PDF 失败: {e}")
            QMessageBox.critical(self, "错误", f"转换失败: {e}")


# ==================== 程序入口 ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToolBoxV3()
    window.show()
    sys.exit(app.exec())