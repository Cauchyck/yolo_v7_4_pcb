import datetime

import cv2
import random
import string
import os

import numpy as np

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement


class Xml_make(object):
    def __init__(self):
        super().__init__()

    def __indent(self, elem, level=0):
        i = "\n" + level * "\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.__indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def _imageinfo(self, list_top):
        annotation_root = ET.Element('annotation')
        annotation_root.set('verified', 'no')
        tree = ET.ElementTree(annotation_root)
        '''
        0:xml_savepath 1:folder,2:filename,3:path
        4:checked,5:width,6:height,7:depth
        '''
        folder_element = ET.Element('folder')
        folder_element.text = list_top[1]
        annotation_root.append(folder_element)

        filename_element = ET.Element('filename')
        filename_element.text = list_top[2]
        annotation_root.append(filename_element)

        path_element = ET.Element('path')
        path_element.text = list_top[3]
        annotation_root.append(path_element)

        checked_element = ET.Element('checked')
        checked_element.text = list_top[4]
        annotation_root.append(checked_element)

        source_element = ET.Element('source')
        database_element = SubElement(source_element, 'database')
        database_element.text = 'Unknown'
        annotation_root.append(source_element)

        size_element = ET.Element('size')
        width_element = SubElement(size_element, 'width')
        width_element.text = str(list_top[5])
        height_element = SubElement(size_element, 'height')
        height_element.text = str(list_top[6])
        depth_element = SubElement(size_element, 'depth')
        depth_element.text = str(list_top[7])
        annotation_root.append(size_element)

        segmented_person_element = ET.Element('segmented')
        segmented_person_element.text = '0'
        annotation_root.append(segmented_person_element)

        return tree, annotation_root

    def _bndbox(self, annotation_root, list_bndbox):
        for i in range(0, len(list_bndbox), 9):
            object_element = ET.Element('object')
            name_element = SubElement(object_element, 'name')
            name_element.text = list_bndbox[i]

            flag_element = SubElement(object_element, 'flag')
            flag_element.text = list_bndbox[i + 1]

            pose_element = SubElement(object_element, 'pose')
            pose_element.text = list_bndbox[i + 2]

            truncated_element = SubElement(object_element, 'truncated')
            truncated_element.text = list_bndbox[i + 3]

            difficult_element = SubElement(object_element, 'difficult')
            difficult_element.text = list_bndbox[i + 4]

            bndbox_element = SubElement(object_element, 'bndbox')
            xmin_element = SubElement(bndbox_element, 'xmin')
            xmin_element.text = str(list_bndbox[i + 5])

            ymin_element = SubElement(bndbox_element, 'ymin')
            ymin_element.text = str(list_bndbox[i + 6])

            xmax_element = SubElement(bndbox_element, 'xmax')
            xmax_element.text = str(list_bndbox[i + 7])

            ymax_element = SubElement(bndbox_element, 'ymax')
            ymax_element.text = str(list_bndbox[i + 8])

            annotation_root.append(object_element)

        return annotation_root

    def txt_to_xml(self, list_top, list_bndbox):
        tree, annotation_root = self._imageinfo(list_top)
        annotation_root = self._bndbox(annotation_root, list_bndbox)
        self.__indent(annotation_root)
        tree.write(list_top[0], encoding='utf-8', xml_declaration=True)


def generate_xml(filename, random_locations):
    #######  创建XML文件  ########
    list_top = []
    list_bndbox = []

    output_folder = "gen_data/generate_xml"  # 存放生成图像的文件夹
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    filename = filename.replace('.jpg', '.xml')
    # 保存处理后的图像
    xml_save_path = f"{output_folder}/{filename}"
    # filename = os.path.splitext(file_name)[0]
    checked = 'NO'
    depth = '1'
    flag = 'rectangle'
    pose = 'Unspecified'
    truncated = '0'
    difficult = '0'
    list_top.extend([xml_save_path, 'folder_path_tuple', filename, xml_save_path, checked,
                     1226, 1220, depth])


    # 绘制矩形框 #
    # cv2.rectangle(img=canvas, pt1=(xmin, ymax), pt2=(xmax, ymin), color=COLOR_MAP["green"], thickness=5)
    # cv2.imwrite("draw_rectangle.png", canvas)
    # cv2.waitKey()

    # 添加针脚位置
    for loc in random_locations:
        xmin, ymin, xmax, ymax= loc

        list_bndbox.extend(['pin', flag, pose, truncated, difficult,
                            str(xmin), str(ymin), str(xmax), str(ymax)])

    Xml_make().txt_to_xml(list_top, list_bndbox)
    print(xml_save_path)


