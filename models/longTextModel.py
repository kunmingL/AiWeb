import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

file_object = client.files.create(file=Path("./01-04.pdf"), purpose="file-extract")
print(file_object.id)

completion = client.chat.completions.create(
    model="qwen-long",
    messages=[
        {'role': 'system', 'content': '你是我的文件处理助手，你需要帮我提取这个文件里的内容'},
        {'role': 'system', 'content': 'fileid://'+file_object.id},
        {'role': 'user', 'content': '''提取文件,从day01到day15的内容：
1、重点单词+中文释义
2、句子+中文释义
3、以day01为第一天、day02为第二天，以此内推到day15
4、以json格式进行输出每个要素
5、按照以下格式提取：
第一天
Esentence:句子1
Csentence:中文释义
words：{(单词1，中文释义),(单词2,中文释义)...}

Esentence:句子2
Csentence:中文释义
words：{(单词1，中文释义),(单词2,中文释义)...}
....
第二天
....'''}
    ]
)
print(completion.choices[0].message.content)

