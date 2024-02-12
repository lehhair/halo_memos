#!/bin/bash

export MEMOS_MESSAGE=$(echo $1 | jq -r '.memo.content')
export createdTs=$(echo $1 | jq -r '.memo.createdTs')

export memos_date=$(date -u +%FT%TZ)
if [ "$(echo $1 | jq -r '.memo.visibility')" == "PUBLIC" ] && [ "$(echo $1 | jq -r '.activityType')" == "memos.memo.created" ]; then
  ./config/app
else
  # echo "bad" >> /config/logfile.txt
  echo "非公开发布请求"
fi