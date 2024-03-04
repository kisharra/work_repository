import json
import subprocess
import os


# Укажите свой путь с хранилищем файлов и путь для json файла
os.system("/bin/mediainfo /file_storage/film_storage/* --output=JSON --LogFile=/file_storage/work_repository/media_info.json")


def read(file_name):
    """Читает файл"""
    with open(file_name, "r") as file:
        data = json.load(file)
    return data


def extract_info(media_info):
    """Извлекает нужную информацию"""

    info = {}
    if "media" in media_info:
        href = media_info["media"]["@ref"]
        track = media_info["media"]["track"]
        if track[0]["FileSize"] != "0":
            file_size = track[0]["FileSize"]
            format_ = track[0]["FileExtension"]
            width = track[1]["Width"]
            height = track[1]["Height"]
        else:
            undefined = "не определено"
            file_size = undefined
            format_ = undefined
            width = undefined
            height = undefined

        info = {
            "@ref": href,
            "FileSize": file_size,
            "FileExtension": format_,
            "Width": width,
            "Height": height
        }

    return info


def convert_video(input_file, output_file):
    """Конвертирует видеофайл в формат MP4, оставляя только первую аудиодорожку и сохраняя разрешение"""
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "libx264",  # Используем кодек H.264 для видео
        "-crf", "25",  # Качество видео (меньше значение, лучше качество, больше размер)
        "-preset", "ultrafast",  # Устанавливаем скорость конвертирования 
        "-c:a:0", "aac",  # Кодируем первую аудиодорожку в AAC
        "-strict", "experimental",
        "-map", "0:v:0",  # Выбираем первую видеодорожку
        "-map", "0:a:0",  # Выбираем первую аудиодорожку
        "-movflags", "+faststart",  # Для потокового воспроизведения
        output_file
    ]
    subprocess.run(command)
    os.remove(input_file)


def main(file_name):
    """main function"""

    media_info_list = read(file_name)
    
    info_list = []
    for media_info in media_info_list:
        info = extract_info(media_info)
        if int(info["FileSize"]) >= 10737418240:
            info_list.append(info)

    with open('media_info.json', 'w', encoding='utf-8') as file:
        json.dump(info_list, file, ensure_ascii=False, indent=4)
    
    for info in info_list:
        input_file = info["@ref"]
        output_file = os.path.splitext(input_file)[0] + ".mp4"
        info["CurrentFileStatus"] = "Конвертация"  # Добавляем информацию о текущем статусе файла
        
        with open('media_info.json', 'w', encoding='utf-8') as file:
            json.dump(info_list, file, ensure_ascii=False, indent=4)

        convert_video(input_file, output_file)

        info["CurrentFileStatus"] = f"Файл конвертирован"  # Обновляем информацию о статусе файла
        info["NewFilePath"] = output_file  # Добавляем новый путь к конвертированному файлу
        with open('media_info.json', 'w', encoding='utf-8') as file:
            json.dump(info_list, file, ensure_ascii=False, indent=4)

    with open('media_info.json', 'w', encoding='utf-8') as file:
        json.dump(info_list, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main("media_info.json")
