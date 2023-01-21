import pyautogui
from pynput import mouse
from PIL import ImageDraw
import numpy as np

mouse_x = 0
mouse_y = 0
mouse_pressed = False

def main():
  print("\n\n")

  # starting mouse listener
  listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click)
  listener.start()

  # waiting for input
  print("Click and drag a rectangle across the game screen")
  while mouse_pressed == False:
    pass
  start_x = mouse_x
  start_y = mouse_y
  while mouse_pressed:
    pass
  end_x = mouse_x
  end_y = mouse_y

  # x, y, w, h
  game_region = (min([start_x, end_x]), min([start_y, end_y]), max([start_x, end_x]) - min([start_x, end_x]), max([start_y, end_y]) - min([start_y, end_y]))
  
  # cropping edges
  crop_amount = 20
  game_region = (game_region[0] + crop_amount, game_region[1] + crop_amount, game_region[2] - 2*crop_amount, game_region[3] - 2*crop_amount)
  game_img = pyautogui.screenshot(region=game_region)
  game_img.save("game.png")
  #game_img.show()
  width, height = game_img.size
  print(f"Game size: {game_img.size}")

  x_borders = [0]
  y_borders = [0]

  # determining x dimension
  print("Determining game dimensions")
  possible_x_sizes = []
  for y in range(height):
    col = game_img.getpixel((0, y))
    switches = 1
    last_switch = 0
    for x in range(1, width, 5):
      new_col = game_img.getpixel((x, y))
      if new_col != col:
        col = new_col
        if (x - last_switch > 10):
          switches += 1
          last_switch = x
          if (y == 4):
            x_borders.append(x)

    while len(possible_x_sizes) <= switches:
      possible_x_sizes.append(0)
    possible_x_sizes[switches] += 1

  x_size = possible_x_sizes.index(max(possible_x_sizes))
  print(f" - x size: {x_size} [{(max(possible_x_sizes) / sum(possible_x_sizes)) * 100:.4}% confident]")
  # y dimension
  possible_y_sizes = []
  for x in range(width):
    col = game_img.getpixel((x, 0))
    switches = 1
    last_switch = 0
    for y in range(1, height, 5):
      new_col = game_img.getpixel((x, y))
      if new_col != col:
        col = new_col
        if y - last_switch > 10:
          switches += 1
          last_switch = y
          if (x == 4):
            y_borders.append(y)

    while len(possible_y_sizes) <= switches:
      possible_y_sizes.append(0)
    possible_y_sizes[switches] += 1

  y_size = possible_y_sizes.index(max(possible_y_sizes))
  print(f" - y size: {y_size} [{(max(possible_y_sizes) / sum(possible_y_sizes)) * 100:.4}% confident]")

  x_borders.append(width)
  y_borders.append(height)

  # identifying tiles
  tiles = []
  print("Parsing tiles")
  for y in range(len(y_borders) - 1):
    tiles.append([])
    for x in range(len(x_borders) - 1):
      new_tile = Tile(x, y, x_borders[x], x_borders[x+1], y_borders[y], y_borders[y+1])
      img = game_img.crop((new_tile.x_pos, new_tile.y_pos, new_tile.x_pos + new_tile.w, new_tile.y_pos + new_tile.h))
      colors = {}
      
      
      

  return

class Tile:
  def __init__(self, _x, _y, x_min, x_max, y_min, y_max):
    self.x = _x
    self.y = _y
    self.x_pos = x_min + 3
    self.y_pos = y_min + 3
    self.w = (x_max - x_min) - 6
    self.h = (y_max - y_min) - 6
    self.center_x = (x_min + x_max) / 2
    self.center_y = (y_min + y_max) / 2
    self.color = None

    pass

def on_move(x, y):
  global mouse_x, mouse_y
  mouse_x = x
  mouse_y = y

def on_click(x, y, button, pressed):
  global mouse_x, mouse_y, mouse_pressed
  mouse_x = x
  mouse_y = y
  mouse_pressed = pressed
  

if __name__ == "__main__":
  main()