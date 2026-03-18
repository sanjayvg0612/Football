import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Football API Gateway")

# Allow CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 172.17.0.1 is the default host IP from inside a Linux Docker container
LIVE_SCORE_SERVICE_URL = "http://172.17.0.1:8081"
FIXTURE_SERVICE_URL = "http://172.17.0.1:8082"

@app.api_route("/api/live-scores/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def proxy_live_scores(request: Request, path: str):
    url = f"{LIVE_SCORE_SERVICE_URL}/api/live-scores/{path}"
    
    client = httpx.AsyncClient()
    
    # Handle Server-Sent Events (SSE) streaming for live scores
    if "stream" in path:
        async def event_generator():
            async with client.stream(request.method, url, headers=dict(request.headers)) as response:
                async for chunk in response.aiter_raw():
                    yield chunk
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    
    # Standard REST proxy logic
    body = await request.body()
    response = await client.request(
        method=request.method,
        url=url,
        headers=dict(request.headers),
        content=body
    )
    headers = dict(response.headers)
    headers.pop("transfer-encoding", None) # FastAPI/Uvicorn handles this
    
    return Response(content=response.content, status_code=response.status_code, headers=headers)


@app.api_route("/api/fixtures/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def proxy_fixtures(request: Request, path: str):
    url = f"{FIXTURE_SERVICE_URL}/api/fixtures/{path}"
    
    async with httpx.AsyncClient() as client:
        body = await request.body()
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=body
        )
        headers = dict(response.headers)
        headers.pop("transfer-encoding", None) 
        headers.pop("content-encoding", None) # Proxy uncompressed response back up
        return Response(content=response.content, status_code=response.status_code, headers=headers)

if __name__ == "__main__":
    # Runs the Python gateway on the same port 8080 as the Java one did
    uvicorn.run(app, host="0.0.0.0", port=8080)
