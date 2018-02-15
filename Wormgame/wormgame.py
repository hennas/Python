"""A very simple worm game, controlled with arrow keys. Graphics made with PSE."""

import pyglet
from pyglet.gl import *
import random

window = pyglet.window.Window(600, 600)
body = pyglet.resource.image('body.png')
apple = pyglet.sprite.Sprite(pyglet.resource.image('apple.png'))
head = pyglet.sprite.Sprite(pyglet.resource.image('head.png'))
background = pyglet.sprite.Sprite(pyglet.resource.image('background.png'))
sprites = []
batch = pyglet.graphics.Batch()

@window.event
def on_draw():
    """Draws the game to the player, content is determined by the state of the game"""
    window.clear()
    background.draw()
    if gameon:
        apple.draw()
        x, y = bodylocation[-1]
        head.position = x * 40, y * 40
        head.rotation = direction
        if direction in [90, 180]:
            head.y += 40
        if direction in [180, 270]:
            head.x +=40
        head.draw()
        for i in range(len(bodylocation) - 1):
            x, y = bodylocation[i]
            sprites.append(pyglet.sprite.Sprite(body, x * 40, y * 40, batch=batch))
            sprites[i].rotation = direction
            if direction in [90, 180]:
                sprites[i].y += 40
            if direction in [180, 270]:
                sprites[i].x +=40
        batch.draw()
        sprites.clear()
    else:
        pyglet.text.Label('Game Over!', 
                            font_name='Times New Roman', font_size=45, 
                            color=(255, 255, 255, 255), 
                            x=300, y=300, 
                            anchor_x='center', anchor_y='center').draw()  
        pyglet.text.Label('Press Enter to start again', 
                            font_name='Times New Roman', font_size=15, 
                            color=(255, 255, 255, 255), 
                            x=300, y=250, 
                            anchor_x='center', anchor_y='center').draw()                              
    pyglet.text.Label('Score: %s'%(score),
                          font_name='Times New Roman', font_size=12, 
                          color=(255, 255, 255, 255),
                          x=8, y=5,
                          anchor_x='left', anchor_y='bottom').draw()
@window.event
def on_key_press(symbol, modifiers):
    """Handles the key presses"""
    global direction, bodylocation, gameon, score
    if symbol == pyglet.window.key.LEFT and direction != 0:
        direction = 180
    elif symbol == pyglet.window.key.RIGHT and direction != 180:
        direction = 0
    elif symbol == pyglet.window.key.UP and direction != 90:
        direction = 270
    elif symbol == pyglet.window.key.DOWN and direction != 270:
        direction = 90
    if not gameon and symbol == pyglet.window.key.ENTER:
        init_game()
    
def update(dt):
    """
    If the worm hits itself or goes outside the bounds, the game ends and the function returns.
    If the worm eats the apple, a new apple is placed and the score is increased by 10, otherwise the 'tail' of the worm is removed. 
    At the end of the function, a new part is added to the worm's body.
    """
    global gameon, score
    x, y = bodylocation[-1]
    a, b = apple.x // 40, apple.y // 40
    if outside_field(x, y) or are_there_hits(x, y, 0, len(bodylocation) - 1):
        gameon = False
        pyglet.clock.unschedule(update)
        return
    elif x == a and y == b:
        place_apple()
        score += 10
    else:
        del bodylocation[0]
    x, y = new_coordinates(x, y)
    bodylocation.append((x, y))
    
def place_apple():
    """Places the apple to a random location"""
    while True:
        a, b = random.randint(0, 14), random.randint(0, 14)
        if not are_there_hits(a, b, 0, len(bodylocation)):
            apple.position = a * 40, b * 40
            return
        
def outside_field(x,y):
    """Checks if the coordinates given as parameters are out of predetermined bounds"""
    if x < 0 or y < 0 or x > 14 or y > 14:
        return True
    return False
    
def are_there_hits(x, y, start, stop):
    """Checks if the worm has hit itself"""
    for i in range(start, stop):
        x2, y2 = bodylocation[i]
        if x == x2 and y == y2:
            return True         
    return False

def new_coordinates(x, y):
    """Calculates the next coordinates and returns them."""
    if direction == 0:
        x += 1
    elif direction == 180:
        x -= 1
    elif direction == 270:
        y += 1
    else:
        y -= 1
    return x, y
    
def init_game():
    """
    Sets the default values, places the apple and starts updating the game. 
    Called at the beginning of the game and every time player wants to start a new game right after the previous one.
    """
    global direction, bodylocation, gameon, score
    bodylocation = [(2, 8), (3, 8), (4, 8)]
    direction = 0
    score = 0
    gameon = True 
    
    place_apple()    
    pyglet.clock.schedule_interval(update, 0.1)

init_game()
pyglet.app.run()
