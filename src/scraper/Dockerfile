FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y \
    nss \
    atk \
    at-spi2-atk \
    cups-libs \
    libXcomposite \
    libXdamage \
    libXrandr \
    mesa-libgbm \
    pango \
    gtk3 \
    alsa-lib \
    libxkbcommon \
    libXScrnSaver \
    && dnf clean all

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium

COPY app.py .

CMD ["app.lambda_handler"]