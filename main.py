import os
import shutil

import os, pytz
from datetime import datetime
import argparse
from chatgpt_automation.chatgpt_automation import ChatGPTAutomation



question = """Hãy trích xuất thông tin:  
- Họ tên
- Ngày sinh
- Giới tính  
- Số điện thoại
- Email
- Địa chỉ
không lấy thêm thông tin nào khác
"""
import pandas as pd

def save_to_excel(conversations, file_name):
    # Chuyển đổi danh sách đối tượng JSON thành DataFrame
    df = pd.DataFrame(conversations)

    # Lưu DataFrame vào file Excel
    df.to_excel(file_name, index=False, engine='openpyxl')
    print(f"Dữ liệu đã được lưu vào file: {file_name}")



def main():
    parser = argparse.ArgumentParser()

    # Arguments users used when running command lines
    parser.add_argument('--folder-input', type=str, default="E:\\Data\\TopCV", help='Where input data is located')
    parser.add_argument('--folder-output', default='E:\\Data', type=str,  help='Where output data is located')
    parser.add_argument('--chrome-path', default='E:\\Software\\chrome-win64\\chrome.exe', type=str, help='Where chrome application is located')
    parser.add_argument('--chrome-driver', default='E:\\Software\\chromedriver-win64\\chromedriver.exe', type=str, help='Where chrome driver is located ')
    args = parser.parse_args()
    print(args)
    # Đường dẫn đến thư mục chứa file PDF
    folder_path = args.folder_input
    backup_path = os.path.join(folder_path, "backup")
    error_path = os.path.join(folder_path, "error")

    os.makedirs(backup_path, exist_ok=True)
    os.makedirs(error_path, exist_ok=True)

    combined_list = []
    chat_bot = ChatGPTAutomation(
        chrome_path=args.chrome_path,
        chrome_driver_path=args.chrome_driver,
    )


    current_time = datetime.now()

    # Convert to Vietnam time zone
    vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time_vietnam = current_time.astimezone(vietnam_timezone)

    # Format the datetime object to exclude milliseconds
    current_time = str(current_time_vietnam.strftime('%Y-%m-%d %H:%M:%S'))

    current_time = current_time.replace(" ", "_")
    current_time = current_time.replace("-", "_")
    current_time = current_time.replace(":", "_")
    current_time = current_time.replace("+", "_")


    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            # Tạo đường dẫn đầy đủ đến file
            full_path = os.path.join(folder_path, filename)
            print(f"Đang xử lý file: {full_path}")

            try:
                chat_bot.upload_file_for_prompt(full_path)
                chat_bot.send_prompt_to_chatgpt(question)
                json_data = chat_bot.get_conversation()
                print(json_data)
                if json_data:
                    combined_list.append(json_data)
                    save_to_excel(combined_list, args.folder_input + "\\output_" + current_time + ".xlsx")
                shutil.move(full_path, os.path.join(backup_path, filename))
                print(f"File đã được di chuyển đến thư mục backup: {filename}")

                chat_bot.open_new_chat()

            except Exception as e:
                print(f"Có lỗi xảy ra với file {filename}: {e}. File đã được di chuyển đến thư mục error.")
                shutil.move(full_path, os.path.join(error_path, filename))
                chat_bot.open_new_chat()


            # In ra danh sách kết quả
    print(combined_list)

    # Đóng chat bot
    chat_bot.quit()

if __name__ == "__main__":
    main()

