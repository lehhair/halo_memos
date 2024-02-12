使用 https://github.com/adnanh/webhook
# 将你的memos发送到瞬间

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
