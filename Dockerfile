FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 HOST=0.0.0.0
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pybr_certificados ./pybr_certificados
COPY assets ./assets
COPY data/exemplo.csv ./data/exemplo.csv
EXPOSE 8000
CMD ["python", "-m", "pybr_certificados"]
