import cv2
import numpy as np

def detect_pins(image):
    # 将图像转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 应用 Canny 边缘检测
    edges = cv2.Canny(gray, 125, 200)

    # 使用形态学操作去除噪声
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # 寻找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 筛选出针脚轮廓
    pin_contours = []
    for contour in contours:
        if cv2.contourArea(contour) > 100:
            pin_contours.append(contour)

    # 绘制针脚位置并输出坐标
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_scale = 0.5
    text_thickness = 2
    for i, contour in enumerate(pin_contours):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 输出坐标
        print(f"pin {i + 1}: xmin = {x}, ymin = {y}, xmax = {x + w}, ymax = {y + h}")

        # 在矩形框上绘制编号
        text_pos = (x + w // 2, y + h // 2)
        cv2.putText(image, str(i + 1), text_pos, font, text_scale, (0, 255, 0), text_thickness)

    # 保存截图
    cv2.imwrite('template_images/pin_locations.jpg', image)

    # 返回针脚位置
    pin_locations = []
    for contour in pin_contours:
        x, y, w, h = cv2.boundingRect(contour)
        pin_locations.append((x, y))
    return pin_locations

if __name__ == '__main__':
    image = cv2.imread('template_images/1@557.jpg')
    pin_locations = detect_pins(image)
    print(pin_locations)
