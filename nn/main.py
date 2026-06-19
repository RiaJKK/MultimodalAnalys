from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
from llama_cpp import Llama
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

try:
    import cv2
    from paddleocr import PaddleOCR
    _OCR_AVAILABLE = True
except Exception:
    _OCR_AVAILABLE = False



ORIGINS = ["http://localhost:5173", "http://localhost:5174"]

VIDEO_DIR = "video"
TEXT_DIR  = "texts"

LLM_MODEL_PATH = "/Users/tori/Documents/prog/ProgramFiles/saiga_yandexgpt_8b.Q4_K_S.gguf"

OCR_FRAME_STEP      = 30   
OCR_CONF_THRESHOLD  = 0.7  
JACCARD_THRESHOLD   = 0.5   

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

try:
    ocr_engine = PaddleOCR(lang="ru") if _OCR_AVAILABLE else None
except Exception:
    ocr_engine = None

_executor = ThreadPoolExecutor(max_workers=4)

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


def transcribe_audio(video_path: str) -> str:
    """Транскрибирование аудиодорожки через Faster-Whisper."""
    segments, _ = whisper.transcribe(video_path, language="ru")
    return " ".join(seg.text for seg in segments)


def extract_ocr_text(video_path: str) -> str:
    """Покадровый обход видео, сбор текста с кадров через PaddleOCR."""
    if not _OCR_AVAILABLE or ocr_engine is None:
        return ""
    cap = cv2.VideoCapture(video_path)
    collected, idx = [], 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if idx % OCR_FRAME_STEP == 0:
            result = ocr_engine.ocr(frame, cls=True)
            for line in (result or []):
                for box in (line or []):
                    text, conf = box[1][0], box[1][1]
                    if conf >= OCR_CONF_THRESHOLD:
                        collected.append(text)
        idx += 1
    cap.release()
    return " ".join(collected)


def jaccard(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def merge_asr_ocr(asr_text: str, ocr_text: str) -> str:
    """Дополняет ASR-транскрипт уникальными OCR-фрагментами.
    Дубликаты (Jaccard >= JACCARD_THRESHOLD) отбрасываются."""
    ocr_chunks = [c.strip() for c in ocr_text.split(".") if c.strip()]
    asr_sentences = [s.strip() for s in asr_text.split(".") if s.strip()]
    extra = []
    for chunk in ocr_chunks:
        if all(jaccard(chunk, sent) < JACCARD_THRESHOLD for sent in asr_sentences):
            extra.append(chunk)
    if extra:
        return asr_text.rstrip() + ". " + ". ".join(extra)
    return asr_text


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        video_path = os.path.join(VIDEO_DIR, file.filename)

        with open(video_path, "wb") as f:
            f.write(await file.read())

        loop = asyncio.get_event_loop()

        asr_task = loop.run_in_executor(_executor, transcribe_audio, video_path)
        ocr_task = loop.run_in_executor(_executor, extract_ocr_text, video_path)
        raw_asr, ocr_text = await asyncio.gather(asr_task, ocr_task)

        with open(os.path.join(TEXT_DIR, file.filename + ".txt"), "w", encoding="utf-8") as f:
            f.write(raw_asr)

        combined = merge_asr_ocr(raw_asr, ocr_text)
        cleaned  = llm_complete(combined + "\n\n" + PROMPT_CLEAN)
        analysis = llm_complete(cleaned  + "\n\n" + PROMPT_ANALYZE)

        return JSONResponse({"filename": file.filename, "analysis": analysis})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
