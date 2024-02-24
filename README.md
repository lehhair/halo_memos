# 将你的memos发送到瞬间
使用 https://github.com/adnanh/webhook
## 构建docker镜像
```bash
git clone https://github.com/lehhair/halo_memos.git
cd halo_memos
docker build --no-cache -t halo_memos .
```
## 使用

创建一个目录，在目录下新建config.yml文件，内容如下：

```shell
mkdir halo_memos
cd halo_memos
touch config.yml
```

```yaml
halo:
  url: "https://halo.xxx"
  token: "pat_eyxxx"
memos:
  url: "https://memos.xxx"
  token: "eyxxx"
```

在配置文件所在目录运行

```shell
docker run -d --name halo_memos -p 9000:9000 -e LANG=C.UTF-8 -v "${PWD}/config.yml:/config/config.yml" --restart always lehhair/halo_memos:latest -verbose -hooks="/config/hooks.yml" -hotreload
```
最后将webhook地址填到memos
如同
`http://127.0.0.1:9000/hooks/memos`

本脚本只同步公开发布的memos，图片功能仅支持使用对象存储的memos

如果你恰好还和我一样使用misskey,可以使用如下脚本
```bash
#!/bin/bash

json_string=$1
token='eyxxx'

text=$(echo $json_string | jq '.body.note.text' | sed 's/^"//' | sed 's/"$//')
image_links=$(echo "$json_string" | jq -r '.body.note.files[] | select(.type | startswith("image")) | "![image](\(.url))"' | tr -d '\n')
content="#misskey\n$text\n$image_links"

curl -X POST \
     -H "Accept: application/json" \
     -H "Authorization: Bearer $token" \
     -H "Content-Type: application/json" \
     -d "{\"content\": \"$content\",\"visibility\": \"PUBLIC\"}" \
     https://memos/api/v1/memo
```
如果你希望只同步你的嘟文和回复你自己的可以用这个脚本，避免回复其他人没有引用部分造成不便
```bash
#!/bin/bash

json_string=$1
# echo $json_string >> /config/logfile.txt
token='eyxxx'

reply_id=$(echo $json_string | jq '.body.note.reply.userId')
note_id=$(echo $json_string | jq '.body.note.userId')

if [ "$reply_id" == "null" ] || [ "$reply_id" == "$note_id" ]; then
 text=$(echo $json_string | jq '.body.note.text' | sed 's/^"//' | sed 's/"$//')
 image_links=$(echo "$json_string" | jq -r '.body.note.files[] | select(.type | startswith("image")) | "![image](\(.url))"' | tr -d '\n')
 content="#misskey\n$text\n$image_links"
 curl -X POST \
 -H "Accept: application/json" \
 -H "Authorization: Bearer $token" \
 -H "Content-Type: application/json" \
 -d "{\"content\": \"$content\",\"visibility\": \"PUBLIC\"}" \
 https://memos/api/v1/memo
fi
```
docker命令,这个镜像额外增加了curl
```bash
docker run -d --name halo_memos -p 127.0.0.1:9000:9000 -e LANG=C.UTF-8 -v "${PWD}:/config" --restart always lehhair/halo_memos:curl -verbose -hooks="/config/hooks.yml" -hotreload
```
由于是挂载目录，需要你在目录提前放好配置文件和脚本，并且给脚本设置权限
