import json
import englishobject
import edge_tts
import os
import asyncio
import pygame
import time

language_speaker = {
    "ja": "ja-JP-NanamiNeural",            # ok
    "fr": "fr-FR-DeniseNeural",            # ok
    "es": "ca-ES-JoanaNeural",             # ok
    "de": "de-DE-KatjaNeural",             # ok
    "zh": "zh-CN-XiaoyiNeural",            # ok
    "en": "en-US-AnaNeural",               # ok
}

# 加载文件并输出对象
def load_objects_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    object_list = []
    for temp in data:
        print(temp['content'])
        for tmp_content in temp['content']:
            obj = englishobject.enlishObject(tmp_content['Esentence'], tmp_content['Csentence'], tmp_content['words'])
            object_list.append(obj)
    return object_list

async def generate_voice(text, output_file, language='en'):
    """Generate voice from text and save to output file."""
    communicate = edge_tts.Communicate(text, language_speaker[language])
    await communicate.save(output_file)

def play_audio(file_path):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except Exception as e:
        print(f"播放失败: {e}")
    finally:
        pygame.mixer.quit()

def dictation(english_list):
    for english_obj in english_list:
        for word in english_obj.words:
            # 播放单词和句子的语音
            count = count_files_in_folder('./voice')
            eword_path = rf'./voice/eword{count}.mp3'
            cword_path = rf'./voice/cword{count}.mp3'
            esentence_path = rf'./voice/esentence{count}.mp3'
            csentence_path = rf'./voice/csentence{count}.mp3'
            asyncio.run(generate_voice(word['e'], eword_path, 'en'))
            asyncio.run(generate_voice(english_obj.Esentence, esentence_path, 'en'))
            asyncio.run(generate_voice(english_obj.Csentence, csentence_path, 'zh'))
            asyncio.run(generate_voice(word['c'], cword_path, 'zh'))
            play_audio(eword_path)
            play_audio(cword_path)
            play_audio(esentence_path)
            play_audio(csentence_path)
            # 等待用户输入
            # user_input = input(f"请输入单词当前听写单词：")
            # if user_input == word['e']:
            #     print("正确！")
            # else:
            #     print(f"错误！正确答案是：{word['e']}")
            
            # 用户控制选项
            while True:
                control = input("请输入1 重复当前听写单词和中文释义，2重复播放当前听写英语句子，3重复播放当前中文句子，4播放带有当前单词的相似例句，回车键则听写下一个单词,0结束本次听写测验并产出听写报告：\n")
                if control == '1':
                    play_audio(eword_path)
                    play_audio(cword_path)
                elif control == '2':
                    play_audio(esentence_path)
                elif control == '3':
                    play_audio(csentence_path)
                elif control == '4':
                    # 假设相似例句在words中
                    similar_sentence = word.get('similar_sentence', '')
                    if similar_sentence:
                        generate_voice(similar_sentence, esentence_path, 'en')
                elif control == '0':
                    return
                elif control == '':
                    print("跳过单词")
                    break
                elif len(control)>2:
                    if control == word['e']:
                        print("正确！")
                        break
                    else:
                        print(f"错误！正确答案是：{word['e']}")

def count_files_in_folder(folder_path):
    """Count the number of files in a given folder."""
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        return len(files)
    except Exception as e:
        print(f"Error counting files in folder {folder_path}: {e}")
        return 0

if __name__ == "__main__":
    english_objects = load_objects_from_json('day01.json')
    dictation(english_objects)