import sys

import keyboard

from roku import Roku

ROKU_IP = "192.168.68.106"
roku = Roku(ROKU_IP)


# keyboard.add_hotkey(12, sys.exit(1))
keyboard.add_hotkey(13, roku.up)
keyboard.add_hotkey(1, roku.down)
keyboard.add_hotkey(0, roku.left)
keyboard.add_hotkey(2, roku.right)
keyboard.add_hotkey(49, roku.select)
keyboard.add_hotkey(11, roku.back)
keyboard.add_hotkey(4, roku.home)
keyboard.wait()
