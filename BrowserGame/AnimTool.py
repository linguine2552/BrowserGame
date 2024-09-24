import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QHeaderView, QTextEdit, QComboBox, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QPoint
import math

class PoseTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pose Tool")
        self.setGeometry(100, 100, 1000, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        self.load_animation_frames()

        self.points = self.animation_frames["IDLE"]

        self.constraints = [
            ("neck", "top_head"),
            ("neck", "spine_01"),
            ("spine_01", "spine_02"),
            ("spine_02", "pelvis"),
            ("neck", "l_elbow"),
            ("l_elbow", "l_hand"),
            ("neck", "r_elbow"),
            ("r_elbow", "r_hand"),
            ("pelvis", "l_knee"),
            ("l_knee", "l_ankle"),
            ("l_ankle", "l_toe"),
            ("pelvis", "r_knee"),
            ("r_knee", "r_ankle"),
            ("r_ankle", "r_toe")
        ]

        self.initial_distances = self.calculate_initial_distances()

        self.canvas = Canvas(self.points, self.update_tree_widget, self.apply_constraints)
        self.layout.addWidget(self.canvas)

        right_layout = QVBoxLayout()
        self.layout.addLayout(right_layout)

        pose_layout = QHBoxLayout()
        pose_label = QLabel("Select Pose:")
        self.pose_dropdown = QComboBox()
        self.pose_dropdown.addItems(self.animation_frames.keys())
        self.pose_dropdown.currentTextChanged.connect(self.change_pose)
        pose_layout.addWidget(pose_label)
        pose_layout.addWidget(self.pose_dropdown)
        right_layout.addLayout(pose_layout)

        self.point_list = QTreeWidget()
        self.point_list.setHeaderLabels(["Point", "X", "Y"])
        self.point_list.setColumnCount(3)
        self.point_list.header().setSectionResizeMode(QHeaderView.Stretch)
        self.point_list.itemChanged.connect(self.on_item_changed)
        right_layout.addWidget(self.point_list)

        self.json_output = QTextEdit()
        self.json_output.setReadOnly(True)
        right_layout.addWidget(self.json_output)

        self.update_points()

    def load_animation_frames(self):
        try:
            with open('backend/game_app/animation_frames.json', 'r') as file:
                self.animation_frames = json.load(file)
        except FileNotFoundError:
            print("Error: animation_frames.json not found")
            self.animation_frames = {"IDLE": {}}

    def change_pose(self, pose_name):
        self.points = self.animation_frames[pose_name]
        self.initial_distances = self.calculate_initial_distances()
        self.canvas.update_points(self.points)
        self.update_points()

    def calculate_initial_distances(self):
        distances = {}
        for start, end in self.constraints:
            start_point = self.points[start]
            end_point = self.points[end]
            distance = math.sqrt((start_point[0] - end_point[0])**2 + (start_point[1] - end_point[1])**2)
            distances[(start, end)] = distance
        return distances

    def apply_constraints(self):
        for start, end in self.constraints:
            start_point = self.points[start]
            end_point = self.points[end]
            current_distance = math.sqrt((start_point[0] - end_point[0])**2 + (start_point[1] - end_point[1])**2)
            target_distance = self.initial_distances[(start, end)]

            if current_distance != target_distance:
                scale = target_distance / current_distance
                mid_x = (start_point[0] + end_point[0]) / 2
                mid_y = (start_point[1] + end_point[1]) / 2

                self.points[start] = [
                    mid_x + (start_point[0] - mid_x) * scale,
                    mid_y + (start_point[1] - mid_y) * scale
                ]
                self.points[end] = [
                    mid_x + (end_point[0] - mid_x) * scale,
                    mid_y + (end_point[1] - mid_y) * scale
                ]

        # physics constrain rules for neck, spine01, and spine02 X positions
        neck_x = self.points["neck"][0]
        spine01_x = self.points["spine_01"][0]
        spine02_x = self.points["spine_02"][0]

        # neck in front of or equal to spine01
        if neck_x < spine01_x:
            self.points["neck"][0] = spine01_x

        # spine01 and spine02 within ±0.10 distance on X-axis
        spine_x_diff = spine01_x - spine02_x
        if abs(spine_x_diff) > 0.10:
            if spine_x_diff > 0:
                self.points["spine_01"][0] = spine02_x + 0.10
            else:
                self.points["spine_01"][0] = spine02_x - 0.10

        # spine01 is in front of or equal to spine02
        if self.points["spine_01"][0] < spine02_x:
            self.points["spine_01"][0] = spine02_x

        # spine01 was moved, check neck again
        if self.points["spine_01"][0] > self.points["neck"][0]:
            self.points["neck"][0] = self.points["spine_01"][0]

        # prevent spine02 Y value from being greater or equal to pelvis
        spine02_y = self.points["spine_02"][1]
        pelvis_y = self.points["pelvis"][1]

        if spine02_y >= pelvis_y:
            # spine02 slightly above pelvis always
            self.points["spine_02"][1] = pelvis_y - 0.01

        # adjusting spine02, recheck spine alignment
        self.align_spine()

    def align_spine(self):
        # spine01 is always above spine02
        if self.points["spine_01"][1] >= self.points["spine_02"][1]:
            self.points["spine_01"][1] = self.points["spine_02"][1] - 0.01

        # neck is always above spine01
        if self.points["neck"][1] >= self.points["spine_01"][1]:
            self.points["neck"][1] = self.points["spine_01"][1] - 0.01

    def update_points(self):
        self.point_list.clear()
        for name, coords in self.points.items():
            item = QTreeWidgetItem(self.point_list)
            item.setText(0, name)
            item.setText(1, f"{coords[0]:.2f}")
            item.setText(2, f"{coords[1]:.2f}")
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.canvas.update()
        self.update_json_output()

    def on_item_changed(self, item, column):
        if column in (1, 2):  # X or Y
            try:
                new_value = float(item.text(column))
                max_value = 1 if column == 1 else 2
                if 0 <= new_value <= max_value:
                    name = item.text(0)
                    self.points[name][column - 1] = new_value
                    self.apply_constraints()
                    self.canvas.update_points(self.points)
                    self.update_json_output()
                else:
                    raise ValueError
            except ValueError:
                coords = self.points[item.text(0)]
                item.setText(column, f"{coords[column - 1]:.2f}")

    def update_tree_widget(self):
        for i in range(self.point_list.topLevelItemCount()):
            item = self.point_list.topLevelItem(i)
            name = item.text(0)
            coords = self.points[name]
            item.setText(1, f"{coords[0]:.2f}")
            item.setText(2, f"{coords[1]:.2f}")
        self.update_json_output()

    def update_json_output(self):
        formatted_data = {
            self.pose_dropdown.currentText(): {
                key: [round(value[0], 2), round(value[1], 2)]
                for key, value in self.points.items()
            }
        }
        
        lines = ['{']
        lines.append(f'    "{self.pose_dropdown.currentText()}": ' + '{')
        for key, value in formatted_data[self.pose_dropdown.currentText()].items():
            lines.append(f'        "{key}": [{value[0]:.2f}, {value[1]:.2f}],')
        lines[-1] = lines[-1].rstrip(',')
        lines.append('    }')
        lines.append('}')
        
        formatted_json = '\n'.join(lines)
        self.json_output.setText(formatted_json)

class Canvas(QWidget):
    def __init__(self, points, update_callback, apply_constraints):
        super().__init__()
        self.setMinimumSize(400, 800)
        self.points = points
        self.update_callback = update_callback
        self.apply_constraints = apply_constraints
        self.LINE_THICKNESS = 3
        self.POINT_SIZE = 6
        self.dragging = False
        self.drag_point = None
        self.setMouseTracking(True)

    def update_points(self, points):
        self.points = points
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QPen(Qt.gray, 1))
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
        for i in range(1, 4):
            y = i * self.height() // 4
            painter.drawLine(0, y, self.width(), y)

        self.draw_stick_figure(painter)

    def draw_stick_figure(self, painter):
        color = QColor(0, 0, 0)
        painter.setPen(QPen(color, self.LINE_THICKNESS))

        self.draw_line(painter, "neck", "spine_01")
        self.draw_line(painter, "spine_01", "spine_02")
        self.draw_line(painter, "spine_02", "pelvis")

        self.draw_line(painter, "neck", "l_elbow")
        self.draw_line(painter, "l_elbow", "l_hand")
        self.draw_line(painter, "neck", "r_elbow")
        self.draw_line(painter, "r_elbow", "r_hand")

        self.draw_line(painter, "pelvis", "l_knee")
        self.draw_line(painter, "l_knee", "l_ankle")
        self.draw_line(painter, "l_ankle", "l_toe")
        self.draw_line(painter, "pelvis", "r_knee")
        self.draw_line(painter, "r_knee", "r_ankle")
        self.draw_line(painter, "r_ankle", "r_toe")

        self.draw_head(painter)

        painter.setPen(QPen(Qt.red, self.POINT_SIZE))
        for name, coords in self.points.items():
            if name != "r_shoulder":  # hard code inclusion of top_head and exclusion of r_shoulder
                x, y = coords
                point_x = int(x * self.width())
                point_y = int(y * self.height() / 2)
                painter.drawPoint(QPoint(point_x, point_y))

    def draw_line(self, painter, start_point, end_point):
        if start_point not in self.points or end_point not in self.points:
            return
        start = self.points[start_point]
        end = self.points[end_point]
        start_x, start_y = int(start[0] * self.width()), int(start[1] * self.height() / 2)
        end_x, end_y = int(end[0] * self.width()), int(end[1] * self.height() / 2)
        painter.drawLine(start_x, start_y, end_x, end_y)

    def draw_head(self, painter):
        if "neck" not in self.points or "top_head" not in self.points:
            return
        neck = self.points["neck"]
        top_head = self.points["top_head"]
        neck_x, neck_y = int(neck[0] * self.width()), int(neck[1] * self.height() / 2)
        top_head_x, top_head_y = int(top_head[0] * self.width()), int(top_head[1] * self.height() / 2)
        
        radius = abs(top_head_y - neck_y) // 2
        center_x = (neck_x + top_head_x) // 2
        center_y = (neck_y + top_head_y) // 2
        
        painter.drawEllipse(QPoint(center_x, center_y), radius, radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for name, coords in self.points.items():
                x, y = coords
                point_x = int(x * self.width())
                point_y = int(y * self.height() / 2)
                if abs(event.x() - point_x) < self.POINT_SIZE and abs(event.y() - point_y) < self.POINT_SIZE:
                    self.dragging = True
                    self.drag_point = name
                    break

    def mouseMoveEvent(self, event):
            if self.dragging and self.drag_point:
                new_x = event.x() / self.width()
                new_y = event.y() / (self.height() / 2)
                new_x = max(0, min(1, new_x))
                new_y = max(0, min(2, new_y))
                self.points[self.drag_point] = [new_x, new_y]
                self.apply_constraints()
                self.update()
                self.update_callback()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.drag_point = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = PoseTool()
    tool.show()
    sys.exit(app.exec_())