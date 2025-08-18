import pyautogui as pag

pag.PAUSE = .15
def del_page():
    pag.moveTo(x=277, y=208)
    pag.dragTo(x=1234, y=745, duration=1, button='left')
    pag.press("delete")
    x, y = pag.size()
    pag.moveTo(x // 2, y // 2)
    pag.click()
    pag.hotkey('command', 'backspace')

def first_page(page_amt):
    for i in range(page_amt):
        pag.press("left")
    del_page()

def cpy():
    pag.moveTo(x=277, y=208)
    pag.dragTo(x=1234, y=745, duration=1, button='left')
    pag.hotkey('command', 'c')
    pag.click()

def newt():
    pag.moveTo(1051, 387, duration=0.5)
    pag.click()
    pag.hotkey('command', 'enter')
    pag.hotkey('command', 'v')
    pag.click()

def name_puter(names, locations):
    for name, location in zip(names, locations):
        pag.tripleClick(location, duration=0.3)
        pag.press('backspace')
        pag.write(name)

def grouper_9000(names, group_size):
    grouped = []
    for i in range(0, len(names), group_size):
        grouped.append(names[i:i + group_size])
    return grouped

#have names be names (integrate w/ my_edu_data.py)
#have locs be the locations of the text boxes on the page (integrate w/ pag_locations.py)
names = ['Kqgmj T', 'Odbt E', 'Nvbn T', 'Hxkxvcbopg E', 'Bqmuqdlrvw Y', 'Qoxsgexgpw G', 'Yfxz S', 'Anxwbxvj Y', 'Plevthhl Z', 'Msrqdvdaxgg X', 'Aymqkbdcujn E', 'Zccspei F', 'Qvudisfps M', 'Trnfmbn I', 'Btjqblo W', 'Iyrcpm D', 'Ulaanz Z', 'Sxuxjf T', 'Jjptq N', 'Yzikjubtjr F', 'Omdthwdz A', 'Klmjwwa G', 'Btulqkzgsn W', 'Dxoq S', 'Lqlxk E', 'Fbpiqp W', 'Cwqpkl F', 'Hcpbu V', 'Ghwfxtq C', 'Qkzteyblw S'] # data.names
letters = sorted(list("qwertyuiopasdfghjklzxcvbnm"))
locs = [(420, 479), (601, 418), (774, 472), (925, 413)]
grouped_names = grouper_9000(names, len(locs))

del_fp_counter = 0
cpy()
newt()
for i in grouped_names:
    name_puter(i, locs)
    newt()
    del_fp_counter += 1
del_page()
first_page(del_fp_counter)