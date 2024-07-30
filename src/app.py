# app.py
import sys
import os
import netifaces
from fastapi import FastAPI, HTTPException, Request, UploadFile, Form, File

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transformer import handle_file_upload, transcribe_audio

app = FastAPI()

def get_local_ips():
    local_ips = set()
    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for addr_info in addresses[netifaces.AF_INET]:
                local_ips.add(addr_info['addr'])
    return local_ips

local_ips = get_local_ips()
print(f"Local IPs: {local_ips}")

@app.middleware("http")
async def check_request_origin(request: Request, call_next):
    client_host = request.client.host
    if client_host not in local_ips:
        raise HTTPException(status_code=403, detail="Forbidden: requests from this host are not allowed")
    response = await call_next(request)
    return response

@app.post("/update/")

async def transformation_flow(file: UploadFile = File(...),
                            clientId: str = Form(...),  
                            segment_number: str = Form(default='unknown')):
    print(f"Request file: {file.filename}")
    print(f"User ID: {clientId}")
    print(f"Segment Number: {segment_number}")

    filepath, filename = handle_file_upload(clientId, file, segment_number )
    transcription = transcribe_audio(filepath)

    if int(os.getenv('TRANSCRIPTION_OUT_LOG', '0')) == 1:
        sys.stdout.reconfigure(encoding='utf-8')
        print(f"User ID: {clientId}")
        print(f'File {filename}, Transcription: {transcription}')

    os.remove(filepath)
    if transcription:
        return {"translated_text":transcription}
    else:
        raise HTTPException(status_code=500, detail="Invalid transformation")


if __name__ == "__main__":
    import hypercorn.asyncio
    import asyncio

    async def main():
        config = hypercorn.Config()
        config.bind = ["0.0.0.0:8338"]
        config.workers = 4
        await hypercorn.asyncio.serve(app, config)

    asyncio.run(main())