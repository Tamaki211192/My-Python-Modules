from PySide6.QtWidgets import (
    QApplication,    # 启动引擎，所有 Qt 程序必须先有它
    QWidget,         # 空白窗口（所有控件的"容器"）
    QPushButton,     # 按钮
    QLabel,          # 标签（显示文字，用户不能编辑）
    QLineEdit,       # 单行输入框（用户可以在里面打字）
    QTextEdit,       # 多行文本区（可读写，也可设为只读当显示屏）
    QCheckBox,       # 勾选框
    QSpinBox,        # 数字调节框（带上下箭头）
    QListWidget,     # 列表控件（可以点击选中、多选）
    QFileDialog,     # 文件/文件夹选择弹窗
    QMessageBox,     # 消息弹窗（提示框、警告框、确认框）
    QTabWidget,      # 标签页（多个页面切换）
    QGroupBox,       # 分组框（把相关控件圈在一起，带标题）
    QVBoxLayout,     # 竖排布局（从上往下排）
    QHBoxLayout,     # 横排布局（从左往右排）
    QGridLayout,     # 网格布局（按行列排列）
)
from PySide6.QtCore import Qt          # 枚举常量（对齐方式等）
from PySide6.QtGui import QPixmap, QIcon  # 图片、图标相关


from PySide6.QtWidgets import QApplication, QWidget
import sys

app = QApplication(sys.argv)    # ① 启动引擎（固定写法，照抄）
window = QWidget()              # ② 创建空白窗口
window.resize(800, 600)         # ③ 设置大小（宽, 高）
window.setWindowTitle("标题")    # ④ 设置标题
window.show()                   # ⑤ 显示窗口
sys.exit(app.exec())            # ⑥ 保持运行（必须放在最后）


# 竖排：控件从上往下堆
layout = QVBoxLayout(window)       # 创建竖排布局，绑到窗口
layout.addWidget(label)            # 加控件（按顺序往下排）
layout.addWidget(btn)

# 横排：控件从左往右排
row = QHBoxLayout()                # 创建横排布局
row.addWidget(label)
row.addWidget(input_box)
layout.addLayout(row)              # 把横排布局嵌进竖排布局


label = QLabel("这是标签")
label.setStyleSheet("color: red; font-weight: bold;")


btn = QPushButton("按钮文字")
btn.clicked.connect(某个函数)      # 点击时调用该函数（不要加括号）


box = QLineEdit()
box.setPlaceholderText("提示文字...")   # 灰色提示（输入后消失）
box.text()                              # 读取用户输入的内容（返回字符串）
box.setText("写进去")                    # 往输入框里写入文字
box.clear()                             # 清空输入框


display = QTextEdit()
display.setReadOnly(True)          # 设为只读（用户不能编辑，适合做日志/结果显示）
display.append("追加一行文字")      # 在末尾追加内容
display.clear()                    # 清空全部内容


file_list = QListWidget()
file_list.addItem("文件名.txt")    # 添加一行
file_list.addItems(["a.txt", "b.txt"])  # 批量添加
file_list.clear()                  # 清空列表

# 获取用户选中的项目
selected = file_list.selectedItems()   # 返回列表
for item in selected:
    print(item.text())                 # 取出选中那行的文字


# 选择文件夹
folder = QFileDialog.getExistingDirectory(window, "选择文件夹")
# 用户取消时返回空字符串 ""

# 选择单个文件
file_path, _ = QFileDialog.getOpenFileName(
    window, "选择文件", "",
    "Text Files (*.txt);;All Files (*.*)"
)


QMessageBox.information(window, "标题", "操作成功！")   # 信息提示
QMessageBox.warning(window, "警告", "有冲突！")          # 警告
QMessageBox.critical(window, "错误", "出错了！")         # 错误


btn.clicked.connect(my_function)   # 按钮被点击（信号） → 调用 my_function（槽）
btn.clicked.connect(my_function)    # 正确：点击时才调用
btn.clicked.connect(my_function())  # 错误：程序启动时立刻调用了


def do_something():
    text = input_box.text().strip()       # 读取输入框
    if not text:
        display.append("请输入内容")
        return
    result = text.upper()                 # 处理
    display.clear()
    display.append(result)               # 显示结果

btn.clicked.connect(do_something)


def choose_folder():
    folder = QFileDialog.getExistingDirectory(window, "选择文件夹")
    if folder:
        path_input.setText(folder)

btn_choose.clicked.connect(choose_folder)


from pathlib import Path

def list_files():
    address = path_input.text().strip()
    if not address:
        display.append("请先输入路径")
        return
    try:
        folder = Path(address)
        file_list.clear()
        for item in folder.iterdir():
            file_list.addItem(item.name)
    except Exception as e:
        display.append(f"路径无效：{e}")
