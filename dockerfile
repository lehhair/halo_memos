FROM golang:alpine AS BUILD_IMAGE

RUN apk update && apk add curl gcc libc-dev --no-cache

WORKDIR /go/src/github.com/adnanh/webhook
COPY webhook.version .
RUN curl -#L -o webhook.tar.gz https://api.github.com/repos/adnanh/webhook/tarball/$(cat webhook.version) && \
    tar -xzf webhook.tar.gz --strip 1 && \
    go get -d && \
    go build -ldflags="-s -w" -o /usr/local/bin/webhook


FROM python:alpine AS PYTHON_BUILD
RUN apk add --no-cache curl jq tini binutils && \
    apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install --no-cache-dir markdown requests pyyaml pyinstaller && \
    apk del .build-deps  # remove build dependencies
WORKDIR /src
COPY app.py .  
RUN pyinstaller --onefile app.py

FROM alpine:latest
RUN apk add --no-cache bash jq tini
COPY --from=BUILD_IMAGE /usr/local/bin/webhook /usr/local/bin/webhook
COPY --from=PYTHON_BUILD /src/dist/app /memos/app
COPY ./config/hooks.yml /config/hooks.yml
COPY ./config/memos.sh /config/memos.sh
RUN chmod +x /config/memos.sh
RUN chmod +x /memos/app
WORKDIR /config
EXPOSE 9000

ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/webhook"]
CMD ["-verbose", "-hotreload", "-hooks=hooks.yml"]
