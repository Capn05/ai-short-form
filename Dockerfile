FROM python:3.10-slim-bookworm

# System deps: FFmpeg + all Chromium runtime libraries installed manually
# (avoids playwright install-deps which has broken font package names on Debian trixie)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    # Chromium runtime
    libnss3 libnspr4 \
    libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 \
    libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 \
    libx11-6 libxcb1 libxext6 libxshmfence1 \
    libasound2 \
    # Fonts
    fonts-liberation fonts-noto-color-emoji fonts-unifont \
    wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install browser binary only — deps already installed above
RUN playwright install chromium

COPY . .
RUN mkdir -p output/runs data
