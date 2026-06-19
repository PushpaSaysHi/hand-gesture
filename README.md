# 🖐️ Hand Gesture Control

> Control your computer with just your hand using Python, OpenCV and MediaPipe — no extra hardware needed, just a webcam.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

## 📁 Features

| # | Script | Description |
|---|--------|-------------|
| 1 | `hand_detector.py` | Detects hands in frame and counts how many |
| 2 | `finger_counter.py` | Counts fingers and recognizes gestures like fist, peace, thumbs up |
| 3 | `volume_control.py` | Pinch fingers to control system volume |
| 4 | `brightness_control.py` | Pinch fingers to control screen brightness |
| 5 | `mouse_control.py` | Move mouse with index finger, pinch to click |
| 6 | `air_draw.py` | Draw in the air with your index finger |
| 7 | `snake_game.py` | Play snake using hand gestures |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/hand-gesture-control.git
cd hand-gesture-control
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the launcher
```bash
python main.py
```

Or run any script directly:
```bash
python volume_control.py
python snake_game.py
```

---

## 📦 Requirements

```
opencv-python
mediapipe
numpy
pycaw
comtypes
pyautogui
screen-brightness-control
```

> ⚠️ `pycaw` and `screen-brightness-control` are **Windows only**

---

## 🎮 Controls

### Volume & Brightness Control
| Gesture | Action |
|---------|--------|
| 🤏 Pinch fingers together | Minimum volume/brightness |
| ✋ Open hand wide | Maximum volume/brightness |

### Mouse Control
| Gesture | Action |
|---------|--------|
| ☝️ Move index finger | Move cursor |
| 🤏 Pinch index + thumb | Left click |

### Air Draw
| Action | What it does |
|--------|-------------|
| ☝️ Move index finger | Draw on screen |
| ✊ Fist | Erase |
| Tap toolbar buttons | Change color / clear |
| `+` / `-` keys | Increase / decrease brush size |

### Snake Game
| Gesture | Action |
|---------|--------|
| Point finger right of palm | Move right |
| Point finger left of palm | Move left |
| Point finger above palm | Move up |
| Point finger below palm | Move down |
| `R` key | Restart after game over |

---

## 🗂️ Project Structure

```
hand-gesture-control/
│
├── main.py                  # launcher menu
├── hand_detector.py         
├── finger_counter.py        
├── volume_control.py        
├── brightness_control.py    
├── mouse_control.py         
├── air_draw.py              
├── snake_game.py            
├── requirements.txt         
└── README.md                
```

---

## 🛠️ Built With

- [Python](https://python.org)
- [OpenCV](https://opencv.org)
- [MediaPipe](https://mediapipe.dev)
- [pycaw](https://github.com/AndreMiras/pycaw)
- [PyAutoGUI](https://pyautogui.readthedocs.io)
- [screen-brightness-control](https://github.com/Crozzers/screen-brightness-control)

---

## 📌 Notes

- Works best with good lighting
- Keep your hand clearly visible in the frame
- Press `Q` or `Esc` to quit any script

---

## 👤 Author

Made by **Puspa Mandal**  
GitHub: [@PushpaSaysHi](https://github.com/PushpaSaysHi)