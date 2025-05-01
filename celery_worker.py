from celery_app import celery
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, pipeline
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma
from FlagEmbedding import FlagReranker
from app import celery_globals

@celery.on_after_configure.connect
def setup_globals(sender, **kwargs):
    print("Инициализация глобальных компонентов Celery...")
    
    # LLM
    model_name = "t-bank-ai/T-lite-instruct-0.1"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    quant_config = BitsAndBytesConfig(load_in_8bit=True)
    model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=quant_config, device_map="auto")

    celery_globals.llm = pipeline("text-generation", model=model, tokenizer=tokenizer, return_full_text=False)
    celery_globals.terminators = list({
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>") or tokenizer.eos_token_id,
    })

    # Embedder
    celery_globals.embedding_model = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"}
    )

    # Reranker
    celery_globals.reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)

    # Vectorstore
    celery_globals.vectorstore = Chroma(
        persist_directory="chroma_storage",
        embedding_function=celery_globals.embedding_model
    )

    print("Глобальные компоненты Celery инициализированы.")