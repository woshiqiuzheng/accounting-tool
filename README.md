# 📒 个人记账本

一个轻量级的个人桌面记账工具，使用 Python + CustomTkinter 构建，数据存储在本地 SQLite 数据库中。

## ✨ 功能特性

- **📊 总览** — 月度收支汇总卡片、最近账单预览、预算执行进度
- **➕ 记账** — 支持支出、收入、转账三种类型，分类图标网格快速选择
- **📋 账单** — 完整账单列表，按日期分组，支持类型/分类/日期/备注筛选
- **📈 统计** — 月度收支汇总表 + 分类占比饼图（Matplotlib）
- **💰 预算** — 按分类设置月度预算，进度可视化，超支自动提醒
- **⚙️ 设置** — 自定义分类/账户、调整余额、导出 CSV

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| GUI 框架 | CustomTkinter |
| 数据库 | SQLite（`~/.personal_accounting/data.db`） |
| 图表 | Matplotlib |
| 测试 | pytest |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或使用 uv：

```bash
uv pip install -r requirements.txt
```

### 2. 启动应用

```bash
python main.py
```

或使用 uv：

```bash
uv run python main.py
```

### 3. 开始记账

首次启动会自动创建数据库并预置以下数据：

- **17 个分类**（11 个支出分类 + 6 个收入分类）
- **4 个默认账户**：现金、银行卡、支付宝、微信支付

## 📁 项目结构

```
personal_accounting/
├── main.py                  # 应用入口
├── requirements.txt         # 依赖列表
├── database/                # 数据库层
│   ├── connection.py        # SQLite 连接管理
│   ├── schema.py            # 建表 DDL
│   └── seed.py              # 预置数据
├── models/                  # 业务逻辑层
│   ├── transaction.py       # 账单 CRUD
│   ├── category.py          # 分类 CRUD
│   ├── account.py           # 账户 CRUD
│   ├── budget.py            # 预算 CRUD
│   └── statistics.py        # 统计查询
├── ui/                      # 界面层
│   ├── app.py               # 主窗口 + 侧边栏
│   ├── base_page.py         # 页面基类
│   ├── pages/               # 6 个功能页面
│   │   ├── overview_page.py
│   │   ├── add_page.py
│   │   ├── bills_page.py
│   │   ├── stats_page.py
│   │   ├── budget_page.py
│   │   └── settings_page.py
│   └── widgets/             # 可复用组件
│       ├── transaction_form.py
│       ├── transaction_list.py
│       ├── summary_cards.py
│       ├── budget_progress.py
│       └── toast.py
├── utils/
│   └── helpers.py           # 工具函数
└── tests/                   # 测试（34 个测试用例）
```

## 🗄️ 数据存储

- 数据库文件：`~/.personal_accounting/data.db`
- 数据库损坏时自动备份为 `data.db.bak` 并重建

## 📤 导出数据

在设置页可按时间范围导出账单为 CSV 文件，可用 Excel 打开。

## 📦 GitHub

项目地址：[https://github.com/woshiqiuzheng/accounting-tool](https://github.com/woshiqiuzheng/accounting-tool)
