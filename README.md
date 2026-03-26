# 安顶山云雾茶数字焕新平台

这是一个基于 Python + SQLite + HTML5 构建的电商数据可视化平台，旨在通过数字化手段提升安顶山云雾茶的运营效率。

## 功能模块

1.  **数据生成模块**: 使用 `init_db.py` 自动生成逼真的模拟数据（包含产品、客户、订单、订单项）。
2.  **数据分析模块**: 使用 `export_data.py` 从 SQLite 数据库中提取关键业务指标，并生成 `static/data.json` 供前端使用。
3.  **可视化展示模块**: 使用 `index.html` 结合 Bootstrap 和 Chart.js 展示实时数据看板，包括：
    - 关键指标（销售额、订单数、客单价、活跃客户）
    - 月度销售趋势图
    - 产品类别销售占比图
    - 热销产品排行
    - 最新订单列表

## 技术栈

- **后端**: Python (标准库 sqlite3, json, random)
- **数据库**: SQLite
- **前端**: HTML5, Bootstrap 5, Chart.js
- **服务器**: Python 内置 HTTP Server (自定义脚本解决中文环境兼容性)

## 如何运行

1.  **初始化数据库** (如果第一次运行):
    ```bash
    python init_db.py
    ```
    这将创建 `tea_platform.db` 并填充模拟数据。

2.  **更新数据** (可选):
    ```bash
    python export_data.py
    ```
    这将重新计算指标并更新 `static/data.json`。

3.  **启动服务器**:
    ```bash
    python run_server.py
    ```
    服务器将在 `http://127.0.0.1:8000` 启动。

4.  **访问平台**:
    打开浏览器访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 项目结构

```
tea_platform/
├── init_db.py          # 数据库初始化与数据生成
├── export_data.py      # 数据分析与导出脚本
├── run_server.py       # 本地开发服务器
├── shop.html           # (前端) C端茶商城与产业互联网门户 (参考 365tea 与 yiruit)
├── index.html          # (后台) B端数据看板与企业 ERP
├── static/
│   ├── data.json       # 生成的数据文件
│   ├── css/
│   └── js/
└── tea_platform.db     # SQLite 数据库文件
```
