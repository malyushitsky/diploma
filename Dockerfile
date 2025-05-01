FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel

WORKDIR /code
COPY requirements/requirements-celery.txt /tmp/requirements.txt

RUN pip install --upgrade pip wheel setuptools \
 && pip install --no-cache-dir -r /tmp/requirements.txt \
      --extra-index-url https://huggingface.github.io/bnb-nn/wheels/cu121/ \
 || true   # wheel может не найтись → пойдём собирать

RUN python - << 'PY' \
 || ( \
      apt-get update && apt-get install -y --no-install-recommends \
          git build-essential cmake && \
      git clone --depth 1 --branch 0.45.0 \
          https://github.com/bitsandbytes-foundation/bitsandbytes.git && \
      cd bitsandbytes && \
      TORCH_CUDA_ARCH_LIST=8.9 make CUDA_VERSION=12.1 && \
      pip install . && \
      cd .. && rm -rf bitsandbytes \
 )


COPY . .

ENV PYTHONPATH=/code

CMD ["celery", "-A", "celery_worker", "worker", "--loglevel=info", "--pool=solo"]
