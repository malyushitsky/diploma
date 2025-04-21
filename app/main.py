from fastapi import FastAPI
from app.api import ingest, ask, summarize
from contextlib import asynccontextmanager
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma
from FlagEmbedding import FlagReranker
import torch

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Инициализирует LLM pipeline при старте FastAPI
    """
    # LLM
    model_name = "t-bank-ai/T-lite-instruct-0.1"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    quant_config = BitsAndBytesConfig(load_in_8bit=True)
    model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config, device_map="auto")
    app.state.llm = pipeline("text-generation", model=model, tokenizer=tokenizer)

    # Embedder
    app.state.embedding_model = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"}
    )

    # Reranker
    app.state.reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)

    # Chroma
    app.state.vectorstore = Chroma(persist_directory="chroma_storage", embedding_function=app.state.embedding_model)

    yield



app = FastAPI(title="arXiv RAG API", lifespan=lifespan)

# Подключаем маршруты
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(summarize.router, prefix="/summarize", tags=["Summarize"])
app.include_router(ask.router, prefix="/question_answer", tags=["QA"])


@app.get("/")
def root():
    return {"message": "arXiv RAG API"}