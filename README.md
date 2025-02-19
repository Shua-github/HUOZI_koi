
# HUOZI
电棍活字印刷后端
基于 FastAPI 框架
## 食用方法
### Python 版本
- 理论`3.8`以上均可(我是使用`3.12.6`)
### 部署步骤
1. 克隆项目仓库：
```bash
git clone https://github.com/Shua-github/HUOZI_koi.git
cd HUOZI_koi
```
2. 执行脚本
- `Windows`请执行`Windows.bat`

- `Macos`和`Liunx`请执行`Macos丨Liunx.sh`

3. 修改配置：
- 如果有需要，你可以根据 `config.yaml` 修改配置

4. 运行程序
- ```python app.py```

5. 查看API文档：
- 在浏览器中访问 [http://127.0.0.1:8989/docs](http://127.0.0.1:8989/docs) (默认端口为 8989，可以在 `config.yaml` 中更改)


## 使用 API 调用
你可以通过 API 来生成音频，以下是使用示例：
### API 端点
- `GET,POST /api/make`

### 请求参数
- `text` (字符串): 要转换的文本
- `inYsddMode` (布尔值): 是否启用 Ysdd 模式 (`true`/`false`)
- `norm` (布尔值): 是否启用 norm 模式 (`true`/`false`)
- `reverse` (布尔值): 是否启用反转模式 (`true`/`false`)
- `speedMult` (浮点数): 速度倍增器 (0.5 - 2.0)
- `pitchMult` (浮点数): 音高倍增器 (0.5 - 2.0)
### 示例请求
**GET 请求示例：**
```
http://127.0.0.1:8989/api/make?text=你好啊&inYsddMode=false&norm=false&reverse=false&speedMult=1.0&pitchMult=1.0
```
### 响应格式
- 成功响应：
```json
{
    "code": 200,
    "id": "<生成的文件ID>",
    "file_path": "<生成的文件url>"
}
```
- 错误响应：
```json
{
    "code": 400,
    "message": "<错误信息>"
}
```
