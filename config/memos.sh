#!/bin/bash
export MEMOS_MESSAGE=$(echo $1 | jq -r '.memo.content')
export createdTs=$(echo $1 | jq -r '.memo.createdTs')
# export memos_date=$(date -u +%FT%TZ)
export memos_date=$(date -u -d @"$createdTs" +%FT%TZ)
export activity=$(echo $1 | jq -r '.activityType')
if [ "$(echo $1 | jq -r '.memo.visibility')" == "PUBLIC" ]; then
  ./memos/app
else
  # echo $1 >> /config/logfile.txt
  echo "非公开请求"
fi
