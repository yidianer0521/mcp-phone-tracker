import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app_status_db = {}
app = FastAPI(title="OPPO App Tracker")

# 升级后的写入接口：同时支持 Body 和 URL 参数抓取！
@app.get("/update")
@app.post("/update")
async def update_status(request: Request, app_name: str = None, event: str = None):
    try:
        # 如果 URL 参数里没有，就去 Body 里找
        if not app_name or not event:
            try:
                data = await request.json()
                app_name = data.get("app_name")
                event = data.get("event")
            except:
                pass
        
        # 抓取到了就记录
        if app_name and event:
            # 过滤掉没被替换的原始变量字符串，防止脏数据
            if "{" in app_name or "[" in app_name:
                return {"status": "error", "message": "变量未被手机正确替换"}
                
            status_map = {"open": "打开", "close": "关闭"}
            app_status_db[app_name] = status_map.get(event, event)
            return {"status": "success", "current_data": app_status_db}
            
        return JSONResponse(content={"status": "error", "message": "参数缺失"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.get("/mcp/status")
@app.post("/mcp/status")
async def get_mcp_status():
    if not app_status_db:
        text = "主人目前手机上所有监控的应用程序都处于关闭状态。"
    else:
        text = "这是主人手机上最新的应用程序运行状态：\n" + "\n".join([f"- {k} 的状态是：【{v}】" for k, v in app_status_db.items()])
    return {"result": text, "status": text}

@app.get("/")
async def root():
    return {"status": "running", "current_apps": app_status_db}
