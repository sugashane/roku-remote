import sys
from dataclasses import dataclass
from functools import partial

from PyQt6.QtCore import QDateTime, QObject, QSettings, QThread, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from roku import Roku

PREFERRED_APPS = [
    "Netflix",
    "Prime Video",
    "Apple TV",
    "YouTube",
    "Hulu",
    "Max",
    "Disney Plus",
    "Plex - Free Movies & TV",
    "Peacock TV",
]

TV_CONTROLS = [
    ("Vol -", "volume_down"),
    ("Mute", "volume_mute"),
    ("Vol +", "volume_up"),
    ("TV", "input_tuner"),
    ("HDMI 1", "input_hdmi1"),
    ("HDMI 2", "input_hdmi2"),
    ("HDMI 3", "input_hdmi3"),
    ("HDMI 4", "input_hdmi4"),
]


@dataclass(frozen=True)
class DeviceRecord:
    name: str
    host: str
    port: int
    model_name: str
    roku_type: str
    serial_num: str

    @property
    def label(self):
        return f"{self.name} ({self.model_name} • {self.host})"


class DiscoveryWorker(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def run(self):
        try:
            rokus = Roku.discover(timeout=2, retries=2)
        except Exception as exc:
            self.failed.emit(f"Discovery failed: {exc}")
            return

        devices = []
        seen_hosts = set()

        for roku in rokus:
            if roku.host in seen_hosts:
                continue

            seen_hosts.add(roku.host)

            try:
                info = roku.device_info
                devices.append(
                    DeviceRecord(
                        name=getattr(info, "user_device_name", f"Roku {roku.host}"),
                        host=roku.host,
                        port=roku.port,
                        model_name=getattr(info, "model_name", "Unknown model"),
                        roku_type=getattr(info, "roku_type", "Unknown type"),
                        serial_num=getattr(info, "serial_num", "Unknown serial"),
                    )
                )
            except Exception:
                devices.append(
                    DeviceRecord(
                        name=f"Roku {roku.host}",
                        host=roku.host,
                        port=roku.port,
                        model_name="Unknown model",
                        roku_type="Unknown type",
                        serial_num="Unavailable",
                    )
                )

        devices.sort(key=lambda device: (device.name.lower(), device.host))
        self.finished.emit(devices)


class RokuRemote(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("roku-remote", "roku-remote")
        self.roku = None
        self.connected_device = None
        self.devices = []
        self.apps_by_id = {}
        self.discovery_thread = None
        self.discovery_worker = None
        self.device_controls = []
        self.favorite_buttons = []

        self.setWindowTitle("Roku Remote")
        self.resize(980, 860)

        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(14)
        self.content_widget.setLayout(self.layout)

        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

        self.build_device_section()
        self.build_navigation_section()
        self.build_text_section()
        self.build_apps_section()
        self.build_tv_section()
        self.build_log_section()
        self.setup_shortcuts()
        self.update_device_controls()

        QTimer.singleShot(0, self.refresh_devices)

    def build_device_section(self):
        group = QGroupBox("Devices")
        layout = QGridLayout()
        group.setLayout(layout)

        self.device_combo = QComboBox()
        self.device_combo.addItem("Discovering Roku devices…")
        self.device_combo.currentIndexChanged.connect(self.handle_device_selected)

        self.refresh_button = QPushButton("Refresh Devices")
        self.refresh_button.clicked.connect(self.refresh_devices)

        self.refresh_status_button = QPushButton("Refresh Status")
        self.refresh_status_button.clicked.connect(self.refresh_device_state)

        self.connection_label = QLabel("Not connected")
        self.device_details_label = QLabel("No Roku selected yet.")
        self.current_app_label = QLabel("Current app: Unknown")

        layout.addWidget(QLabel("Choose Roku:"), 0, 0)
        layout.addWidget(self.device_combo, 0, 1)
        layout.addWidget(self.refresh_button, 0, 2)
        layout.addWidget(self.refresh_status_button, 0, 3)
        layout.addWidget(self.connection_label, 1, 0, 1, 4)
        layout.addWidget(self.device_details_label, 2, 0, 1, 4)
        layout.addWidget(self.current_app_label, 3, 0, 1, 4)

        self.layout.addWidget(group)
        self.device_controls.extend([self.device_combo, self.refresh_status_button])

    def build_navigation_section(self):
        group = QGroupBox("Navigation")
        layout = QGridLayout()
        group.setLayout(layout)
        group.setStyleSheet(
            """
            QGroupBox QPushButton[navRole] {
                color: #1f2937;
                background-color: #f4f6fb;
                border: 1px solid #cfd7e6;
            }
            QGroupBox QPushButton[navRole]:hover {
                background-color: #e8edf8;
                border: 1px solid #b8c4dc;
            }
            QGroupBox QPushButton[navRole]:pressed {
                background-color: #dbe4f5;
                border: 1px solid #9cafcf;
            }
            QGroupBox QPushButton[navRole]:disabled {
                color: #7b8798;
                background-color: #f5f5f5;
                border: 1px solid #dddddd;
            }
            QGroupBox QPushButton[navRole="top"] {
                min-width: 98px;
                min-height: 40px;
                padding: 5px 10px;
                font-weight: 600;
                border-radius: 12px;
            }
            QGroupBox QPushButton[navRole="direction"] {
                min-width: 78px;
                min-height: 58px;
                padding: 6px 10px;
                font-weight: 600;
                border-radius: 18px;
            }
            QGroupBox QPushButton[navRole="center"] {
                min-width: 88px;
                min-height: 64px;
                padding: 6px 10px;
                font-weight: 700;
                border-radius: 22px;
                background-color: #dfe8fb;
                border: 1px solid #a8badf;
            }
            QGroupBox QPushButton[navRole="utility"] {
                min-width: 180px;
                min-height: 40px;
                padding: 5px 14px;
                font-weight: 600;
                border-radius: 16px;
            }
            """
        )
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(10)
        layout.setRowMinimumHeight(1, 12)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(6, 1)

        buttons = [
            ("Back", 0, 1, partial(self.send_command, "back", "Back"), "top"),
            ("Home", 0, 2, partial(self.send_command, "home", "Home", True), "top"),
            ("Replay", 0, 4, partial(self.send_command, "replay", "Replay"), "top"),
            ("Info", 0, 5, partial(self.send_command, "info", "Info"), "top"),
            ("Up", 2, 3, partial(self.send_command, "up", "Up"), "direction"),
            ("Left", 3, 2, partial(self.send_command, "left", "Left"), "direction"),
            ("Select", 3, 3, partial(self.send_command, "select", "Select", True), "center"),
            ("Right", 3, 4, partial(self.send_command, "right", "Right"), "direction"),
            ("Down", 4, 3, partial(self.send_command, "down", "Down"), "direction"),
            ("Find Remote", 5, 2, partial(self.send_command, "find_remote", "Find Remote"), "utility"),
        ]

        for text, row, column, handler, role in buttons:
            span = 3 if text == "Find Remote" else 1
            self.add_button(
                layout,
                text,
                row,
                column,
                handler,
                column_span=span,
                nav_role=role,
            )

        self.layout.addWidget(group)

    def build_text_section(self):
        group = QGroupBox("Text Input & Search")
        layout = QGridLayout()
        group.setLayout(layout)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type text for Roku search fields or app login screens")
        self.text_input.returnPressed.connect(self.type_text)

        type_button = QPushButton("Type Text")
        type_button.clicked.connect(self.type_text)

        search_button = QPushButton("Roku Search")
        search_button.clicked.connect(self.search_on_roku)

        enter_button = QPushButton("Enter")
        enter_button.clicked.connect(partial(self.send_command, "enter", "Enter", True))

        backspace_button = QPushButton("Backspace")
        backspace_button.clicked.connect(partial(self.send_command, "backspace", "Backspace"))

        clear_button = QPushButton("Clear Box")
        clear_button.clicked.connect(self.text_input.clear)

        layout.addWidget(self.text_input, 0, 0, 1, 5)
        layout.addWidget(type_button, 1, 0)
        layout.addWidget(search_button, 1, 1)
        layout.addWidget(enter_button, 1, 2)
        layout.addWidget(backspace_button, 1, 3)
        layout.addWidget(clear_button, 1, 4)

        self.layout.addWidget(group)
        self.device_controls.extend(
            [self.text_input, type_button, search_button, enter_button, backspace_button]
        )

    def build_apps_section(self):
        group = QGroupBox("Apps")
        layout = QGridLayout()
        group.setLayout(layout)

        self.favorite_apps_widget = QWidget()
        self.favorite_apps_layout = QGridLayout()
        self.favorite_apps_widget.setLayout(self.favorite_apps_layout)

        self.app_filter = QLineEdit()
        self.app_filter.setPlaceholderText("Filter installed apps")
        self.app_filter.textChanged.connect(self.filter_apps)

        self.app_list = QListWidget()
        self.app_list.itemDoubleClicked.connect(self.launch_selected_app)

        self.launch_app_button = QPushButton("Launch Selected App")
        self.launch_app_button.clicked.connect(self.launch_selected_app)

        self.refresh_apps_button = QPushButton("Refresh Apps")
        self.refresh_apps_button.clicked.connect(self.load_apps)

        layout.addWidget(QLabel("Quick Launch"), 0, 0, 1, 2)
        layout.addWidget(self.favorite_apps_widget, 1, 0, 1, 2)
        layout.addWidget(self.app_filter, 2, 0, 1, 2)
        layout.addWidget(self.app_list, 3, 0, 1, 2)
        layout.addWidget(self.launch_app_button, 4, 0)
        layout.addWidget(self.refresh_apps_button, 4, 1)

        self.layout.addWidget(group, stretch=1)
        self.device_controls.extend(
            [self.app_filter, self.app_list, self.launch_app_button, self.refresh_apps_button]
        )

    def build_tv_section(self):
        group = QGroupBox("TV Controls")
        layout = QGridLayout()
        group.setLayout(layout)

        for index, (label, command_name) in enumerate(TV_CONTROLS):
            row = index // 4
            column = index % 4
            self.add_button(
                layout,
                label,
                row,
                column,
                partial(self.send_command, command_name, label, True),
            )

        self.layout.addWidget(group)

    def build_log_section(self):
        group = QGroupBox("Activity")
        layout = QVBoxLayout()
        group.setLayout(layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(180)
        layout.addWidget(self.log_output)

        self.layout.addWidget(group)

    def setup_shortcuts(self):
        bindings = [
            ("Up", partial(self.send_command, "up", "Up")),
            ("Down", partial(self.send_command, "down", "Down")),
            ("Left", partial(self.send_command, "left", "Left")),
            ("Right", partial(self.send_command, "right", "Right")),
            ("Return", partial(self.send_command, "select", "Select", True)),
            ("Enter", partial(self.send_command, "select", "Select", True)),
            ("Escape", partial(self.send_command, "back", "Back")),
            ("H", partial(self.send_command, "home", "Home", True)),
        ]

        for key_sequence, handler in bindings:
            shortcut = QShortcut(key_sequence, self)
            shortcut.activated.connect(partial(self.handle_shortcut, handler))

    def handle_shortcut(self, handler):
        if isinstance(self.focusWidget(), QLineEdit):
            return

        handler()

    def add_button(self, layout, text, row, column, handler, column_span=1, nav_role=None):
        button = QPushButton(text)
        button.setMinimumHeight(40)
        if nav_role is not None:
            button.setProperty("navRole", nav_role)
        button.clicked.connect(handler)
        layout.addWidget(button, row, column, 1, column_span)
        self.device_controls.append(button)
        return button

    def append_log(self, message):
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_output.append(f"[{timestamp}] {message}")

    def set_connection_status(self, text):
        self.connection_label.setText(text)

    def refresh_devices(self):
        if self.discovery_thread and self.discovery_thread.isRunning():
            self.append_log("Discovery is already running.")
            return

        self.set_connection_status("Scanning for Roku devices…")
        self.device_details_label.setText("Searching your network for Roku players and TVs.")
        self.current_app_label.setText("Current app: Unknown")
        self.device_combo.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.append_log("Starting Roku discovery.")

        self.discovery_thread = QThread(self)
        self.discovery_worker = DiscoveryWorker()
        self.discovery_worker.moveToThread(self.discovery_thread)

        self.discovery_thread.started.connect(self.discovery_worker.run)
        self.discovery_worker.finished.connect(self.handle_discovery_finished)
        self.discovery_worker.failed.connect(self.handle_discovery_failed)
        self.discovery_worker.finished.connect(self.discovery_thread.quit)
        self.discovery_worker.failed.connect(self.discovery_thread.quit)
        self.discovery_worker.finished.connect(self.discovery_worker.deleteLater)
        self.discovery_worker.failed.connect(self.discovery_worker.deleteLater)
        self.discovery_thread.finished.connect(self.discovery_thread.deleteLater)
        self.discovery_thread.finished.connect(self.cleanup_discovery_thread)

        self.discovery_thread.start()

    def cleanup_discovery_thread(self):
        self.discovery_thread = None
        self.discovery_worker = None
        self.device_combo.setEnabled(True)
        self.refresh_button.setEnabled(True)

    def handle_discovery_finished(self, devices):
        self.devices = devices
        self.populate_device_combo()

        if not devices:
            self.disconnect_device("No Roku devices were found.")
            self.append_log("Discovery finished with no devices found.")
            return

        self.append_log(f"Discovered {len(devices)} Roku device(s).")
        self.set_connection_status("Choose a Roku to connect.")

        preferred_host = self.settings.value("last_device_host", "", str)
        selected_index = 1

        for index, device in enumerate(devices, start=1):
            if device.host == preferred_host:
                selected_index = index
                break

        self.device_combo.setCurrentIndex(selected_index)

    def handle_discovery_failed(self, message):
        self.populate_device_combo()
        self.disconnect_device(message)
        self.append_log(message)

    def populate_device_combo(self):
        self.device_combo.blockSignals(True)
        self.device_combo.clear()
        self.device_combo.addItem("Select Roku", None)

        for device in self.devices:
            self.device_combo.addItem(device.label, device)

        self.device_combo.blockSignals(False)

    def handle_device_selected(self, index):
        if index <= 0:
            self.disconnect_device("Select a Roku to begin.")
            return

        selected_device = self.device_combo.currentData(Qt.ItemDataRole.UserRole)
        if selected_device is None:
            self.disconnect_device("Select a Roku to begin.")
            return

        self.connect_to_device(selected_device)

    def connect_to_device(self, device):
        self.roku = Roku(device.host, device.port)

        try:
            info = self.roku.device_info
        except Exception as exc:
            self.disconnect_device(self.describe_error("Could not connect to Roku", exc))
            return

        self.connected_device = DeviceRecord(
            name=getattr(info, "user_device_name", device.name),
            host=device.host,
            port=device.port,
            model_name=getattr(info, "model_name", device.model_name),
            roku_type=getattr(info, "roku_type", device.roku_type),
            serial_num=getattr(info, "serial_num", device.serial_num),
        )

        self.settings.setValue("last_device_host", device.host)
        self.append_log(f"Connected to {self.connected_device.name} at {device.host}.")
        self.refresh_device_state(load_apps=True)

    def disconnect_device(self, status_message):
        self.roku = None
        self.connected_device = None
        self.apps_by_id = {}
        self.set_connection_status(status_message)
        self.device_details_label.setText("No active Roku connection.")
        self.current_app_label.setText("Current app: Unknown")
        self.app_list.clear()
        self.reset_favorites()
        self.update_device_controls()

    def refresh_device_state(self, load_apps=False):
        if not self.ensure_connected():
            return

        try:
            info = self.roku.device_info
        except Exception as exc:
            self.disconnect_device(self.describe_error("Connection lost", exc))
            return

        self.connected_device = DeviceRecord(
            name=getattr(info, "user_device_name", self.connected_device.name),
            host=self.roku.host,
            port=self.roku.port,
            model_name=getattr(info, "model_name", "Unknown model"),
            roku_type=getattr(info, "roku_type", "Unknown type"),
            serial_num=getattr(info, "serial_num", "Unknown serial"),
        )

        self.set_connection_status(f"Connected to {self.connected_device.name}")
        self.device_details_label.setText(
            f"{self.connected_device.roku_type} • {self.connected_device.model_name} • "
            f"Serial {self.connected_device.serial_num} • {self.connected_device.host}"
        )
        self.refresh_current_app_label()
        self.update_device_controls()

        if load_apps:
            self.load_apps()

    def refresh_current_app_label(self):
        if not self.roku:
            self.current_app_label.setText("Current app: Unknown")
            return

        try:
            current_app = self.roku.current_app
        except Exception as exc:
            self.current_app_label.setText("Current app: Unknown")
            self.append_log(self.describe_error("Could not fetch current app", exc))
            return

        if current_app is None:
            self.current_app_label.setText("Current app: None")
            return

        suffix = " (screensaver)" if getattr(current_app, "is_screensaver", False) else ""
        self.current_app_label.setText(f"Current app: {current_app.name}{suffix}")

    def load_apps(self):
        if not self.ensure_connected():
            return

        try:
            apps = sorted(self.roku.apps, key=lambda app: app.name.lower())
        except Exception as exc:
            self.append_log(self.describe_error("Could not load apps", exc))
            return

        self.apps_by_id = {app.id: app for app in apps}
        self.app_list.clear()

        for app in apps:
            item = QListWidgetItem(app.name)
            item.setData(Qt.ItemDataRole.UserRole, app.id)
            self.app_list.addItem(item)

        self.populate_favorites(apps)
        self.filter_apps(self.app_filter.text())
        self.append_log(f"Loaded {len(apps)} installed app(s).")

    def populate_favorites(self, apps):
        self.reset_favorites()

        ranked_apps = []
        used_ids = set()

        for preferred_name in PREFERRED_APPS:
            for app in apps:
                if app.id in used_ids:
                    continue
                if app.name == preferred_name:
                    ranked_apps.append(app)
                    used_ids.add(app.id)
                    break

        for app in apps:
            if len(ranked_apps) >= 6:
                break
            if app.id in used_ids:
                continue
            ranked_apps.append(app)
            used_ids.add(app.id)

        if not ranked_apps:
            placeholder = QLabel("No apps available yet.")
            self.favorite_apps_layout.addWidget(placeholder, 0, 0)
            self.favorite_buttons.append(placeholder)
            return

        for index, app in enumerate(ranked_apps):
            button = QPushButton(app.name)
            button.clicked.connect(partial(self.launch_app, app.id))
            button.setMinimumHeight(36)
            self.favorite_apps_layout.addWidget(button, index // 3, index % 3)
            self.favorite_buttons.append(button)

    def reset_favorites(self):
        while self.favorite_apps_layout.count():
            item = self.favorite_apps_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.favorite_buttons = []

    def filter_apps(self, text):
        text = text.strip().lower()

        for index in range(self.app_list.count()):
            item = self.app_list.item(index)
            item.setHidden(text not in item.text().lower())

    def launch_selected_app(self, _item=None):
        item = self.app_list.currentItem()
        if item is None:
            self.append_log("Choose an app from the list first.")
            return

        app_id = item.data(Qt.ItemDataRole.UserRole)
        self.launch_app(app_id)

    def launch_app(self, app_id):
        if not self.ensure_connected():
            return

        app = self.apps_by_id.get(str(app_id))
        if app is None:
            self.append_log("That app is no longer available. Refresh the app list.")
            return

        try:
            app.launch()
        except Exception as exc:
            self.append_log(self.describe_error(f"Could not launch {app.name}", exc))
            return

        self.append_log(f"Launched {app.name}.")
        self.refresh_current_app_label()

    def type_text(self):
        if not self.ensure_connected():
            return

        text = self.text_input.text()
        if not text:
            self.append_log("Enter some text first.")
            return

        try:
            self.roku.literal(text)
        except Exception as exc:
            self.append_log(self.describe_error("Could not type text", exc))
            return

        self.append_log(f"Typed text: {text}")

    def search_on_roku(self):
        if not self.ensure_connected():
            return

        text = self.text_input.text().strip()
        if not text:
            self.append_log("Enter text to search for first.")
            return

        try:
            self.roku.search(title=text)
        except Exception as exc:
            self.append_log(self.describe_error("Could not search on Roku", exc))
            return

        self.append_log(f"Sent Roku search for: {text}")
        self.refresh_current_app_label()

    def send_command(self, command_name, label, refresh_state=False):
        if not self.ensure_connected():
            return

        try:
            getattr(self.roku, command_name)()
        except Exception as exc:
            self.append_log(self.describe_error(f"Could not send {label}", exc))
            return

        self.append_log(f"Sent {label}.")

        if refresh_state:
            self.refresh_current_app_label()

    def ensure_connected(self):
        if self.roku is not None:
            return True

        self.append_log("Connect to a Roku device first.")
        return False

    def update_device_controls(self):
        connected = self.roku is not None

        for widget in self.device_controls:
            if widget is self.device_combo:
                widget.setEnabled(True)
                continue

            widget.setEnabled(connected)

        for widget in self.favorite_buttons:
            if isinstance(widget, QPushButton):
                widget.setEnabled(connected)

    def describe_error(self, prefix, exc):
        error_text = str(exc)

        if error_text == "b''":
            return f"{prefix}: device did not respond. Check power and network."

        if "Limited mode" in error_text:
            return (
                f"{prefix}: Roku is in Limited mode. Finish setup or review parental controls."
            )

        return f"{prefix}: {error_text}"


def main():
    QApplication.setOrganizationName("roku-remote")
    QApplication.setApplicationName("roku-remote")
    app = QApplication(sys.argv)
    window = RokuRemote()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
