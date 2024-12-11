import sys

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from roku import Roku


class RokuRemote(QWidget):
    def __init__(self):
        super().__init__()

        self.roku = None
        self.setWindowTitle("Roku Remote")

        # Layout and Widgets
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.combo_box = QComboBox()
        self.combo_box.addItems(
            ["Select Roku", "Living Room Roku", "Master Bedroom Roku"]
        )
        self.combo_box.currentIndexChanged.connect(self.select_roku)
        self.layout.addWidget(self.combo_box, 0, 0, 1, 3)

        # Navigation Buttons
        self.add_button("Back", 1, 0, self.back)
        self.add_button("Home", 1, 2, self.home)

        # Spacer between Back/Home and Directional buttons
        self.layout.addItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            ),
            2,
            0,
            1,
            3,
        )

        self.add_button("Up", 3, 1, self.up)
        self.add_button("Left", 4, 0, self.left)
        self.add_button("Select", 4, 1, self.select)
        self.add_button("Right", 4, 2, self.right)
        self.add_button("Down", 5, 1, self.down)

        # Spacer between Directional and App buttons
        self.layout.addItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            ),
            6,
            0,
            1,
            3,
        )

        # App Buttons
        self.add_button("Netflix", 7, 0, self.launch_netflix)
        self.add_button("Amazon", 7, 1, self.launch_amazon)
        self.add_button("Apple TV", 7, 2, self.launch_apple)
        self.add_button("YouTube", 8, 0, self.launch_youtube)
        self.add_button("Hulu", 8, 1, self.launch_hulu)
        self.add_button("Max", 8, 2, self.launch_max)
        self.add_button("Plex", 9, 0, self.launch_plex)
        self.add_button("Disney Plus", 9, 1, self.launch_disney)
        self.add_button("Peacock", 9, 2, self.launch_peacock)

    def add_button(self, text, row, col, func):
        button = QPushButton(text)
        button.clicked.connect(func)
        self.layout.addWidget(button, row, col)

    def select_roku(self):
        selected = self.combo_box.currentText()
        if selected == "Living Room Roku":
            self.roku = Roku("192.168.68.106")
        elif selected == "Master Bedroom Roku":
            self.roku = Roku("192.168.68.107")
        else:
            self.roku = None

    def up(self):
        if self.roku:
            self.roku.up()

    def down(self):
        if self.roku:
            self.roku.down()

    def left(self):
        if self.roku:
            self.roku.left()

    def right(self):
        if self.roku:
            self.roku.right()

    def select(self):
        if self.roku:
            self.roku.select()

    def back(self):
        if self.roku:
            self.roku.back()

    def home(self):
        if self.roku:
            self.roku.home()

    def launch_netflix(self):
        if self.roku:
            try:
                netflix = self.roku["Netflix"]
                netflix.launch()
            except Exception as e:
                print(f"Error launching Netflix: {e}")

    def launch_amazon(self):
        if self.roku:
            try:
                amazon = self.roku["Prime Video"]
                amazon.launch()
            except Exception as e:
                print(f"Error launching Prime Video: {e}")

    def launch_apple(self):
        if self.roku:
            try:
                apple = self.roku["Apple TV"]
                apple.launch()
            except Exception as e:
                print(f"Error launching Apple TV: {e}")

    def launch_youtube(self):
        if self.roku:
            try:
                youtube = self.roku["YouTube"]
                youtube.launch()
            except Exception as e:
                print(f"Error launching Youtube: {e}")

    def launch_hulu(self):
        if self.roku:
            try:
                hulu = self.roku["Hulu"]
                hulu.launch()
            except Exception as e:
                print(f"Error launching Hulu: {e}")

    def launch_max(self):
        if self.roku:
            try:
                max = self.roku["Max"]
                max.launch()
            except Exception as e:
                print(f"Error launching Max: {e}")

    def launch_plex(self):
        if self.roku:
            try:
                plex = self.roku["Plex - Free Movies & TV"]
                plex.launch()
            except Exception as e:
                print(f"Error launching Plex: {e}")

    def launch_disney(self):
        if self.roku:
            try:
                disney = self.roku["Disney Plus"]
                disney.launch()
            except Exception as e:
                print(f"Error launching Disney: {e}")

    def launch_peacock(self):
        if self.roku:
            try:
                peacock = self.roku["Peacock TV"]
                peacock.launch()
            except Exception as e:
                print(f"Error launching Peacock: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RokuRemote()
    window.show()
    sys.exit(app.exec())
