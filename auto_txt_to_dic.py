import os


def find_all_txt_files(folder_path):
    """查找文件夹及其子文件夹中所有的TXT文件"""
    txt_files = []
    if not os.path.isdir(folder_path):
        print(f"错误：'{folder_path}' 不是有效的文件夹路径")
        return txt_files

    # 递归遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.txt'):
                txt_path = os.path.join(root, file)
                txt_files.append(txt_path)

    return txt_files


def merge_to_dic(txt_files, output_dic_path, encoding='utf-8'):
    """将所有TXT文件内容合并到.dic文件"""
    if not txt_files:
        print("没有找到任何TXT文件，无法合并")
        return False

    total_lines = 0
    try:
        with open(output_dic_path, 'w', encoding=encoding) as dic_file:
            # 遍历所有TXT文件
            for i, txt_path in enumerate(txt_files, 1):
                file_name = os.path.basename(txt_path)
                print(f"正在处理 [{i}/{len(txt_files)}]：{file_name}")

                # 读取TXT文件内容并写入DIC文件
                with open(txt_path, 'r', encoding=encoding) as txt_file:
                    lines = txt_file.readlines()
                    dic_file.writelines(lines)
                    total_lines += len(lines)

        print(f"\n合并完成！")
        print(f"输出文件：{output_dic_path}")
        print(f"总合并行数：{total_lines}")
        return True

    except Exception as e:
        print(f"合并过程出错：{str(e)}")
        # 清理不完整的输出文件
        if os.path.exists(output_dic_path):
            os.remove(output_dic_path)
        return False


def main():
    print("=== TXT文件自动合并为DIC工具 ===")
    print("功能：扫描指定文件夹中的所有TXT文件（包括子文件夹），合并为一个.dic文件\n")

    # 获取用户输入的文件夹路径
    folder_path = input("请输入要扫描的文件夹路径：").strip()
    if not folder_path:
        print("错误：文件夹路径不能为空")
        return

    # 查找所有TXT文件
    txt_files = find_all_txt_files(folder_path)
    if not txt_files:
        return

    print(f"共找到 {len(txt_files)} 个TXT文件\n")

    # 获取输出DIC文件名
    default_dic_name = "merged_dictionary.dic"
    dic_name = input(f"请输入输出的.dic文件名（默认：{default_dic_name}）：").strip() or default_dic_name
    if not dic_name.endswith('.dic'):
        dic_name += '.dic'
    output_path = os.path.join(os.path.dirname(folder_path), dic_name)  # 输出到文件夹同级目录

    # 执行合并
    merge_to_dic(txt_files, output_path)


if __name__ == "__main__":
    main()
