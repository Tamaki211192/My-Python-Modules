
# Git 常用命令理解笔记（入门版）

## 一、完整命令串
```bash
git init
git add .
git commit -m "init: add python modules"
git branch -M main
git remote add origin https://github.com/Tamaki211192/My-Python-Modules.git
git push -u origin main
```

---

## 二、逐条解释

### 1) `git init`
**作用**：把当前文件夹初始化成 Git 仓库。  
**结果**：生成 `.git/` 隐藏目录，用来记录版本历史。

你可以这样记：  
> 从现在开始，这个文件夹进入“可版本管理”状态。

---

### 2) `git add .`
**作用**：把当前目录下的改动加入“暂存区（staging area）”。  
`.` 表示当前目录所有文件（递归）。

你可以这样记：  
> 把准备提交的文件先放进“待提交购物车”。

---

### 3) `git commit -m "init: add python modules"`
**作用**：把暂存区内容保存成一次正式版本快照。  
`-m` 后是提交说明（commit message）。

你可以这样记：  
> 真正按下“保存版本”，并写下这次改了什么。

---

### 4) `git branch -M main`
**作用**：把当前分支强制重命名为 `main`。  
常用于统一主分支名称（避免 `master/main` 混用）。

你可以这样记：  
> 把主干分支名统一成 `main`。

---

### 5) `git remote add origin <仓库URL>`
示例：
```bash
git remote add origin https://github.com/Tamaki211192/My-Python-Modules.git
```

**作用**：给本地仓库绑定远程仓库地址。  
- `origin` 是远程仓库的默认别名（可自定义，但一般都用 origin）。

你可以这样记：  
> 告诉本地 Git：将来要上传到哪个 GitHub 仓库。

---

### 6) `git push -u origin main`
**作用**：把本地 `main` 分支推送到远程 `origin`。  
`-u`：建立上游跟踪关系，后续可直接 `git push` / `git pull`。

你可以这样记：  
> 第一次把本地主分支上传，并建立长期连接。

---

## 三、动作流程图（最重要）

1. `init`：创建本地仓库  
2. `add`：挑选要提交的文件  
3. `commit`：保存版本  
4. `remote add`：连接远程仓库  
5. `push`：上传到 GitHub

---

## 四、常见报错与处理

### 报错1：`remote origin already exists`
说明已经设置过远程仓库。
```bash
git remote set-url origin https://github.com/Tamaki211192/My-Python-Modules.git
```

---

### 报错2：`failed to push ... rejected`
说明远程有提交（如你先在网页创建了 README）。
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

---

## 五、自测（检查是否真正理解）

1. `git add` 和 `git commit` 的区别是什么？  
2. 为什么要 `git remote add origin`？  
3. 第一次 `git push` 为什么常加 `-u`？

---

## 六、一句话总结
Git 不是背命令，而是固定流程：  
**初始化 → 暂存 → 提交 → 连接远程 → 推送**。
