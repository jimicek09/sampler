tell application "System Settings" to activate
delay 0.4
open location "x-apple.systempreferences:com.apple.preference.security?Privacy_InputMonitoring"
delay 0.4
open location "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
delay 0.6
display dialog "Add your Terminal (Terminal/iTerm) and the Python interpreter (e.g. /Users/xoundboy/sampler/.venv/bin/python3).\nThen quit and reopen Terminal before rerunning the script." buttons {"OK"} default button "OK"
