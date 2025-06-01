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
from purple_cube import PurpleCube

game_over = False
death_display = None

app = ursina.Ursina()
ursina.window.borderless = False
ursina.window.title = "Ursina FPS"
ursina.window.exit_button.visible = False

# 得分显示文本
score_text = ursina.Text(
    text="Score: 0 | Time: 0:00",
    position=(-0.8, 0.4),  # 左上角位置
    scale=1.5
)

# 在敌人死亡时增加得分
def enemy_death_callback(enemy):
    global enemies_killed
    enemies_killed += 1
    player.score += 100  # 杀死敌人得100分

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
    new_enemy.set_death_callback(enemy_death_callback)  # 设置死亡回调
    enemies.append(new_enemy)
    # 每40秒调用一次
    ursina.invoke(spawn_enemy, delay=40)
'''
# 紫色方块刷新
def spawn_purple_cube(purple_cube):
    if purple_cube.spawn_new_location():
        # 成功生成后设置下一次刷新
        ursina.invoke(spawn_purple_cube, delay=20)
    else:
        # 如果生成失败，稍后重试
        ursina.invoke(spawn_purple_cube, delay=5)

'''
# 紫色方块刷新
def spawn_purple_cube(cube):
    if cube.spawn_new_location():
        # 成功生成后设置下一次刷新
        ursina.invoke(lambda: spawn_purple_cube(cube), delay=20)
    else:
        # 如果生成失败，稍后重试
        ursina.invoke(lambda: spawn_purple_cube(cube), delay=5)




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
# 创建紫色方块
purple_cube = PurpleCube(game_map)
#初始化小地图
#minimap = Minimap(game_map, player, lambda: enemies)# 传入获取敌人列表的回调
minimap = Minimap(game_map, player, lambda: enemies, purple_cube)  # 传入紫色方块
#刷新敌人
spawn_enemy()
# 刷新紫色方块
spawn_purple_cube(purple_cube)  # 传递参数


def show_death_screen():
    """显示死亡界面"""
    global death_display

    # 计算存活时间（分钟和秒）
    minutes = int(player.survival_time) // 60
    seconds = int(player.survival_time) % 60

    # 计算存活时间得分（每秒1分）
    survival_score = seconds

    # 总得分
    total_score = player.score + survival_score

    # 创建死亡界面
    death_text = f"""
    You are dead!

    Total Score: {total_score}
    Survival Time: {minutes}:{seconds:02d}
    Enemies Killed: {enemies_killed}
    Purple Cubes Collected: {purple_cubes_collected}
    
    
    
    
    
    

    """

    death_display = ursina.Text(
        text=death_text,
        origin=(0, 0),
        position=(0, 0.1),
        scale=2
    )

    # 添加重新开始按钮
    restart_button = ursina.Button(
        text="Restart",
        scale=(0.2, 0.1),
        position=(0, -0.2),
        on_click=restart_game
    )


def restart_game():
    """重新开始游戏"""
    global game_over, death_display, enemies, player, purple_cube, score_text,minimap
    global enemies_killed, purple_cubes_collected

    # 重置游戏状态
    game_over = False
    enemies_killed = 0
    purple_cubes_collected = 0

    # 销毁死亡界面
    if death_display:
        ursina.destroy(death_display)
        death_display = None

    # 销毁所有敌人
    for enemy in enemies:
        ursina.destroy(enemy)
    enemies = []

    # 重置玩家
    ursina.destroy(player)
    player = Player(ursina.Vec3(0, 1, 0))

    # 重置紫色方块
    ursina.destroy(purple_cube)
    purple_cube = PurpleCube(game_map)

    # 重置小地图
    ursina.destroy(minimap)
    minimap = Minimap(game_map, player, lambda: enemies, purple_cube)

    # 刷新敌人和紫色方块
    spawn_enemy()
    spawn_purple_cube(purple_cube)

    # 显示得分文本
    score_text.enabled = True


# 添加全局计数器
enemies_killed = 0
purple_cubes_collected = 0


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
    global enemies, enemies_killed, purple_cubes_collected, game_over
    enemies = [e for e in enemies if e.enabled]

    # 更新得分显示
    if not game_over:
        minutes = int(player.survival_time) // 60
        seconds = int(player.survival_time) % 60
        score_text.text = f"Score: {player.score} | Time: {minutes}:{seconds:02d}"

    # 敌人自动转向玩家
    for enemy in enemies:
        if enemy.health > 0:
            direction = (player.position - enemy.position).normalized()
            enemy.rotation_y = ursina.math.degrees(ursina.math.atan2(-direction.x, -direction.z))
    # 检查玩家是否靠近紫色方块
    if purple_cube.check_player_collision(player):
        # 玩家获得紫色方块后的效果（可自定义）
        player.health = min(100, player.health + 20)  # 恢复20点生命值
        player.score += 1000  # 收集紫色方块得1000分
        purple_cubes_collected += 1
    # 更新小地图位置
    #minimap.update_positions()
    # 更新小地图位置，传入当前的敌人列表
    minimap.update_positions()

    # 检查游戏结束
    if player.health <= 0 and not game_over:
        game_over = True
        show_death_screen()
        # 隐藏实时得分显示
        score_text.enabled = False


app.run()