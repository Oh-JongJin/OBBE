import os
import sys
import numpy as np

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDesktopWidget, \
                            QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QImage, QBrush
from PyQt5.QtCore import Qt, QPoint, QRect, QSettings


class ClassEditDialog(QDialog):
    def __init__(self, current_class, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Class Number')
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Add instruction label
        self.label = QLabel(f'Current class: {current_class}\nEnter new class number:')
        layout.addWidget(self.label)
        
        # Add line edit for class number
        self.class_input = QLineEdit()
        if current_class != "0":
            self.class_input.setText(current_class)
        layout.addWidget(self.class_input)
        
        # Add OK button
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        
        self.setLayout(layout)
        
        
class DeleteConfirmDialog(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle('Delete Confirmation')
        self.setText('Are you sure you want to delete this polygon?')
        self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.setDefaultButton(QMessageBox.No)
        
        # Make Yes button red
        yes_button = self.button(QMessageBox.Yes)
        yes_button.setStyleSheet("QPushButton {color: red}")


class PolygonViewer(QMainWindow):
    def __init__(self, label_dir, image_dir):
        super().__init__()
        self.label_files = sorted([f for f in os.listdir(label_dir) if f.endswith('.txt')])
        self.image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
        
        self.current_datetime = None
        self.settings = QSettings("my", "index")
        if self.settings.value("index") is not None:
            self.current_index = self.settings.value("index")
        else:
            self.current_index = 0
        self.label_dir = label_dir
        self.image_dir = image_dir
        
        self.edit_mode = False
        self.dragging_point = None
        self.point_radius = 5
        
        self.magnifier_size = 200
        self.zoom_factor = 3
        self.mouse_pos = QPoint()
        
        self.load_current_file()
        print(f"{self.current_index + 1}/{len(self.image_files)} - {self.current_datetime}")
        # self.settings.setValue("index", self.current_index)
        self.initUI()

    def load_current_file(self):
        image_path = os.path.join(self.image_dir, self.image_files[self.current_index])
        # label_path = os.path.join(self.label_dir, self.label_files[self.current_index])
        self.current_label_path = os.path.join(self.label_dir, self.label_files[self.current_index])
        
        self.current_datetime = self.label_files[self.current_index].replace(".txt", "")
        
        self.background_image = QImage(image_path)
        if self.background_image.isNull():
            raise Exception(f"Failed to load image: {image_path}")
            
        self.polygons = self.parse_polygon_file(self.current_label_path)
        self.selected_polygon = None
        self.edit_mode = False
        self.dragging_point = None
        
        self.setWindowTitle(f'Polygon Viewer - {self.image_files[self.current_index]} ({self.current_index + 1}/{len(self.image_files)})')
        
    def get_screen_points(self, polygon_index):
        """Convert normalized coordinates to screen coordinates"""
        x_offset = (self.screen_width - self.drawing_width) // 2
        y_offset = (self.screen_height - self.drawing_height) // 2
        
        points = []
        polygon = self.polygons[polygon_index]
        for j in range(0, 8, 2):
            x_coord = x_offset + int(polygon[j] * self.drawing_width)
            y_coord = y_offset + int(polygon[j+1] * self.drawing_height)
            points.append(QPoint(x_coord, y_coord))
        return points
    
    def get_normalized_coordinates(self, screen_x, screen_y):
        """Convert screen coordinates to normalized coordinates"""
        x_offset = (self.screen_width - self.drawing_width) // 2
        y_offset = (self.screen_height - self.drawing_height) // 2
        
        norm_x = (screen_x - x_offset) / self.drawing_width
        norm_y = (screen_y - y_offset) / self.drawing_height
        return norm_x, norm_y
        
    def initUI(self):
        """Get the current screen geometry"""
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        
        self.scaled_image = self.background_image.scaled(
            self.screen_width, 
            self.screen_height,
            Qt.KeepAspectRatio
        )
        
        self.drawing_width = self.scaled_image.width()
        self.drawing_height = self.scaled_image.height()
        
        self.setGeometry(1920, 0, self.screen_width, self.screen_height)
        self.setWindowTitle('Polygon Viewer')
        self.showFullScreen()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        x = (self.screen_width - self.drawing_width) // 2
        y = (self.screen_height - self.drawing_height) // 2
        
        painter.drawImage(x, y, self.scaled_image)
        
        for i, polygon in enumerate(self.polygons):
            if i == self.selected_polygon:
                painter.setPen(QPen(Qt.red, 2))
            elif self.classes[i] == "9":
                painter.setPen(QPen(Qt.blue, 1))
            elif self.classes[i] == "0":
                painter.setPen(QPen(Qt.yellow, 4))
            else:
                painter.setPen(QPen(Qt.green, 1))
            
            points = []
            for j in range(0, 8, 2):
                # x = int(polygon[j] * self.screen_width)
                # y = int(polygon[j+1] * self.screen_height)
                # points.append(QPoint(x, y))
                x_coord = x + int(polygon[j] * self.drawing_width)
                y_coord = y + int(polygon[j+1] * self.drawing_height)
                points.append(QPoint(x_coord, y_coord))
            
            for j in range(4):
                painter.drawLine(points[j], points[(j+1)%4])
                
            if self.edit_mode and i == self.selected_polygon:
                painter.setPen(QPen(Qt.red, 2))
                painter.setBrush(QBrush(Qt.white))
                for point in points:
                    painter.drawEllipse(point, self.point_radius, self.point_radius)
        
        # if self.edit_mode and self.dragging_point is not None:
        #     self.draw_magnifier(painter, x, y)
            
    def draw_magnifier(self, painter, img_x, img_y):
        # 마우스 포인터 우측 상단에 돋보기 위치 계산
        mag_x = self.mouse_pos.x() + 20
        mag_y = self.mouse_pos.y() - self.magnifier_size - 20
        
        # 화면 경계 처리
        if mag_x + self.magnifier_size > self.screen_width:
            mag_x = self.mouse_pos.x() - self.magnifier_size - 20
        if mag_y < 0:
            mag_y = self.mouse_pos.y() + 20
            
        # 돋보기 테두리 그리기
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(Qt.white))
        painter.drawRect(mag_x, mag_y, self.magnifier_size, self.magnifier_size)
        
        # 마우스 위치의 이미지 영역 계산
        source_x = self.mouse_pos.x() - img_x - self.magnifier_size/(2*self.zoom_factor)
        source_y = self.mouse_pos.y() - img_y - self.magnifier_size/(2*self.zoom_factor)
        source_size = self.magnifier_size/self.zoom_factor
        
        # 확대된 이미지 부분 그리기
        target_rect = QRect(mag_x, mag_y, self.magnifier_size, self.magnifier_size)
        source_rect = QRect(
            int(source_x), 
            int(source_y), 
            int(source_size), 
            int(source_size)
        )
        
        # 클리핑 영역 설정
        painter.setClipRect(target_rect)
        
        # 이미지 확대 그리기
        magnified_image = self.background_image.copy(
            int(source_x * self.background_image.width() / self.drawing_width),
            int(source_y * self.background_image.height() / self.drawing_height),
            int(source_size * self.background_image.width() / self.drawing_width),
            int(source_size * self.background_image.height() / self.drawing_height)
        )
        
        if not magnified_image.isNull():
            painter.drawImage(target_rect, magnified_image)
            
            # 선택된 폴리곤의 점들도 확대하여 그리기
            if self.selected_polygon is not None:
                points = self.get_screen_points(self.selected_polygon)
                painter.setPen(QPen(Qt.red, 2))
                painter.setBrush(QBrush(Qt.white))
                
                for i, point in enumerate(points):
                    # 점의 상대 위치 계산
                    rel_x = point.x() - (self.mouse_pos.x() - self.magnifier_size/(2*self.zoom_factor))
                    rel_y = point.y() - (self.mouse_pos.y() - self.magnifier_size/(2*self.zoom_factor))
                    
                    # 확대된 위치 계산
                    mag_point_x = mag_x + rel_x * self.zoom_factor
                    mag_point_y = mag_y + rel_y * self.zoom_factor
                    
                    for j in range(4):
                        painter.drawLine(points[j], points[(j+1)%4])
                    
                    # 확대된 점 그리기
                    if target_rect.contains(int(mag_point_x), int(mag_point_y)):
                        painter.drawEllipse(QPoint(int(mag_point_x), int(mag_point_y)), 
                                         self.point_radius * 1, self.point_radius * 1)
        
        painter.setClipping(False)
        
        # 십자선 그리기
        painter.setPen(QPen(Qt.red, 1))
        center_x = int(mag_x + self.magnifier_size/2)
        center_y = int(mag_y + self.magnifier_size/2)
        line_length = 10
        
        painter.drawLine(center_x - line_length, center_y, center_x + line_length, center_y)
        painter.drawLine(center_x, center_y - line_length, center_x, center_y + line_length)
                
    def mousePressEvent(self, event):
        x_offset = (self.screen_width - self.drawing_width) // 2
        y_offset = (self.screen_height - self.drawing_height) // 2
        
        x = (event.x() - x_offset) / self.drawing_width
        y = (event.y() - y_offset) / self.drawing_height
        
        if self.edit_mode and self.selected_polygon is not None:
            points = self.get_screen_points(self.selected_polygon)
            for i, point in enumerate(points):
                if (point.x() - event.x()) ** 2 + (point.y() - event.y()) ** 2 <= self.point_radius ** 2:
                    self.dragging_point = i
                    return
                
        for i, polygon in enumerate(self.polygons):
            coords = np.array([(polygon[j], polygon[j+1]) for j in range(0, 8, 2)])
            if self.point_in_polygon(x, y, coords):
                self.selected_polygon = i
                print(f"\nClicked Polygon {i}:")
                print(f"Coordinates: {self.classes[i]} {polygon[0]:.6f} {polygon[1]:.6f} {polygon[2]:.6f} {polygon[3]:.6f} {polygon[4]:.6f} {polygon[5]:.6f} {polygon[6]:.6f} {polygon[7]:.6f}")
                self.update()
                break
            
    def mouseDoubleClickEvent(self, event):
        x_offset = (self.screen_width - self.drawing_width) // 2
        y_offset = (self.screen_height - self.drawing_height) // 2
        
        x = (event.x() - x_offset) / self.drawing_width
        y = (event.y() - y_offset) / self.drawing_height
        
        for i, polygon in enumerate(self.polygons):
            coords = np.array([(polygon[j], polygon[j+1]) for j in range(0, 8, 2)])
            if self.point_in_polygon(x, y, coords):
                print("Double Clicked!!")
                self.edit_class(i)
                break
    
    def mouseReleaseEvent(self, event):
        if self.dragging_point is not None:
            self.dragging_point = None
            self.save_changes()
            
    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        if self.edit_mode and self.dragging_point is not None:
            norm_x, norm_y = self.get_normalized_coordinates(event.x(), event.y())
            norm_x = max(0, min(1, norm_x))
            norm_y = max(0, min(1, norm_y))
            
            self.polygons[self.selected_polygon][self.dragging_point * 2] = norm_x
            self.polygons[self.selected_polygon][self.dragging_point * 2 + 1] = norm_y
            self.update()
            
    def edit_class(self, polygon_index):
        dialog = ClassEditDialog(self.classes[polygon_index], self)
        if dialog.exec_() == QDialog.Accepted:
            new_class = dialog.class_input.text()
            if new_class.isdigit():  # Ensure input is a valid number
                self.classes[polygon_index] = new_class
                self.save_changes()
                print(f"Changed polygon {polygon_index} class to {new_class}")
    
    def save_changes(self):
        """Save the updated classes to the label file"""
        lines = []
        for cls, polygon in zip(self.classes, self.polygons):
            coords = ' '.join([f'{x:.6f}' for x in polygon])
            lines.append(f'{cls} {coords}')
        
        with open(self.current_label_path, 'w') as f:
            f.write('\n'.join(lines))
        print("Saved polygon.")
        
    def delete_selected_polygon(self):
        if self.selected_polygon is not None:
            dialog = DeleteConfirmDialog(self)
            if dialog.exec_() == QMessageBox.Yes:
                print(f"Deleting polygon {self.selected_polygon}")
                del self.polygons[self.selected_polygon]
                del self.classes[self.selected_polygon]
                self.save_changes()
                self.selected_polygon = None
                self.edit_mode = False
                self.update()
    
    def point_in_polygon(self, x, y, polygon):
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def keyPressEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            if e.key() == Qt.Key_W:
                self.close()
        elif e.key() == Qt.Key_Q:
            self.close()
        elif e.key() == Qt.Key_Delete:
            if self.selected_polygon is not None:
                self.delete_selected_polygon()
        elif e.key() == Qt.Key_E:
            if self.selected_polygon is not None:
                self.edit_mode = not self.edit_mode
                print(f"Edit mode: {'ON' if self.edit_mode else 'OFF'}")
                self.update()
        elif e.key() == Qt.Key_A:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            print(f"{self.current_index + 1}/{len(self.image_files)} - {self.current_datetime}")
            self.settings.setValue("index", self.current_index)
            self.load_current_file()
            self.initUI()
            self.update()
        elif e.key() == Qt.Key_D:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            print(f"{self.current_index + 1}/{len(self.image_files)} - {self.current_datetime}")
            self.settings.setValue("index", self.current_index)
            self.load_current_file()
            self.initUI()
            self.update()

    def parse_polygon_file(self, filename):
        polygons = []
        self.classes = []
        with open(filename, 'r') as file:
            for line in file:
                values = line.split()
                if len(values) == 9:  # class + 8 coordinates
                    polygons.append([float(x) for x in values[1:]])  # Skip the class
                    self.classes.append(values[0])
        return polygons


if __name__ == '__main__':
    try:
        # fname = "church_20240930-134625"
        # image_file = f"C:/Users/VEStellaLab/Workspace/Drone/kto_hackerthon/original/" \
        #              f"{fname.split('_')[-1][4:8]}/{fname.split('_')[0]}/{fname.split('_')[-1]}.jpg"
        # label_file = parse_polygon_file(f'labels/{fname}.txt')
        
        label_dir = "kto_dataset/labels"
        image_dir = "kto_dataset/images"
        
        app = QApplication(sys.argv)
        viewer = PolygonViewer(label_dir, image_dir)
        viewer.show()
        sys.exit(app.exec_())
        
    except FileNotFoundError:
        print("Error: Could not find the polygon data file.")
    except Exception as e:
        print(f"Error: {str(e)}")
