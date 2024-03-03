import os,requests,json,re,markdown,yaml

def md_text(message):
    return markdown.markdown(message)
#格式化处理·markdown·

def find_and_remove_image_links(markdown_text):
    image_link_pattern = r'!\[.*\]\(.*\)\n?'
    links_only_pattern = r'!\[.*\]\((.*)\)'
    image_links = re.findall(links_only_pattern, markdown_text)
    modified_text = re.sub(image_link_pattern, '', markdown_text)
    modified_text = modified_text.rstrip('\n')
    return image_links, modified_text
#提取markdown中的图片链接

def tags_text(text):
    pattern = r'```(.*?)```'
    code_blocks = re.findall(pattern, text, re.DOTALL)
    for index, block in enumerate(code_blocks):
        text = text.replace(block, f"CODE_BLOCK_{index}")
    pattern = r'#(\w+)'
    tags = re.findall(pattern, text)
    
    replacement = r'<a class="tag" href="?tag=\1" data-pjax="">\1</a>'
    text = re.sub(pattern, replacement, text)

    for index, block in enumerate(code_blocks):
        text = text.replace(f"CODE_BLOCK_{index}", block)
    return text, list(set(tags))
#格式化处理·标签·


def process_code(text):
    def replace_code(match):
        code = match.group(0).split('\n', 1)[1].rsplit('\n', 1)[0]
        return '<pre><code>' + code + '</code></pre><p style=""></p>'
    pattern = r'```(.*?)```'
    text = re.sub(pattern, replace_code, text, 0, re.DOTALL)
    return text
#格式化处理·代码块·

def spotify(text):
    # 定义一个正则表达式来匹配Spotify歌曲链接
    spotify_id = r'https?://open.spotify.com/track/([0-9A-Za-z]+)'
    spotify_regex = r'https?://open\.spotify\.com/track/[0-9a-zA-Z]+(?:\?[^\s]*)?'
    # 找到所有匹配的Spotify歌曲链接
    track_ids = re.findall(spotify_id, text)
    
    urls = re.findall(spotify_regex,text)

    for Id,url in zip(track_ids,urls):
        iframe = f'<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{Id}?utm_source=generator" width="260" height="80" frameborder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        text = text.replace(url,iframe)
    return text
#生成spotify·卡片·


def get_external_link(url,createdTs,token,image_links):
    # 设置查询参数
    params = {
        'page': 1,
        'limit': 10
    }
    cookies = {
    'memos.access-token':token
}
    response = requests.get(url, cookies=cookies, params=params)
    data = json.loads(response.text)
    json_list = []
    for item in data:
        if item['createdTs'] == createdTs:
            if item['resourceList']:
                for i in item['resourceList']:
                    photo = i['externalLink']
                    myjson =  json.dumps({"type":"PHOTO","url":photo,"originType":"image/jpeg"})
                    myjson = json.loads(myjson)
                    json_list.append(myjson)
    for i in image_links:
        myjson =  json.dumps({"type":"PHOTO","url":i,"originType":"image/jpeg"})
        myjson = json.loads(myjson)
        json_list.append(myjson)
    return json_list
#获取·memos图片外部链接·


def myjson(s,date,tag,memos_url,createdTs,memos_token,image_links):
    photo=get_external_link(memos_url,createdTs,memos_token,image_links)
    tags_list = [] if tag is None else tag
    myjson={"spec":{"content":{"raw":s,"html":s,"medium":photo},"releaseTime":date,"owner":"","visible":"PUBLIC","tags":tags_list},"metadata":{"generateName":"moment-"},"kind":"Moment","apiVersion":"moment.halo.run/v1alpha1"}
    myjson = json.dumps(myjson)
    print(myjson)
    return myjson
#格式化处理输出·json·

def halo(text,memos_url,memos_token):

    tags = tags_text(text)
    tags_list = tags[1]
    text = tags[0]
    text = process_code(text)
    text = spotify(text)
    text = text.replace('\n', '\n\n')
    image_links, text = find_and_remove_image_links(text)#test 图片
    text = md_text(text)
    text = re.sub(r'^<p>', '', text, count=1)
    text = re.sub(r'</p>$', '', text, count=1)
    text = '<p style="">' + text + '</p>'
    date=os.environ.get('memos_date')
    createdTs=int(os.environ.get('createdTs'))
    return myjson(text,date,tags_list,memos_url,createdTs,memos_token,image_links)
#处理·halo·

with open('/config/config.yml', 'r') as file:
    data = yaml.safe_load(file)

# post_url = f"{data['halo']['url']}/apis/api.plugin.halo.run/v1alpha1/plugins/PluginMoments/moments"
post_url = f"{data['halo']['url']}/apis/console.api.moment.halo.run/v1alpha1/moments"
auth = f"Bearer {data['halo']['token']}"
memos_url = f"{data['memos']['url']}/api/v1/memo"
memos_token = data['memos']['token']

message = os.environ.get('MEMOS_MESSAGE')

memos = halo(message,memos_url,memos_token)

headers = {
    'Content-Type': 'application/json',
    'Authorization': auth
}
response = requests.post(post_url, headers=headers, data=memos)

print(response.status_code)
print(response.text)
