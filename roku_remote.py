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
        self.connection_ok = False
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
            self.roku = Roku("192.168.0.100")
            self.test_connection()
        elif selected == "Master Bedroom Roku":
            self.roku = Roku("192.168.0.90")
            self.test_connection()
        else:
            self.roku = None
            self.connection_ok = False

    def test_connection(self):
        if self.roku:
            try:
                # Try to get device info to test connectivity
                info = self.roku.device_info
                device_name = getattr(info, "user_device_name", "Unknown Roku Device")
                print(f"Connected to Roku: {device_name}")

                # Test if device is in Limited mode by trying a simple command
                try:
                    # This will fail silently if in Limited mode but won't crash
                    pass  # We'll detect Limited mode when actual commands are sent
                except Exception:
                    pass

                self.connection_ok = True
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print(
                        f"Connected to Roku: {getattr(info, 'user_device_name', 'Unknown Roku Device')} (Limited Mode)"
                    )
                    print(
                        "Note: Device is in Limited mode - some functions may not work"
                    )
                    self.connection_ok = True  # Still connected, just limited
                else:
                    print(f"Warning: Could not connect to Roku device: {e}")
                    print(
                        "Check if the device is powered on and connected to the network"
                    )
                    self.connection_ok = False

    def up(self):
        if self.roku and self.connection_ok:
            try:
                self.roku.up()
            except Exception as e:
                error_msg = str(e)
                if error_msg == "b''":
                    print(
                        "Device not responding - check if Roku is powered on and connected"
                    )
                elif "Limited mode" in error_msg:
                    print(
                        "Roku is in Limited mode - complete setup or check parental controls"
                    )
                else:
                    print(f"Error sending up command: {e}")
        elif self.roku:
            print("Cannot send command - device connection failed")

    def down(self):
        if self.roku and self.connection_ok:
            try:
                self.roku.down()
            except Exception as e:
                error_msg = str(e)
                if error_msg == "b''":
                    print(
                        "Device not responding - check if Roku is powered on and connected"
                    )
                elif "Limited mode" in error_msg:
                    print(
                        "Roku is in Limited mode - complete setup or check parental controls"
                    )
                else:
                    print(f"Error sending down command: {e}")
        elif self.roku:
            print("Cannot send command - device connection failed")

    def left(self):
        if self.roku and self.connection_ok:
            try:
                self.roku.left()
            except Exception as e:
                error_msg = str(e)
                if error_msg == "b''":
                    print(
                        "Device not responding - check if Roku is powered on and connected"
                    )
                elif "Limited mode" in error_msg:
                    print(
                        "Roku is in Limited mode - complete setup or check parental controls"
                    )
                else:
                    print(f"Error sending left command: {e}")
        elif self.roku:
            print("Cannot send command - device connection failed")

    def right(self):
        if self.roku and self.connection_ok:
            try:
                self.roku.right()
            except Exception as e:
                error_msg = str(e)
                if error_msg == "b''":
                    print(
                        "Device not responding - check if Roku is powered on and connected"
                    )
                elif "Limited mode" in error_msg:
                    print(
                        "Roku is in Limited mode - complete setup or check parental controls"
                    )
                else:
                    print(f"Error sending right command: {e}")
        elif self.roku:
            print("Cannot send command - device connection failed")

    def select(self):
        if self.roku and self.connection_ok:
            try:
                self.roku.select()
            except Exception as e:
                error_msg = str(e)
                if error_msg == "b''":
                    print(
                        "Device not responding - check if Roku is powered on and connected"
                    )
                elif "Limited mode" in error_msg:
                    print(
                        "Roku is in Limited mode - complete setup or check parental controls"
                    )
                else:
                    print(f"Error sending select command: {e}")
        elif self.roku:
            print("Cannot send command - device connection failed")

    def back(self):
        if self.roku and self.connection_ok:
            try:
                self.roku.back()
            except Exception as e:
                error_msg = str(e)
                if error_msg == "b''":
                    print(
                        "Device not responding - check if Roku is powered on and connected"
                    )
                elif "Limited mode" in error_msg:
                    print(
                        "Roku is in Limited mode - complete setup or check parental controls"
                    )
                else:
                    print(f"Error sending back command: {e}")
        elif self.roku:
            print("Cannot send command - device connection failed")

    def home(self):
        if self.roku and self.connection_ok:
            try:
                self.roku.home()
            except Exception as e:
                error_msg = str(e)
                if error_msg == "b''":
                    print(
                        "Device not responding - check if Roku is powered on and connected"
                    )
                elif "Limited mode" in error_msg:
                    print(
                        "Roku is in Limited mode - complete setup or check parental controls"
                    )
                else:
                    print(f"Error sending home command: {e}")
        elif self.roku:
            print("Cannot send command - device connection failed")

    def launch_netflix(self):
        if self.roku:
            try:
                netflix = self.roku["Netflix"]
                netflix.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Netflix - Roku is in Limited mode")
                else:
                    print(f"Error launching Netflix: {e}")

    def launch_amazon(self):
        if self.roku:
            try:
                amazon = self.roku["Prime Video"]
                amazon.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Prime Video - Roku is in Limited mode")
                else:
                    print(f"Error launching Prime Video: {e}")

    def launch_apple(self):
        if self.roku:
            try:
                apple = self.roku["Apple TV"]
                apple.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Apple TV - Roku is in Limited mode")
                else:
                    print(f"Error launching Apple TV: {e}")

    def launch_youtube(self):
        if self.roku:
            try:
                youtube = self.roku["YouTube"]
                youtube.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch YouTube - Roku is in Limited mode")
                else:
                    print(f"Error launching Youtube: {e}")

    def launch_hulu(self):
        if self.roku:
            try:
                hulu = self.roku["Hulu"]
                hulu.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Hulu - Roku is in Limited mode")
                else:
                    print(f"Error launching Hulu: {e}")

    def launch_max(self):
        if self.roku:
            try:
                max = self.roku["Max"]
                max.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Max - Roku is in Limited mode")
                else:
                    print(f"Error launching Max: {e}")

    def launch_plex(self):
        if self.roku:
            try:
                plex = self.roku["Plex - Free Movies & TV"]
                plex.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Plex - Roku is in Limited mode")
                else:
                    print(f"Error launching Plex: {e}")

    def launch_disney(self):
        if self.roku:
            try:
                disney = self.roku["Disney Plus"]
                disney.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Disney Plus - Roku is in Limited mode")
                else:
                    print(f"Error launching Disney: {e}")

    def launch_peacock(self):
        if self.roku:
            try:
                peacock = self.roku["Peacock TV"]
                peacock.launch()
            except Exception as e:
                error_msg = str(e)
                if "Limited mode" in error_msg:
                    print("Cannot launch Peacock - Roku is in Limited mode")
                else:
                    print(f"Error launching Peacock: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RokuRemote()
    window.show()
    sys.exit(app.exec())
