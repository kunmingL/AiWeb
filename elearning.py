import modelsLoad
#读取文件
def readFile(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        #读取行拼接
        lines = ''.join(lines)
    return lines

#给大模型输入
def Qwen_Chat(model,tokenizer,prompt):
    messages = [
        {"role": "system", "content": "你叫小千，你是一位英语老师，你需要将输入给你的单词列表整理，按照艾宾浩斯循环学习法，生成每天需要背诵的单词"},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512,
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    output_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print("answer", output_text)

if __name__ == '__main__':
    #调用模型加载
    model_name = r"D:/AI/models/Qwen2.5-7B-Instruct"
    model = modelsLoad.modlesload(model_name)
    tokenizer = modelsLoad.tokenizerload(model_name)
    # 让AI读取文件，并分析按照格式输出内容，生成每天的学习计划
    demand = '''提取文件,从day01到day15的内容：
1、重点单词+中文释义
2、句子+中文释义
3、以day01为第一天、day02为第二天，以此内推到day15
4、按照以下格式提取：
第一天
Esentence:句子1
Csentence:中文释义
words：{(单词1，中文释义),(单词2,中文释义)...}

Esentence:句子2
Csentence:中文释义
words：{(单词1，中文释义),(单词2,中文释义)...}
....
第二天
....'''
    message = [{'role': 'system', 'content': '你是我的文件处理助手，你需要帮我提取这个文件里的内容'},
                {'role': 'user', 'content': demand}]
    text = tokenizer.apply_chat_template(
        message,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(response)

