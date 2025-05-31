import os
import ursina
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
from floor import Floor
from map import Map
from player import Player
from enemy import Enemy
from bullet import Bullet
import random
from minimap import Minimap

app = ursina.Ursina()
ursina.window.borderless = False
ursina.window.title = "Ursina FPS"
ursina.window.exit_button.visible = False

#敌人刷新
def spawn_enemy():
    # 在玩家周围20单位范围内随机生成
    x = random.uniform(-15, 15)
    z = random.uniform(-15, 15)
    enemy_id = str(len(enemies) + 1)
    username = f"Bot{enemy_id}"
    # ...
    new_enemy = Enemy(ursina.Vec3(x, 1, z), enemy_id, username, player)
    new_enemy.game_map = game_map  # 添加地图引用
    enemies.append(new_enemy)
    # 每40秒调用一次
    ursina.invoke(spawn_enemy, delay=40)


# 初始化场景
floor = Floor()
game_map = Map()
sky = ursina.Entity(
    model="sphere",
    texture=os.path.join("textures", "sky.png"),
    scale=9999,
    double_sided=True
)
# 创建敌人
enemies = []
# 创建玩家
player = Player(ursina.Vec3(0, 1, 0))
#初始化小地图
minimap = Minimap(game_map, player, lambda: enemies)# 传入获取敌人列表的回调
#刷新敌人
spawn_enemy()



def input(key):
    if key == "left mouse down" and player.health > 0:
        b_pos = player.position + ursina.Vec3(0, 2, 0)
        bullet = Bullet(b_pos, player.world_rotation_y, -player.camera_pivot.world_rotation_x)
        #后座：
        player.camera_pivot.rotation_x += random.uniform(-1, 1)
        player.rotation_y += random.uniform(-1, 1)

        ursina.destroy(bullet, delay=2)

    if key == "escape":
            application.quit()
def update():
    # 清理已销毁的敌人
    global enemies
    enemies = [e for e in enemies if e.enabled]
    # 敌人自动转向玩家
    for enemy in enemies:
        if enemy.health > 0:
            direction = (player.position - enemy.position).normalized()
            enemy.rotation_y = ursina.math.degrees(ursina.math.atan2(-direction.x, -direction.z))
    # 更新小地图位置
    #minimap.update_positions()
    # 更新小地图位置，传入当前的敌人列表
    minimap.update_positions()
app.run()