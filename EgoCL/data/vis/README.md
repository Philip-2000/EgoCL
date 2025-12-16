# 视频回环自检服务（FastAPI）

一个最小可用的本地网络服务：在浏览器播放本地视频（支持 Range/分段加载），并在进度条下方可视化多行标注轨道；当播放到某段时，在下方显示对应的标注文本。

## 功能
- FastAPI 提供页面与接口
- HTML5 `<video>` + Range 流式传输，支持没一次性加载完整视频
- 多行标注轨道（每行一个类别），小色块表示该时间段有标注
- 播放到对应时间时，在页面下方显示该时刻命中的标注
- 数据源可插拔：当前提供一个基于 JSON 的本地数据源，后续可替换为数据库/服务

## 目录结构
```
./main.py                 # FastAPI 入口
./templates/index.html    # 前端页面
./static/app.js           # 前端逻辑
./static/styles.css       # 样式
./datasources/            # 数据源接口与实现
./sample_data/            # 示例数据（放视频与 annotations.json）
```

## 运行
1. 安装依赖（建议使用虚拟环境）：

```bash
pip install fastapi "uvicorn[standard]" jinja2
```

2. 放置一个测试视频文件到 `sample_data/sample.mp4`（或修改 `sample_data/annotations.json` 中的 `path` 指向你的实际视频路径）。

3. 启动服务：

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

4. 打开浏览器访问：

```
http://127.0.0.1:8000/
```

## 自定义与扩展
- 切换/配置数据源：
  - 目前通过 `LocalJsonDataSource` 读取 `VIS_ANNOTATIONS_JSON`（默认 `./sample_data/annotations.json`）与 `VIS_VIDEOS_BASE_DIR`（默认 `./sample_data`）。
  - 你可以通过环境变量覆盖：

```bash
export VIS_ANNOTATIONS_JSON=/path/to/annotations.json
export VIS_VIDEOS_BASE_DIR=/path/to/videos
```

- 新增/替换数据源：
  - 参考 `datasources/base.py` 定义一个类实现 `BaseVideoDataSource`
  - 在 `main.py` 中将 `DATA_SOURCE = LocalJsonDataSource(...)` 替换为你的实现，并根据需要读取配置

- 注释/标注数据格式（示例）：
```json
{
  "videos": [
    {
      "id": "sample",
      "title": "示例视频",
      "path": "sample.mp4",
      "mime_type": "video/mp4",
      "annotations": [
        { "category": "事件", "start": 1, "end": 10, "label": "和李华一起吃饭" },
        { "category": "事件", "start": 10, "end": 50, "label": "吃完饭去洗碗" }
      ]
    }
  ]
}
```

- 前端：
  - 页面加载后请求 `/api/videos` 获取可播放视频列表
  - 切换视频后请求 `/api/videos/{id}/annotations` 获取标注
  - 通过 `<video>` 的 `timeupdate` 事件实时计算当前命中标注并展示

## 注意事项
- 本项目默认仅用于本机自检，不做鉴权。若对外提供需加上认证与权限控制。
- 视频流支持标准 HTTP Range 请求，常见浏览器/视频控件会自动使用支持拖拽进度。
- 若播放卡顿，检查磁盘 IO、网络、以及是否为远程存储路径。

## 许可
本示例仅用于演示，按需修改集成到你的工程中。
