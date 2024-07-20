import os
import shutil


def move_images(src_dir, dst_dir):
    """
    将src_dir文件夹下所有子文件夹中的图像文件移动到dst_dir文件夹
    :param src_dir: 源文件夹路径
    :param dst_dir: 目标文件夹路径
    """
    # 支持中文路径
    src_dir = os.path.abspath(src_dir)
    dst_dir = os.path.abspath(dst_dir)

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # 支持的图像文件扩展名
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                src_file_path = os.path.join(root, file)
                dst_file_path = os.path.join(dst_dir, file)

                # 避免文件名冲突
                counter = 1
                base_name, extension = os.path.splitext(file)
                while os.path.exists(dst_file_path):
                    dst_file_path = os.path.join(dst_dir, f"{base_name}_{counter}{extension}")
                    counter += 1

                shutil.move(src_file_path, dst_file_path)
                print(f"Moved: {src_file_path} -> {dst_file_path}")


if __name__ == "__main__":
    src_directory = "/Volumes/KIOXIARC20/pcb/SMT元器件样本"  # 替换为源文件夹的路径
    dst_directory = "images"  # 替换为目标文件夹的路径

    move_images(src_directory, dst_directory)
