import pyttsx3
import pyautogui as pag
import time

engine = pyttsx3.init()
voices = engine.getProperty('voices')
text_to_speak = "And Next"
engine.setProperty('voice', voices[76].id)  # Jester :]
def and_next():
    engine.say(text_to_speak)
    engine.runAndWait()
    engine.stop()

def go(amt):
    ret_points = []
    for _ in range(amt):
        print(_)
        x, y = pag.position()
        ret_points.append((x, y))
        and_next()
        time.sleep(2)
    return ret_points

amt = int(input("How many points do you want to get? "))
temp = go(amt) #[(411, 346), (408, 385), (428, 504), (449, 484), (429, 426), (448, 386), (448, 386), (468, 444), (506, 483), (507, 367), (528, 368), (528, 368), (525, 406), (525, 406), (547, 503)]

print(temp)
for i, v in enumerate(temp[1:]):
    if temp[i] == v:
        print(f"possible defect at point {i + 1}")
# print({i + 1: v for i, v in enumerate(temp)})

# if str(input("Wanna fix the faulty point(s)[say y if yes]? ")).lower() == "y":
#     for i, v in enumerate(temp[1:]):
#         if temp[i] == v:
#             time.sleep(2)
#             print(f"Fixing {i + 1}th point")
#             temp[i + 1] = pag.position()
#             print(f"New point: {temp[i].x, temp[i].y}")
#             and_next()
#     print(temp)