# Steam Market Analysis MVP

一个面向 CS2/Steam 饰品市场分析的 Python MVP。

这版目标是先跑通完整链路：

- 采集行情数据
- 存储为统一格式
- 计算技术指标
- 生成基础买卖信号
- 通过 FastAPI 暴露查询接口

## 技术选型

- FastAPI: 提供 API
- SQLAlchemy: 数据模型与存储
- SQLite: 默认本地数据库，方便直接启动
- pandas: K 线与技术指标计算
- httpx: 预留真实数据源接入

## 目录结构

```text
steam_market_mvp/
  app/
    api/
    collectors/
    services/
    config.py
    db.py
    main.py
    models.py
    schemas.py
  tests/
  .env.example
  requirements.txt
```

## 快速开始

1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. 复制环境变量文件

```bash
copy .env.example .env
```

3. 启动服务

```bash
uvicorn app.main:app --reload --app-dir .
```

4. 打开文档

```text
http://127.0.0.1:8000/docs
```

## 推荐调用顺序

1. `POST /api/v1/ingest/mock`
2. `GET /api/v1/items`
3. `GET /api/v1/items/{item_id}/candles`
4. `GET /api/v1/items/{item_id}/signals`
5. `GET /api/v1/items/{item_id}/summary`

## 真实数据源扩展

当前内置两个 collector：

- `mock`: 本地模拟 K 线，方便演示与调试
- `cs2sh`: 真实接口占位，补充鉴权后可接入

后续你可以继续新增：

- `buff.py`
- `youpin.py`
- `c5.py`
- `steamdt.py`

这些模块只需要输出统一的 `NormalizedQuote` 结构即可接入整个分析链路。

## 当前信号逻辑

- 趋势判断：`MA5` 与 `MA20`
- 动量判断：`RSI14`
- 买点提示：短均线上穿长均线，或 RSI 从低位回升
- 卖点提示：短均线走弱，或 RSI 进入高位

## 下一步建议

- 把 `SQLite` 换成 `PostgreSQL`
- 给 collector 加定时任务
- 补充多平台价差与手续费模型
- 接入消息告警
- 再加 AI 做自然语言解释
