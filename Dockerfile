FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY . .
RUN uv sync
EXPOSE 7860
CMD ["uv", "run", "python", "cli.py", "serve"]
