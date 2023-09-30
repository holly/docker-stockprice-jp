FROM python:3.11 AS python-selenium-builder
ENV DEBIAN_FRONTEND noninteractive
ENV LS_COLORS di=01;36

COPY app/ /app
WORKDIR /app

RUN --mount=type=cache,target=/var/lib/apt/lists --mount=type=cache,target=/var/cache/apt/archives \
    apt update \
 && apt -y install zip \
 && mkdir python \
 && cd python \
 && pip install --no-cache-dir  -r ../requirements.txt -t ./ \
 && find ./ -type d -name __pycache__ | xargs rm -frv \
 && curl -LO https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.92/linux64/chromedriver-linux64.zip \
 && unzip chromedriver-linux64.zip  \
 && rm -f chromedriver-linux64.zip \
 && chmod +x /app/stockprice_jp.py \
 && cd ../ 


FROM python:3.11 AS executor
ENV DEBIAN_FRONTEND noninteractive
ENV LS_COLORS di=01;36

COPY --from=python-selenium-builder /app /app
WORKDIR /app

RUN --mount=type=cache,target=/var/lib/apt/lists --mount=type=cache,target=/var/cache/apt/archives \
    apt update \
 && apt -y install vim vim-common vim-runtime libasound2 libatspi2.0-0 libatk-bridge2.0-0 libdrm2 libgtk-3-0 libgbm1 libnspr4 libnss3 libu2f-udev libvulkan1  libxkbcommon0 xdg-utils fonts-liberation fonts-liberation \
 && curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && dpkg -i google-chrome-stable_current_amd64.deb \
 && rm -f google-chrome-stable_current_amd64.deb \
 && curl -L https://raw.githubusercontent.com/holly/dotfiles/main/.vimrc -o ~/.vimrc \
 && cd ../ 

#CMD [ "/bin/bash" ]
ENTRYPOINT [ "/app/stockprice_jp.py" ]
