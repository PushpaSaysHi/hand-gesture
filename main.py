import subprocess
import sys
import os

scripts = {
    "1": {"name": "Hand Detector",        "file": "hand_detector.py"},
    "2": {"name": "Volume Control",       "file": "volume_control.py"},
    "3": {"name": "Brightness Control",   "file": "brightness_control.py"},
    "4": {"name": "Mouse Control",        "file": "mouse_control.py"},
    "5": {"name": "Air Draw",             "file": "air_draw.py"},
    "6": {"name": "Snake Game",           "file": "snake_game.py"},
    "7": {"name": "Finger Counter",       "file": "finger_counter.py"},
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    clear()
    print("=" * 40)
    print("       🖐️  HAND GESTURE CONTROL")
    print("=" * 40)
    for key, val in scripts.items():
        file = val["file"]
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"  {key}.  {exists}  {val['name']}")
    print("=" * 40)
    print("  Q.  Quit")
    print("=" * 40)

while True:
    print_menu()
    choice = input("\n  Pick a feature: ").strip().lower()

    if choice == 'q':
        print("\n  Bye!\n")
        break

    elif choice in scripts:
        script = scripts[choice]
        file = script["file"]

        if not os.path.exists(file):
            print(f"\n  ❌ {file} not found in this folder!")
            input("  Press Enter to go back...")
            continue

        print(f"\n  Launching {script['name']}...")
        print(f"  Press Q or Esc inside the window to stop.\n")

        try:
            subprocess.run([sys.executable, file])
        except KeyboardInterrupt:
            pass

        input("\n  Press Enter to return to menu...")

    else:
        input("\n  Invalid choice. Press Enter to try again...")