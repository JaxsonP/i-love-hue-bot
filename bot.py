import pyautogui
from pynput import mouse
from PIL import ImageStat, Image, ImageDraw
import numpy as np
from random import randint 
import time

mouse_x = 0
mouse_y = 0
mouse_pressed = False

x_size = 0
y_size = 0

def main():
  global x_size, y_size

  print("\n\n")

  # starting mouse listener
  listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click)
  listener.start()

  """# waiting for input
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
  game_region = (game_region[0] + crop_amount, game_region[1] + crop_amount, game_region[2] - 2*crop_amount, game_region[3] - 2*crop_amount)"""
  #game_img = pyautogui.screenshot(region=game_region)
  game_img = Image.open("game.png")
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
  print("getting matches")
  # getting matches
  for y in range(len(tiles)):
    for x in range(len(tiles[y])):
      #print(f"Pos: {x}, {y} | ", end="")
      if tiles[y][x].locked:
        pass

      # gathering neighbors
      neighbors = []
      if x > 0: # has left neighbor
        neighbors.append((-1, 0))
      if x < x_size - 1: # has right neighbor
        neighbors.append((1, 0))
      if y > 0: # has upper neighbor
        neighbors.append((0, -1))
      if y < y_size - 1: # has lower neighbor
        neighbors.append((0, 1))

      # gathering unlocked neighbors
      unlocked_neighbors = []
      for neighbor in neighbors:
        if tiles[y + neighbor[1]][x + neighbor[0]].locked == False:
          unlocked_neighbors.append(neighbor)
      
      other_tiles = []
      for alt_y in range(len(tiles)):
        for alt_x in range(len(tiles[alt_y])):
          if alt_y != y or alt_x != x:
            other_tiles.append(tiles[alt_y][alt_x])

      # finding best matches
      matches = []
      for i in range(len(neighbors)):
        best_tile = None
        lowest_delta = 1_000_000
        for comp_tile in other_tiles:
          delta = abs(tiles[y][x].color[0] - comp_tile.color[0]) # r
          delta += abs(tiles[y][x].color[1] - comp_tile.color[1]) # g
          delta += abs(tiles[y][x].color[2] - comp_tile.color[2]) # b
          if delta < lowest_delta and comp_tile not in matches:
            lowest_delta = delta
            best_tile = comp_tile

        matches.append(best_tile)
      tiles[y][x].matches = matches
      #print([f"{a.x}, {a.y}" for a in matches])

  # getting order of piece solving
  print("Getting order")
  order = []
  distance = 0
  new_tiles = 0
  while True:
    for y in range(len(tiles)):
      for x in range(len(tiles[y])):
        if tiles[y][x].locked or tiles[y][x].distance_from_lock >= 0:
          continue
        
        if y > 0 and tiles[y - 1][x].distance_from_lock == distance:
          pass
        elif y < y_size - 1 and tiles[y + 1][x].distance_from_lock == distance:
          pass
        elif x > 0 and tiles[y][x - 1].distance_from_lock == distance:
          pass
        elif x < x_size - 1 and tiles[y][x + 1].distance_from_lock == distance:
          pass
        else:
          continue
        
        tiles[y][x].distance_from_lock = distance + 1
        order.append((x, y))
        new_tiles += 1
    
    distance += 1
    if (new_tiles == 0):
      break
    new_tiles = 0
  
  """print("Getting matches")
  # identifying possible colors:
  for pos in order:
    x = pos[0]
    y = pos[1]
    print(f"Pos: {x}, {y} | ", end="")

    possible_tiles = []
    if y > 0 and tiles[y - 1][x].distance_from_lock == tiles[y][x].distance_from_lock - 1:
      possible_tiles.extend(tiles[y - 1][x].matches)
    if y < y_size - 1 and tiles[y + 1][x].distance_from_lock == tiles[y][x].distance_from_lock - 1:
      possible_tiles.extend(tiles[y + 1][x].matches)
    if x > 0 and tiles[y][x - 1].distance_from_lock == tiles[y][x].distance_from_lock - 1:
      possible_tiles.extend(tiles[y][x - 1].matches)
    if x < x_size - 1 and tiles[y][x + 1].distance_from_lock == tiles[y][x].distance_from_lock - 1:
      possible_tiles.extend(tiles[y][x + 1].matches)

    
    possible_colors = []
    for tile in possible_tiles:
      if tile.color not in possible_colors:
        possible_colors.append(tile.color)
    tiles[y][x].possible_colors = possible_colors
    print(possible_colors)"""

  print("Starting recursive sort")
  result = recursive_sort(order, tiles)

  #print(result)
  solution_img = Image.new("RGB", (x_size * 50, y_size * 50))
  solution_img_draw = ImageDraw.Draw(solution_img)
  for y in range(len(tiles)):
    for x in range(len(tiles[y])):
      print("%02x%02x%02x " % result[y][x].color, end="")
      solution_img_draw.rectangle([(x * 50, y * 50), (x * 50 + 50, y * 50 + 50)], fill=result[y][x].color)
    print()
  solution_img.show()
  # main
  return

