import frida
import sys
rdev = frida.get_remote_device()
front_app = rdev.get_frontmost_application()
print (front_app)
