from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
import os
from faster_whisper import WhisperModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost:5173",  
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # список разрешённых фронтендов
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST и т.д.
    allow_headers=["*"],         # все заголовки
)

model = WhisperModel("base")

video_folder = "video"
output_folder = "texts"

os.makedirs(video_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

@app.post("/transcribe")
async def transcribe_video(file: UploadFile = File(...)):
    try: 
        video_path = os.path.join(video_folder, file.filename)
        
        # сохраняем видео на диск
        with open(video_path, "wb") as f:
            f.write(await file.read())
        
        # транскрибируем
        segments, _ = model.transcribe(video_path, language="ru")
        text = " ".join([segment.text for segment in segments])
        
        # сохраняем текст
        output_path = os.path.join(output_folder, file.filename + ".txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        return JSONResponse({"filename": file.filename, "text": text})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
