import pyautogui
from pynput import mouse
from PIL import ImageStat
import numpy as np
from random import randint 

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
  crop_amount = 10
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
  print("Finding locked tiles", end="")
  for y in range(len(y_borders) - 1):
    print("\n ", end="")
    tiles.append([])

    for x in range(len(x_borders) - 1):
      new_tile = Tile(x, y, x_borders[x], x_borders[x+1], y_borders[y], y_borders[y+1])
      img = game_img.crop((new_tile.x_pos, new_tile.y_pos, new_tile.x_pos + new_tile.w, new_tile.y_pos + new_tile.h))
      if new_tile.determine_locked(img=img):
        print("#", end="")
      else:
        print(".", end="")
      tiles[y].append(new_tile)
  print()


  print("Getting colors")
  for y in range(len(tiles)):
    for x in range(len(tiles[y])):
      img = game_img.crop((tiles[y][x].x_pos, tiles[y][x].y_pos, tiles[y][x].x_pos + tiles[y][x].w, tiles[y][x].y_pos + tiles[y][x].h))
      tiles[y][x].determine_color(img)
  
  print("Solving")
  while True:
    
    for y in range(len(tiles)):
      for x in range(len(tiles[y])):

        if tiles[y][x].locked:
          continue
        
        
    return
      

  return

class Tile:
  
  # threshold to use when determining lock, based on summed stddev of all bands in the img
  lock_stddev_threshold = 15

  # number of samples to take when determining color
  color_samples = 500

  # the amount to crop off initialized size
  img_clip_amount = 10

  def __init__(self, _x, _y, x_min, x_max, y_min, y_max):
    self.x = _x
    self.y = _y
    self.x_pos = x_min + Tile.img_clip_amount
    self.y_pos = y_min + Tile.img_clip_amount
    self.w = (x_max - x_min) - (Tile.img_clip_amount * 2)
    self.h = (y_max - y_min) - (Tile.img_clip_amount * 2)
    self.center_x = (x_min + x_max) / 2
    self.center_y = (y_min + y_max) / 2
    self.color = None
    self.locked = False
  
  def determine_locked (self, img):
    stat = ImageStat.Stat(img)
    self.locked = sum(stat.stddev) > Tile.lock_stddev_threshold
    return self.locked

  def determine_color (self, col_img):
    colors = {}
    for i in range(Tile.color_samples):
      col = col_img.getpixel((randint(0, col_img.size[0] - 1), randint(0, col_img.size[1] - 1)))
      hex_col = "%02x%02x%02x" % col
      if hex_col not in colors:
        colors.update({hex_col: 1})
      else:
        colors[hex_col] += 1
    
    final_hex_col = ""
    highest_score = 0
    for col, score in colors.items():
      if score > highest_score:
        highest_score = score
        final_hex_col = col

    lv = len(final_hex_col)
    final = tuple(int(final_hex_col[i:i+lv//3], 16) for i in range(0, lv, lv//3))
    self.color = final
    return final
    

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