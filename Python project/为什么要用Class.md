# 为什么要用 Class？—— 从"能跑就行"到"写得好"

## 你现在的疑问

> "class 不是达成目的的必要条件，所以我不理解它的作用。"

这个疑问完全正确。对于小程序，`class` 确实不是必须的。但随着项目变大，你会遇到一堵墙——本文就是为了让你在撞墙之前，提前理解 `class` 的价值。

---

## 第一步：看一个真实的问题

以你的剪贴板管理器为例，你现在有这些全局变量：

```python
last_clipboard = ''
change_count = 1
history = []
drag_pos = None
```

以及这些函数：

```python
def check_clipboard(): ...
def copy_back(item): ...
def research_keyword(): ...
def clear_all(): ...
def delete_selected(): ...
def close_to_tray(event): ...
def ball_mouse_press(event): ...
def ball_mouse_move(event): ...
def ball_mouse_release(event): ...
```

**现在假设你想在同一个程序里开两个剪贴板窗口**，会发生什么？

- `history` 是全局的，两个窗口会共用同一份历史
- `last_clipboard` 也是共用的，逻辑会混乱
- 函数也只有一套，没法分别控制两个窗口

这就是全局变量的核心问题：**数据和功能无法被"复制"和"独立使用"**。

---

## 第二步：class 是什么

`class` 就是一个**模板**，用来创建拥有**自己数据**和**自己方法**的对象。

```python
class ClipboardManager:
    def __init__(self):          # 初始化，每个对象都有自己的数据
        self.history = []
        self.last_clipboard = ''
        self.drag_pos = None

    def check_clipboard(self):
        text = clipboard.text()
        if not text or text == self.last_clipboard:
            return
        self.last_clipboard = text
        self.history.insert(0, text)

    def clear_all(self):
        self.history.clear()
```

用的时候：

```python
manager1 = ClipboardManager()   # 第一个管理器，有自己的 history
manager2 = ClipboardManager()   # 第二个管理器，有自己的 history，互不干扰
```

`self` 就是"这个对象自己"，`self.history` 就是"这个对象自己的 history"。

---

## 第三步：类比现实世界

| 概念 | 类比 |
|------|------|
| `class ClipboardManager` | 剪贴板管理器的**设计图纸** |
| `manager = ClipboardManager()` | 按图纸**造出一台**管理器 |
| `self.history` | 这台管理器**内部**的历史记录 |
| `self.check_clipboard()` | 这台管理器能执行的**操作** |

图纸只有一份，但可以造出很多台，每台都独立运作。

---

## 第四步：你现在的代码 vs 用 class 改写后

### 现在（全局变量版）

```python
history = []
last_clipboard = ''

def check_clipboard():
    global last_clipboard   # ← 每次都要声明 global，麻烦且危险
    text = clipboard.text()
    if text == last_clipboard:
        return
    last_clipboard = text
    history.insert(0, text)
```

### 改成 class 后

```python
class ClipboardManager:
    def __init__(self):
        self.history = []
        self.last_clipboard = ''

    def check_clipboard(self):
        text = clipboard.text()
        if text == self.last_clipboard:   # ← 不需要 global，直接用 self
            return
        self.last_clipboard = text
        self.history.insert(0, text)
```

没有了 `global`，数据属于对象本身，更安全，更清晰。

---

## 第五步：你已经在用 class 了！

你用的 PySide6 里到处都是 class：

```python
window = QWidget()        # QWidget 是一个 class，window 是它的一个对象
timer = QTimer()          # QTimer 是一个 class
tray = QSystemTrayIcon()  # QSystemTrayIcon 是一个 class
```

你每次写 `window.show()`、`timer.start(500)`，就是在调用**对象的方法**，这就是 class 的使用。

你下一步要做的，是**自己写 class**，而不只是用别人写的。

---

## 第六步：什么时候应该用 class？

| 场景 | 建议 |
|------|------|
| 脚本只有 20 行，跑一次就结束 | 不用 class，函数就够了 |
| 有多个相关的全局变量 + 操作它们的函数 | **应该**用 class 把它们包起来 |
| 需要创建多个相似的"东西" | **必须**用 class |
| 代码超过 100 行，变量越来越多 | **强烈建议**用 class |

你的剪贴板管理器已经满足第2条和第4条了。

---

## 动手练习建议

把 `drag_pos`、`ball_mouse_press`、`ball_mouse_move`、`ball_mouse_release` 包成一个 `DraggableBall` 类：

```python
class DraggableBall(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_pos = None        # self 代替 global
        # ... 窗口设置 ...

    def mousePressEvent(self, event):    # 直接重写方法，不用赋值
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
```

对比你原来的写法，功能完全相同，但：
- 没有全局变量
- `drag_pos` 只属于这个悬浮球，不会污染其他代码
- 以后想要两个悬浮球？`ball1 = DraggableBall()`，`ball2 = DraggableBall()`，一行搞定

---

## 总结

> class 不是让程序"能跑"的工具，它是让程序"能长大"的工具。

当你的项目只有 50 行时，感受不到 class 的价值。  
当你的项目到了 300 行，你会开始觉得全局变量很乱。  
当你的项目到了 1000 行，你会非常感激当初用了 class。
