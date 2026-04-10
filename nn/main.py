from fastapi import FastAPI, UploadFile, File
from fastapi.responses import PlainTextResponse
import os
from faster_whisper import WhisperModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from llama_cpp import Llama


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

LLM = Llama(
    model_path="/Users/tori/Documents/prog/ProgramFiles/saiga_yandexgpt_8b.Q4_K_S.gguf",  
    n_ctx=2048,      # Размер контекста (сколько токенов модель "помнит")
    n_threads=8,     # Количество потоков CPU 
    verbose=False   
)

PROMT_ANALYS = ' Выше представлен текст. Выдели ключевые темы из этого текста (если здесь несколько - напиши все, либо одна) и определи отношение автора текста к каждой из выделенных тобой тем. ответ дай в виде Формат ответа:[{ "topic": "название темы", "sentiment": "positive/negative/neutral", "explanation": "объяснение" }]'
PROMT_TRANSLATED_TEXT = " Выше написан текст с ошибками, ошибочными буквами или словами. Измени некоторые слова, в которых видишь ошибки, чтобы смысловой контекст сохранялся. Не меняй весь текст, не меняй смысл и структуру"


model = WhisperModel("base")

video_folder = "video"
output_folder = "texts"

os.makedirs(video_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# @app.post("/transcribe")
# async def transcribe_video(file: UploadFile = File(...)):
#     try: 
#         video_path = os.path.join(video_folder, file.filename)
        
#         # сохраняем видео на диск
#         with open(video_path, "wb") as f:
#             f.write(await file.read())
        
#         # транскрибируем
#         segments, _ = model.transcribe(video_path, language="ru")
#         text = " ".join([segment.text for segment in segments])
        
#         # сохраняем текст
#         output_path = os.path.join(output_folder, file.filename + ".txt")
#         with open(output_path, "w", encoding="utf-8") as f:
#             f.write(text)
        
#         return JSONResponse({"filename": file.filename, "text": text})
#     except Exception as e:
#         return JSONResponse({"error": str(e)}, status_code=500)
    
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
        response =  LLM(
            text + PROMT_TRANSLATED_TEXT,
            max_tokens=250,   # Максимум токенов в ответе
            temperature=0.7   # Температура (0 = детерминировано, 1 = креативно)
        )
        print(response["choices"][0]["text"])
        cleaned_text = response["choices"][0]["text"]
                # print("CHINA + BLONDE" + "-"*20)
        response = LLM(
            cleaned_text + PROMT_ANALYS,
            max_tokens=250,  
            temperature=0.7  
        )
        print(response["choices"][0]["text"])
        
        
        return JSONResponse({"filename": file.filename, "text": response["choices"][0]["text"]})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    