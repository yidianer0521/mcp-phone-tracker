import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import json

app = FastAPI(title="App Tracker with Duration")

# 存储结构：{app_name: {"status": "打开/关闭", "start_time": "ISO时间"}}
app_status_db = {}

@app.get("/update")
@app.post("/update")
async def update_status(request: Request, app_name: str = None, event: str = None):
    try:
        if not app_name or not event:
            try:
                data = await request.json()
                app_name = data.get("app_name")
                event = data.get("event")
            except:
                pass

        if app_name and event:
            if "{" in app_name or "[" in app_name:
                return {"status": "error", "message": "变量未被手机正确替换"}

            now = datetime.now().isoformat()
            if event == "open":
                app_status_db[app_name] = {
                    "status": "打开",
                    "start_time": now
                }
            elif event == "close":
                duration = 0
                if app_name in app_status_db and app_status_db[app_name].get("start_time"):
                    start = datetime.fromisoformat(app_status_db[app_name]["start_time"])
                    duration = (datetime.now() - start).total_seconds()
                app_status_db[app_name] = {
                    "status": "关闭",
                    "duration_seconds": round(duration, 1)
                }
            return {"status": "success", "current_data": app_status_db}
        return JSONResponse(content={"status": "error", "message": "参数缺失"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.get("/mcp/status")
@app.post("/mcp/status")
async def get_mcp_status():
    if not app_status_db:
        text = "朱典宜目前手机上所有监控的应用程序都处于关闭状态，也就是说朱典宜现在没有在玩手机。"
    else:
        lines = []
        is_using = any(info.get("status") == "打开" for info in app_status_db.values())
        
        for app_name, info in app_status_db.items():
            status = info.get("status", "未知")
            if status == "打开":
                start = datetime.fromisoformat(info["start_time"])
                duration = (datetime.now() - start).total_seconds()
                lines.append(f"- {app_name} 的状态是：【打开】，已持续使用 {duration:.1f} 秒")
            else:
                duration = info.get("duration_seconds", 0)
                if duration > 0:
                    lines.append(f"- {app_name} 的状态是：【关闭】，本次使用了 {duration:.1f} 秒")
                else:
                    lines.append(f"- {app_name} 的状态是：【关闭】")
        
        if is_using:
            summary = "朱典宜当前正在使用手机。以下是各应用的最新状态：\n"
        else:
            summary = "朱典宜当前没有在玩手机。以下是各应用的最新状态（最近关闭的会显示时长）：\n"
        
        text = summary + "\n".join(lines)
    return {"result": text, "status": text}

@app.get("/")
async def root():
    return {"status": "running", "current_apps": app_status_db}
