import json
import englishobject
import edge_tts
import os

language_speaker = {
    "ja" : "ja-JP-NanamiNeural",            # ok
    "fr" : "fr-FR-DeniseNeural",            # ok
    "es" : "ca-ES-JoanaNeural",             # ok
    "de" : "de-DE-KatjaNeural",             # ok
    "zh" : "zh-CN-XiaoyiNeural",            # ok
    "en" : "en-US-AnaNeural",               # ok
    "ja": "ja-JP-NanamiNeural",            # ok
    "fr": "fr-FR-DeniseNeural",            # ok
    "es": "ca-ES-JoanaNeural",             # ok
    "de": "de-DE-KatjaNeural",             # ok
    "zh": "zh-CN-XiaoyiNeural",            # ok
    "en": "en-US-AnaNeural",               # ok
}

#加载文件并输出对象
def load_object_from_json(file_path):
# 加载文件并输出对象
def load_objects_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    objectList = []
    object_list = []
    for temp in data:
        print(temp['content'])
        for tmpcontent in temp['content']:
            o = englishobject.enlishObject(tmpcontent['Esentence'], tmpcontent['Csentence'], tmpcontent['words'])
            objectList.append(o)
    return objectList
    for tmp_content in temp['content']:
        obj = englishobject.EnglishObject(tmp_content['Esentence'], tmp_content['Csentence'], tmp_content['words'])
        object_list.append(obj)
return object_list

async def amain(txt,type) -> None:
    count = count_files_in_folder('./voice')
    if type == '1':
        path = rf'./voice/words{count}.mp3'
    elif type == '2':
        path = rf'./voice/Esentence{count}.mp3'
    elif type == '3':
        path = rf'./voice/Csentence{count}.mp3'
    elif type == '4':
        path = rf'./voice/Ssentence{count}.mp3'
    """Main function"""
    communicate = edge_tts.Communicate(txt, language_speaker['en'])
    await communicate.save(path)
async def generate_voice(text, output_file, language='en'):
    """Generate voice from text and save to output file."""
    communicate = edge_tts.Communicate(text, language_speaker[language])
    await communicate.save(output_file)

def play_voice(english_list):
    for english_obj in english_list:
        # 先生成语音
        count = count_files_in_folder('./voice')
        path = rf'./voice/test{count}.mp3'
        await generate_voice(english_obj.Esentence, path, 'en')
        await generate_voice(english_obj.Csentence, path, 'zh')
        for word in english_obj.words:
            await generate_voice(word['word'], path, 'en')
            await generate_voice(word['meaning'], path, 'zh')

#生成语音
def initVoice(engList):
    for eng in engList:
        #先生成语音
        amain(eng.Esentence, '2')
        amain(eng.Csentence, '3')
        for i in range(len(eng.words)):
            amain(eng.words[i], '1')
def dictation(english_list):
    for english_obj in english_list:
        for word in english_obj.words:
            # 播放单词和句子的语音
            count = count_files_in_folder('./voice')
            word_path = rf'./voice/word{count}.mp3'
            sentence_path = rf'./voice/sentence{count}.mp3'
            await generate_voice(word['word'], word_path, 'en')
            await generate_voice(english_obj.Esentence, sentence_path, 'en')
            await generate_voice(english_obj.Csentence, sentence_path, 'zh')
            await generate_voice(word['meaning'], word_path, 'zh')


            # 等待用户输入
            user_input = input(f"请输入单词 '{word['word']}' 的中文释义：")
            if user_input == word['meaning']:
                print("正确！")
            else:
                print(f"错误！正确答案是：{word['meaning']}")

            # 用户控制选项
            while True:
                control = input("请输入1 重复当前听写单词和中文释义，2重复播放当前听写英语句子，3重复播放当前中文句子，4播放带有当前单词的相似例句，回车键则听写下一个单词,0结束本次听写测验并产出听写报告：")
                if control == '1':
                    await generate_voice(word['word'], word_path, 'en')
                    await generate_voice(word['meaning'], word_path, 'zh')
                elif control == '2':
                    await generate_voice(english_obj.Esentence, sentence_path, 'en')
                elif control == '3':
                    await generate_voice(english_obj.Csentence, sentence_path, 'zh')
                elif control == '4':
                    # 假设相似例句在words中
                    similar_sentence = word.get('similar_sentence', '')
                    if similar_sentence:
                        await generate_voice(similar_sentence, sentence_path, 'en')
                elif control == '0':
                    return
                elif control == '':
                    break



def controlKey():
    swich = input("请输入1播放单词，2播放英语句子，3播放中文句子，4播放带有单词的句子，5下一个单词,0结束本次听写测验并产出听写报告")
    if swich == '1':
        amain(ob[0].Esentence, 'test.mp3')

def count_files_in_folder(folder_path):
    """Count the number of files in a given folder."""
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return len(files)
    except Exception as e:
        print(f"Error counting files in folder {folder_path}: {e}")
        return 0

if __name__ == "__main__":
    ob = load_object_from_json('day01.json')
    print(ob)

    english_objects = load_objects_from_json('day01.json')
    dictation(english_objects)
