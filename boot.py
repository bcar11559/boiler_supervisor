VERSION = "dev0.0.1"
print(f'Booting: Firmware version {VERSION}')

import webrepl
import ugit

ugit.pull_all()
webrepl.start()