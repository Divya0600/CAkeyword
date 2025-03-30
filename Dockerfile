
FROM python:3.10-slim AS build

WORKDIR /usr/app
RUN python -m venv /usr/app/venv
ENV PATH="/usr/app/venv/bin:$PATH"

RUN python -m pip install --upgrade pip
RUN apt upgrade perl-base

COPY ./requirements.txt ./
# COPY ./pip.conf /root/.config/pip/pip.conf

COPY ./ranking_features-0.2.3-py3-none-any.whl ./

RUN pip install -r requirements.txt
RUN pip install ranking_features-0.2.3-py3-none-any.whl

RUN python -m spacy download en_core_web_sm
RUN python -m spacy download fr_core_news_sm

#Remove pip.conf so that we don't expose token
# RUN rm /root/.config/pip/pip.conf

FROM python:3.10-slim

RUN adduser --disabled-password worker

RUN chgrp -R 0 /home/worker && \
    chmod -R g=u /home/worker

USER worker
WORKDIR /home/worker
COPY --from=build /usr/app/venv /home/worker/venv

COPY --chown=worker:worker /data /home/worker/data
COPY --chown=worker:worker /src /home/worker/src

ENV PATH="/home/worker/venv/bin:$PATH"

EXPOSE 8080

CMD python -m uvicorn src.main:app --reload --port 8080 --host 0.0.0.0