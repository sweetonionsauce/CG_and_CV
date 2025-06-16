from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()
controller = FirstPersonController()
controller.ignore_pause = True

def update ():
    if held_keys['escape']:
        application.paused = not application.paused

app.run()