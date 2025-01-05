from fastapi import FastAPI, Request, HTTPException, Query, Form
from fastapi.responses import FileResponse, JSONResponse
from huoZiYinShua import *
from pathlib import Path
import time
import secrets
from threading import Lock
import logging
import sys
import yaml
app = FastAPI()

# 读取配置
with open("config.yaml", "r",encoding="utf-8") as file:
    config = yaml.safe_load(file)

# 临时文件目录
temp_output_path = Path(config["paths"]["temp_output_path"])
temp_output_path.mkdir(parents=True, exist_ok=True)

# 日志文件
log_path = Path(config["logging"]["log_path"])
log_path.mkdir(parents=True, exist_ok=True)
log_path_name = log_path / config["logging"]["log_name"]

# 印刷音频音频
audio_source = config["paths"]["audio_path"]

# 进程锁
locker = Lock()
queue_record = {"time": 0, "place": 0}

# 日志设置
hzysLogger = logging.getLogger("hzys")
if not hzysLogger.handlers:
    hzysFileHandler = logging.FileHandler(f"{log_path_name}", encoding=config["logging"]["encoding"], mode="a")
    hzysFormatter = logging.Formatter(config["logging"]["format"])
    hzysFileHandler.setFormatter(hzysFormatter)
    hzysLogger.addHandler(hzysFileHandler)
    hzysLogger.addHandler(logging.StreamHandler(sys.stdout))
    level = getattr(logging, config["logging"]["level"].upper(), None)
hzysLogger.setLevel(level)

# 生成唯一 ID
def makeid():
    with locker:
        current_sec = str(int(time.time()))
        if queue_record["time"] != current_sec:
            queue_record["time"] = current_sec
            queue_record["place"] = 0
        id = f"{current_sec}_{queue_record['place']}_{secrets.token_hex(8)}"
        queue_record["place"] += 1
        return id

# 清理缓存
def clear_cache():
    while True:
        current_time = int(time.time())
        for file_name in temp_output_path.iterdir():
            try:
                time_created = int(file_name.stem.split("_")[0])
                if current_time - time_created > config["cleanup"]["interval"]:
                    file_name.unlink()
            except:
                pass
        time.sleep(config["cleanup"]["file_lifetime"])

# 文件下载接口
@app.get("/file/{file_name}")
async def get_audio(file_name: str):
    file_path = temp_output_path / file_name
    if file_path.exists():
        return FileResponse(
            path=file_path,
            media_type="audio/wav",
            filename=file_name,
        )
    raise HTTPException(status_code=404, detail="没有这个文件")

# 处理生成音频请求
@app.get("/api/make")
async def api_make_get(
    request:Request,
    text: str = Query(...),
    inYsddMode: bool = Query(True),
    norm: bool = Query(True),
    reverse: bool = Query(True),
    speedMult: float = Query(1.0),
    pitchMult: float = Query(1.0),
):
    return await process_make_request(request, text, inYsddMode, norm, reverse, speedMult, pitchMult)

# 处理生成音频请求
@app.post("/api/make")
async def api_make_post(
    request: Request,
    text: str = Form(...),
    inYsddMode: bool = Form(True),
    norm: bool = Form(True),
    reverse: bool = Form(True),
    speedMult: float = Form(1.0),
    pitchMult: float = Form(1.0),
):
    return await process_make_request(request, text, inYsddMode, norm, reverse, speedMult, pitchMult)

async def process_make_request(
    request: Request,
    text: str,
    inYsddMode: bool,
    norm: bool,
    reverse: bool,
    speedMult: float,
    pitchMult: float,
):
    # 检查输入文本长度
    if not text or len(text) > 100:
        return JSONResponse(status_code=400, content={"code": 400, "message": "憋刷辣!"})

    # 检查参数范围
    if speedMult < 0.5 or speedMult > 2 or pitchMult < 0.5 or pitchMult > 2:
        return JSONResponse(status_code=400, content={"code": 400, "message": "你在搞什么飞机?"})

    try:
        # 生成 ID 和处理音频
        id = makeid()
        HZYS = huoZiYinShua(audio_source)
        file_path = temp_output_path / f"{id}.wav"
        HZYS.export(
            text,
            filePath=str(file_path),
            inYsddMode=inYsddMode,
            norm=norm,
            reverse=reverse,
            speedMult=speedMult,
            pitchMult=pitchMult,
        )

        # 构造文件 URL
        file_url = str(request.url_for("get_audio", file_name=f"{id}.wav"))

        return JSONResponse(
            status_code=200,
            content={"code": 200, "id": id, "file_url": file_url},
        )

    except Exception as e:
        hzysLogger.error("生成失败: %s", e)
        return JSONResponse(status_code=400, content={"code": 400, "message": "生成失败"})

if __name__ == '__main__':
    from threading import Thread
    # 启动缓存清理
    Thread(target=clear_cache, daemon=True).start()
    # 启动应用
    from uvicorn import run
    run(app,port=config["app"]["port"], host=config["app"]["host"])