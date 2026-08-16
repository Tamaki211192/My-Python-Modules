from PySide6.QtWidgets import (QApplication, QWidget, QPushButton,
                                QVBoxLayout, QHBoxLayout, QLineEdit,
                                QFileDialog, QTextEdit,QListWidget, QListWidgetItem,QAbstractItemView)
import sys
from PySide6.QtCore import Qt
app = QApplication(sys.argv)      # 启动 Qt 引擎
window = QWidget()                  # 创建一个空白窗口
window.resize(1200,800)             # 控制窗口大小
window.setWindowTitle("批量重命名器")  # 命名
layout = QVBoxLayout(window)        # 布局管理器

# 创建输入框
path_input = QLineEdit()
path_input.setPlaceholderText("输入路径或点击右边按钮选择...")
layout.addWidget(path_input)

# 创建按钮绑定函数
button = QPushButton('')
button.clicked.connect()
layout.addWidget(button)

# 调用输入框的内容
name_input = QLineEdit()
name_input.setPlaceholderText('文件名')
layout.addWidget(name_input)


def require_file():
    selected = file_list.selectedItems()        # 触发函数时取值
    if not selected:
        display.append('请先在列表中选择文件')
        return
    name_input.setText(selected[0].text())      # 取第一个选中项的文字 → 填进输入框
    display.append(f"已载入：{selected[0].text()}")     # 调用输入的内容


# 输出区（只读模式）
display = QTextEdit()
display.setReadOnly(True)
layout.addWidget(display)