def recursive_sort (queue, tiles):
  global x_size, y_size
  x, y = queue.pop(0)
  if len(queue) <= 0:
    return tiles
  print(f"Pos: {x}, {y} | ", end="")

  # getting possible colors for this tile:
  all_matches = []
  if y > 0 and tiles[y - 1][x].distance_from_lock < tiles[y][x].distance_from_lock:
    all_matches.extend([tile for tile in tiles[y - 1][x].matches])
  if y < y_size - 1 and tiles[y + 1][x].distance_from_lock < tiles[y][x].distance_from_lock:
    all_matches.extend([tile for tile in tiles[y + 1][x].matches])
  if x > 0 and tiles[y][x - 1].distance_from_lock < tiles[y][x].distance_from_lock:
    all_matches.extend([tile for tile in tiles[y][x - 1].matches])
  if x < x_size - 1 and tiles[y][x + 1].distance_from_lock < tiles[y][x].distance_from_lock:
    all_matches.extend([tile for tile in tiles[y][x + 1].matches])

  possible_colors = []
  for match in all_matches:
    if match.color not in possible_colors:
      possible_colors.append(match.color)
  
  print(possible_colors)

  #print(["%02x%02x%02x " % c.color for c in tiles[y][x].matches])
  for color_to_swap in possible_colors:
    print("  Searching for " + str(color_to_swap))
    found_match = False
    for alt_y in range(len(tiles)):
      for alt_x in range(len(tiles[alt_y])):
        
        if tiles[alt_y][alt_x].color == color_to_swap:
          if tiles[alt_y][alt_x].distance_from_lock < tiles[y][x].distance_from_lock:
            print("    found sub")
            continue
          # o keia ka swap e hana
          found_match = True
          
          # copying array
          new_tiles = []
          for new_y in range(len(tiles)):
            new_tiles.append([])
            for new_x in range(len(tiles[new_y])):
              new_tiles[new_y].append(tiles[new_y][new_x])
          
          # swapping
          new_tiles[alt_y][alt_x].color = new_tiles[y][x].color
          new_tiles[y][x].color = color_to_swap

          # da magic
          result = recursive_sort(queue, new_tiles)
          if result != False:
            return result
          break
      
      if found_match:
        break

    if found_match == False:
      print(f"    No match found for ({x}, {y})")
      return False
  
  print("Failed")
  return tiles

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
    self.matches = []
    self.possible_colors = []
    self.color_index = 0
    self.distance_from_lock = -1
  
  def determine_locked (self, img):
    stat = ImageStat.Stat(img)
    self.locked = sum(stat.stddev) > Tile.lock_stddev_threshold
    if self.locked:
      self.distance_from_lock = 0
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