def generate_random_location(number, x1, y1, w, h):
    '''
    随机生成n个针脚位置，生成坐标要求针脚放置区域，且放置针脚图像后不会重叠，针脚size约为70*140
    如果位置在下侧，down为1，否则为0

    :param number: int, 放置针脚个数
    :param x1: int, 图像上侧区域原点x
    :param y1: int, 图像上侧区域原点y
    :param x2: int, 图像下侧区域原点x
    :param y2: int, 图像下侧区域原点y
    :param w:  int, 区域宽度
    :param h:  int, 区域高度
    :return: list of tuple, locations[(xmin, ymin, xmax, ymax, down),]
    '''

    pin_width = 40
    pin_height = 120
    locations = []
    max_attempts = 1000  # 最大尝试次数，以避免无限循环

    def is_overlap(new_loc):
        ''' 检查新位置是否与已存在的位置重叠 '''
        for loc in locations:
            if (new_loc[0] < loc[2] and new_loc[2] > loc[0] and
                    new_loc[1] < loc[3] and new_loc[3] > loc[1]):
                return True
        return False

    attempts = 0
    while len(locations) < number and attempts < max_attempts:
        xmin = random.randint(x1, x1 + w - pin_width)
        ymin = y1
        xmax = xmin + pin_width
        ymax = ymin + pin_height

        new_location = (xmin, ymin, xmax, ymax)

        if not is_overlap(new_location):
            locations.append(new_location)

        attempts += 1

    if len(locations) < number:
        print(f"Warning: Only {len(locations)} out of {number} pin locations were successfully placed without overlap.")

    return locations


def generate_image(image, random_locations):
    '''
    从针脚图像的文件夹中随机读取针脚图像，将图像按照locations中的坐标融合于模版图像image，数量取决于locations长度，
    如果down为0，需要将针脚图像旋转180度

    :param image: numpy array, 模版图像
    :param random_locations: list of tuple, locations[(xmin, ymin, xmax, ymax, down),]
    :param pin_folder: str, 针脚图像文件夹路径
    :return: numpy array, 融合后的图像
    '''
    pin_folder = "template_images/4pins"
    pin_images = [f for f in os.listdir(pin_folder) if os.path.isfile(os.path.join(pin_folder, f))]


    for i in range(4):
        for loc in random_locations:
            xmin, ymin, xmax, ymax = loc
            pin_image_path = os.path.join(pin_folder, random.choice(pin_images))
            pin_image = cv2.imread(pin_image_path)

            if pin_image is None:
                print(f"Error reading {pin_image_path}")
                continue

            # 调整针脚图像大小为 (xmax - xmin) x (ymax - ymin)
            pin_image = cv2.resize(pin_image, (xmax - xmin, ymax - ymin))
            # 将针脚图像粘贴到模板图像的相应位置
            image[ymin:ymax, xmin:xmax] = pin_image
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    output_folder = "gen_data/generate_data"  # 存放生成图像的文件夹
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    # 使用时间戳命名图像文件
    now = datetime.datetime.now()
    # 获取时间戳（精确到秒）
    timestamp_seconds = now.strftime("%H%M%S")

    # 获取当前时间的毫秒数
    milliseconds = now.microsecond // 1000

    # 生成包含毫秒级时间戳的字符串
    timestamp = f"{timestamp_seconds}{milliseconds:03d}"

    image_filename = f"{timestamp}.jpg"
    # 保存处理后的图像
    output_path = f"{output_folder}/{image_filename}"
    cv2.imwrite(output_path, image)

    generate_xml(image_filename, random_locations)


def generate_and_save_images(num_images):
    # 读取背景图像
    background_path = "template_images/557.jpg"  # 替换为实际图像路径
    background = cv2.imread(background_path)

    # print(random_text)cv2.rotate(image, cv2.ROTATE_90)
    for i in range(num_images):
        num = random.randint(5, 20)
        random_location = generate_random_location(num, 200, 30, 800, 100)
        generate_image(background.copy(), random_location)


def main():
    num_images = 1  # 要生成的图像数量

    # 生成并保存图像
    generate_and_save_images(num_images)


if __name__ == "__main__":
    main()
