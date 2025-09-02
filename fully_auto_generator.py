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
