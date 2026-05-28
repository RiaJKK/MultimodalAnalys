from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
from llama_cpp import Llama
import os


# ── Config ────────────────────────────────────────────────────────────────────

ORIGINS = ["http://localhost:5173", "http://localhost:5174"]

VIDEO_DIR = "video"
TEXT_DIR  = "texts"

LLM_MODEL_PATH = "/Users/tori/Documents/prog/ProgramFiles/saiga_yandexgpt_8b.Q4_K_S.gguf"

PROMPT_CLEAN = (
    "Выше написан текст с ошибками, ошибочными буквами или словами. "
    "Измени слова, в которых видишь ошибки, чтобы смысловой контекст сохранялся. "
    "Не меняй смысл и структуру текста."
)

PROMPT_ANALYZE = (
    "Выше представлен текст. Выдели ключевые темы "
    "(если их несколько — перечисли все) и определи отношение автора к каждой теме. "
    'Формат ответа: [{"topic": "...", "sentiment": "positive/negative/neutral", "explanation": "..."}]'
)


# ── Startup ───────────────────────────────────────────────────────────────────

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(TEXT_DIR,  exist_ok=True)

whisper = WhisperModel("base")

llm = Llama(
    model_path=LLM_MODEL_PATH,
    n_ctx=2048,
    n_threads=8,
    verbose=False,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def llm_complete(prompt: str, max_tokens: int = 250) -> str:
    result = llm(prompt, max_tokens=max_tokens, temperature=0.7)
    return result["choices"][0]["text"]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        video_path = os.path.join(VIDEO_DIR, file.filename)

        with open(video_path, "wb") as f:
            f.write(await file.read())

        segments, _ = whisper.transcribe(video_path, language="ru")
        raw_text = " ".join(seg.text for seg in segments)

        with open(os.path.join(TEXT_DIR, file.filename + ".txt"), "w", encoding="utf-8") as f:
            f.write(raw_text)

        cleaned  = llm_complete(raw_text + "\n\n" + PROMPT_CLEAN)
        analysis = llm_complete(cleaned  + "\n\n" + PROMPT_ANALYZE)

        return JSONResponse({"filename": file.filename, "analysis": analysis})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
