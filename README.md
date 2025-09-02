# Lab---RE-Bingo-
当然可以使用正确的方法，但是我想要要找到正确的密码
《X86-SOFTWARE-REVERSE-ENGINEERING-CRACKING-AND-COUNTER-MEASURES》这本书有个实验，
Lab - RE Bingo
这个实验我没有在网上找到答案，自己试着做了，感觉有好多种可能，比如i_exo_f_wxo_wx_fo_i，这个比较接近。
通过暴力破解这个第一部分，终于找到了答案，鉴于作者的意图是通过这个实验掌握知识，我就不给出答案了。
暴力破解软件是Advanced Archive Password Recovery，思路是：通过代码生成密码字典集，然后让这个软件爆破。
第一个文件：

```python
import itertools
import os
import math

# 配置常量
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB (字节)
APPROX_PASSWORD_SIZE = 20  # 每个密码的近似字节数（含换行符）
NUM_PARTS = 8  # 密码包含的部分数量
FIRST_CHARS = ['i', 'e', 'w', 's', 'f']  # 首字符可选范围
SUFFIXES = ['', 'x', 'o', 'xo']  # 首字符后可跟的后缀


def generate_all_possible_parts():
    """自动生成所有部分的可能组合（首字符+后缀）"""
    all_possible_parts = []
    # 为每个部分生成所有可能的组合（首字符从FIRST_CHARS中选，后跟SUFFIXES）
    for i in range(NUM_PARTS):
        parts = [f"{first}{suffix}" for first in FIRST_CHARS for suffix in SUFFIXES]
        all_possible_parts.append(parts)
        print(f"第{i + 1}部分可能的组合数: {len(parts)}种")

    return all_possible_parts


def calculate_total_combinations(all_possible_parts):
    """计算总组合数"""
    total = 1
    for parts in all_possible_parts:
        total *= len(parts)
    return total


def get_next_filename(base_name):
    """获取下一个可用的文件名（格式：base_name_1.txt, base_name_2.txt...）"""
    index = 1
    while True:
        if '.' in base_name:
            name_parts = base_name.rsplit('.', 1)
            filename = f"{name_parts[0]}_{index}.{name_parts[1]}"
        else:
            filename = f"{base_name}_{index}.txt"

        if not os.path.exists(filename):
            return filename
        index += 1


def batch_generator(all_possible_parts, batch_size=100000, start_index=0):
    """分批次生成密码"""
    total = calculate_total_combinations(all_possible_parts)
    all_combos = itertools.product(*all_possible_parts)

    # 跳过前面的组合
    for _ in range(start_index):
        try:
            next(all_combos)
        except StopIteration:
            break

    while True:
        batch = []
        for _ in range(batch_size):
            try:
                combo = next(all_combos)
                batch.append('_'.join(combo))
            except StopIteration:
                break

        if not batch:
            break

        yield batch


def save_progress(progress_file, index, current_file):
    """保存当前进度（已生成的数量和当前文件名）"""
    with open(progress_file, 'w', encoding='utf-8') as f:
        f.write(f"{index}\n{current_file}")


def load_progress(progress_file):
    """读取上次保存的进度"""
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                try:
                    return int(lines[0].strip()), lines[1].strip()
                except:
                    return 0, None
    return 0, None


def main():
    print("全自动密码生成器")
    print("规则：")
    print(f"- 共{NUM_PARTS}个部分，用下划线拼接")
    print(f"- 每个部分的第一个字符自动从{FIRST_CHARS}中选择")
    print(f"- 第一个字符之后的部分只能是：{SUFFIXES}")
    print(f"- 每个文件大小限制为{MAX_FILE_SIZE / (1024 * 1024):.0f}MB")

    # 生成所有可能的部分组合
    all_possible_parts = generate_all_possible_parts()
    total = calculate_total_combinations(all_possible_parts)

    print(f"\n总密码组合数: {total:,}个")  # 每个部分有5×4=20种可能，总组合数为20^8=2560000000

    # 如果数量过大，提示用户
    if total > 10 ** 9:  # 超过10亿
        confirm = input(f"注意：将生成{total:,}个密码，可能需要较长时间和存储空间。是否继续？(y/n): ")
        if confirm.lower() != 'y':
            print("已取消操作")
            return

    # 获取基础文件名
    base_name = input("\n请输入文件基础名称（如mypass）: ").strip()
    if not base_name:
        base_name = "passwords"

    # 批次设置
    suggested_batch = max(100000, (MAX_FILE_SIZE // 10) // APPROX_PASSWORD_SIZE)
    batch_input = input(f"每批生成数量（建议{suggested_batch:,}）: ").strip()
    batch_size = int(batch_input) if batch_input else suggested_batch

    # 进度和文件设置
    progress_file = "generate_progress.txt"
    start_index, last_file = load_progress(progress_file)
    current_file = last_file if last_file and os.path.exists(last_file) else get_next_filename(base_name)

    if start_index > 0:
        print(f"检测到上次进度，将从第{start_index + 1}个密码开始生成，当前文件: {current_file}")

    # 检查当前文件大小
    file_mode = 'a' if start_index > 0 else 'w'
    if os.path.exists(current_file) and os.path.getsize(current_file) >= MAX_FILE_SIZE * 0.95:
        current_file = get_next_filename(base_name)
        file_mode = 'w'
        print(f"当前文件已接近大小限制，将使用新文件: {current_file}")

    # 开始生成
    try:
        processed = start_index
        current_f = open(current_file, file_mode, encoding='utf-8', buffering=1024 * 1024)

        for batch in batch_generator(all_possible_parts, batch_size, start_index):
            # 检查当前文件是否需要切换
            if current_f.tell() + len(batch) * APPROX_PASSWORD_SIZE > MAX_FILE_SIZE:
                current_f.close()
                current_file = get_next_filename(base_name)
                current_f = open(current_file, 'w', encoding='utf-8', buffering=1024 * 1024)
                print(f"\n已切换到新文件: {current_file}")

            # 写入当前批次
            current_f.write('\n'.join(batch) + '\n')
            processed += len(batch)

            # 显示进度
            progress = (processed / total) * 100 if total > 0 else 100
            file_size = current_f.tell() / (1024 * 1024)
            print(
                f"已生成: {processed:,}/{total:,} ({progress:.2f}%) | 当前文件: {current_file} ({file_size:.1f}MB/{MAX_FILE_SIZE / (1024 * 1024):.0f}MB)",
                end='\r')

            # 保存进度
            save_progress(progress_file, processed, current_file)

        current_f.close()
        print("\n\n所有密码生成完成！")

        # 清理进度文件
        if os.path.exists(progress_file):
            os.remove(progress_file)

    except KeyboardInterrupt:
        current_f.close()
        print(f"\n\n已中断，已生成{processed:,}个密码，进度已保存")
    except Exception as e:
        if 'current_f' in locals():
            current_f.close()
        print(f"\n\n错误: {str(e)}，已生成{processed:,}个密码，进度已保存")


if __name__ == "__main__":
    main()

```



第二个文件：

```python
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

```

可以通过40个（.txt）文件转成（.dic）文件，本来是不用多此一举的，但是过大的txt文件无法打开，而且不清楚进度，这里我生成了5%的密码就破解了，就是第二个dic文件，也可能是第3个。

由于这本书是逆向工程，感觉可以使用这种方法，有兴趣的可以试一下。
