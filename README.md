# CounterStrike Analysis MVP

一个面向 `CS2 / Steam 饰品市场` 的 Python 分析原型项目。

当前版本的目标不是直接做自动交易，而是先把一条稳定、可扩展的分析链路跑通：

- 拉取行情数据
- 统一清洗与存储
- 计算技术指标
- 生成基础买卖信号
- 通过 API 输出给前端、脚本或告警系统

这个仓库适合作为后续继续扩展的基础版本，比如接入 `BUFF`、`悠悠有品`、`C5Game`、`SteamDT` 或第三方聚合源。

## Features

- `FastAPI` API 服务
- `SQLAlchemy` 数据模型与存储层
- `SQLite` 默认数据库，方便本地直接启动
- `mock collector`，无需真实平台账号也能跑通整条链路
- `pandas` 技术指标计算
- 内置基础分析指标：
  - `MA5 / MA20`
  - `EMA12 / EMA26`
  - `MACD`
  - `RSI14`
- 基础信号输出：
  - `buy_watch`
  - `hold`
  - `sell_watch`

## Project Structure

```text
steam_market_mvp/
  app/
    api/
      routes.py
    collectors/
      base.py
      mock_source.py
      cs2sh.py
    services/
      indicators.py
      ingest.py
      signals.py
    config.py
    db.py
    main.py
    models.py
    schemas.py
  tests/
    test_indicators.py
  .env.example
  .gitignore
  pytest.ini
  requirements.txt
  README.md
```

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- pandas
- numpy
- httpx
- pytest

## Quick Start

1. 创建虚拟环境

```bash
python -m venv .venv
```

2. 激活虚拟环境

Windows:

```bash
.venv\Scripts\activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 复制环境变量

```bash
copy .env.example .env
```

5. 启动服务

```bash
uvicorn app.main:app --reload --app-dir .
```

6. 打开接口文档

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

默认环境变量见 [.env.example](./.env.example)。

主要字段：

- `APP_NAME`: 服务名称
- `APP_ENV`: 运行环境
- `DATABASE_URL`: 数据库连接串，默认使用本地 SQLite
- `DEFAULT_SOURCE`: 默认数据源
- `CS2SH_API_KEY`: 预留给真实聚合数据源
- `CS2SH_BASE_URL`: 预留聚合数据源基础地址

## API Overview

### Health Check

```http
GET /api/v1/health
```

### Ingest Mock Data

```http
POST /api/v1/ingest/mock?item_name=AK-47%20%7C%20Redline%20(Field-Tested)&limit=120
```

作用：

- 生成指定饰品的模拟历史 K 线
- 写入数据库
- 自动刷新最新分析信号

### Ingest Real Source

```http
POST /api/v1/ingest/{source}?item_name=AK-47%20%7C%20Redline%20(Field-Tested)&limit=120
```

当前已预留：

- `mock`
- `cs2sh` 占位

### List Items

```http
GET /api/v1/items
```

### Query Candles

```http
GET /api/v1/items/{item_id}/candles?source=mock&limit=120
```

### Query Signals

```http
GET /api/v1/items/{item_id}/signals?source=mock
```

### Query Summary

```http
GET /api/v1/items/{item_id}/summary?source=mock
```

返回内容包括：

- 最新收盘价
- `MA5`
- `MA20`
- `RSI14`
- 趋势偏向
- 建议动作
- 自然语言说明

## Recommended Demo Flow

第一次启动后，推荐按这个顺序调用：

1. `POST /api/v1/ingest/mock`
2. `GET /api/v1/items`
3. `GET /api/v1/items/{item_id}/candles`
4. `GET /api/v1/items/{item_id}/signals`
5. `GET /api/v1/items/{item_id}/summary`

## Current Signal Logic

当前信号逻辑是规则驱动，不是机器学习预测。

大致思路：

- `MA5 > MA20` 时偏向短线走强
- `MA5 < MA20` 时偏向短线走弱
- `RSI14 < 35` 视为低位观察区
- `RSI14 > 70` 视为高位风险区
- `MACD` 与信号线关系用于辅助判断动量方向

最终输出一个简化动作：

- `buy_watch`
- `hold`
- `sell_watch`

这适合做第一版看盘和提示系统，但不应直接视为自动交易建议。

## Testing

运行测试：

```bash
pytest
```

当前已包含一个基础测试，覆盖：

- 技术指标计算
- 信号生成流程

## Roadmap

接下来适合继续扩展的方向：

- 接入真实数据源
  - `BUFF`
  - `悠悠有品`
  - `C5Game`
  - `SteamDT`
  - 聚合 API
- 增加数据库能力
  - PostgreSQL
  - 时间序列优化
- 增加策略维度
  - 手续费模型
  - 多平台价差
  - 深度与流动性过滤
- 增加任务系统
  - 定时采集
  - 增量更新
  - 告警推送
- 增加可视化
  - K 线页面
  - Watchlist
  - 多平台对比面板
- 增加 AI 解释层
  - 自动总结走势
  - 自动解释信号原因
  - 风险提示

## Notes

- 当前默认使用 `mock` 数据源，因此可以离线演示完整流程。
- `cs2sh` collector 目前是占位实现，后续确认接口契约后可直接补上。
- 如果要接入真实平台，请优先确认平台协议、频率限制与鉴权要求。

## License

当前仓库未显式声明许可证；如果你准备公开长期维护，建议补一个 `MIT` 或你偏好的开源协议。
