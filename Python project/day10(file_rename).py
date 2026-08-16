from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit,
    QFileDialog, QTextEdit, QListWidget, QAbstractItemView, QLabel, QFrame
)
from PySide6.QtGui import QPixmap,QIcon
from PySide6.QtCore import Qt
from pathlib import Path
import sys


class RenamerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量重命名器")
        self.resize(1200, 800)

        # ===== 背景图 =====
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.bg_label.setPixmap(QPixmap(r"bg.jpg"))
        self.bg_label.setGeometry(self.rect())
        self.bg_label.lower()

        # ===== 根布局 =====
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(0)

        # ===== Panel（关键：把主要控件都放进这个容器）=====
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(12)

        root_layout.addWidget(self.panel)

        # ===== 第1行：路径输入 + 确认路径 =====
        row_path = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("输入路径或点击右边按钮选择...")
        self.btn_confirm = QPushButton("确认路径")
        self.btn_confirm.clicked.connect(self.confirm_path)
        row_path.addWidget(self.path_input, 1)
        row_path.addWidget(self.btn_confirm)
        panel_layout.addLayout(row_path)

        # ===== 第2行：打开文件夹按钮（主按钮）=====
        self.btn_choose = QPushButton("打开文件管理器选择")
        self.btn_choose.setObjectName("primaryBtn")
        self.btn_choose.clicked.connect(self.choose_folder)
        row_path.addWidget(self.btn_choose)
        panel_layout.addLayout(row_path)
        # ===== 第3行：关键词输入 + 确认关键词 =====
        row_keyword = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入关键词")
        self.but_keyword = QPushButton("确认关键词")
        self.but_keyword.clicked.connect(self.keyword_select)
        row_keyword.addWidget(self.keyword_input, 1)
        row_keyword.addWidget(self.but_keyword)
        panel_layout.addLayout(row_keyword)

        # ===== 文件列表 =====
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        panel_layout.addWidget(self.file_list)

        # ===== 第4行：旧文件名 + 选中文件 =====
        row_old_name = QHBoxLayout()
        self.old_name_input = QLineEdit()
        self.old_name_input.setPlaceholderText("旧文件名")
        self.but_old_file = QPushButton("选中文件")
        self.but_old_file.clicked.connect(self.require_file)
        row_old_name.addWidget(self.old_name_input, 1)
        row_old_name.addWidget(self.but_old_file)
        panel_layout.addLayout(row_old_name)

        # ===== 第5行：新文件名 + 更改命名 =====
        row_new_name = QHBoxLayout()
        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText("新文件名")
        self.but_rename = QPushButton("更改命名")
        self.but_rename.setObjectName("primaryBtn")
        self.but_rename.clicked.connect(self.file_rename)
        row_new_name.addWidget(self.new_name_input, 1)
        row_new_name.addWidget(self.but_rename)
        panel_layout.addLayout(row_new_name)

        # ===== 日志区 =====
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        panel_layout.addWidget(self.display)

    # 背景图跟随窗口大小
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_label.setGeometry(self.rect())

    def confirm_path(self):
        self.file_list.clear()
        address = self.path_input.text().strip()
        if not address:
            self.file_list.addItem("请先输入路径")
            return
        try:
            folder = Path(address)
            for item in folder.iterdir():
                self.file_list.addItem(item.name)
        except Exception as e:
            self.file_list.addItem(f"路径无效：{e}")

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.path_input.setText(folder)

    def keyword_select(self):
        keyword = self.keyword_input.text().strip()
        address = self.path_input.text().strip()
        if not keyword or not address:
            self.file_list.addItem("请先输入路径和关键词")
            return
        try:
            folder = Path(address)
            self.file_list.clear()
            for item in folder.iterdir():
                if keyword in item.name:
                    self.file_list.addItem(item.name)
        except Exception as e:
            self.file_list.addItem(f"出错了：{e}")

    def require_file(self):
        selected = self.file_list.selectedItems()
        if not selected:
            self.display.append("请先在列表中选择文件")
            return
        self.old_name_input.setText(selected[0].text())
        self.display.append(f"已载入：{selected[0].text()}")

    def file_rename(self):
        address = self.path_input.text().strip()
        old_name = self.old_name_input.text().strip()
        new_name = self.new_name_input.text().strip()

        if not address or not old_name or not new_name:
            self.display.append("请填写完整再执行")
            return
        try:
            folder = Path(address)
            old_path = folder / old_name
            new_path = folder / new_name
            old_path.rename(new_path)
            self.display.append(f"更改成功：{old_name} -> {new_name}")
            self.confirm_path()  # 刷新列表
        except Exception as e:
            self.display.append(f"出错了：{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 全局样式（只设置一次）
    app.setStyleSheet("""
    QWidget {
        color: #0f172a;
        font-size: 16px;
    }

    QFrame#panel {
        background-color: rgba(255, 255, 255, 92);
        border: 1px solid rgba(191, 208, 230, 180);
        border-radius: 14px;
    }

    QLineEdit, QTextEdit, QListWidget {
        background-color: rgba(255, 255, 255, 228);
        border: 1px solid rgba(203, 213, 225, 190);
        border-radius: 10px;
        padding: 8px 10px;
        selection-background-color: #93c5fd;
    }

    QPushButton {
        min-height: 38px;
        background-color: rgba(241, 245, 249, 228);
        border: 1px solid rgba(203, 213, 225, 190);
        border-radius: 10px;
        padding: 6px 14px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: rgba(226, 232, 240, 240);
    }
    QPushButton:pressed {
        background-color: rgba(203, 213, 225, 245);
    }

    QPushButton#primaryBtn {
        background-color: rgba(255, 255, 255, 92);
        color: ;
        border: 1px solid rgba(37, 99, 235, 220);
    }
    QPushButton#primaryBtn:hover {
        background-color: rgba(37, 99, 235, 230);
    }
    QPushButton#primaryBtn:pressed {
        background-color: rgba(29, 78, 216, 235);
    }
    """)
    window = RenamerWindow()
    window.setWindowIcon(QIcon(r"app.ico"))
    window.show()
    sys.exit(app.exec())
