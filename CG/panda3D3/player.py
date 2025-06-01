import os.path

import ursina
from ursina.prefabs.first_person_controller import FirstPersonController

class Player(FirstPersonController):
    def __init__(self, position: ursina.Vec3):
        super().__init__(
            position=position,
            model="cube",
            jump_height=2.5,
            jump_duration=0.4,
            origin_y=-2,
            collider="box",
            speed=7
        )
        # 得分和存活时间属性
        self.score = 0
        self.survival_time = 0.0  # 以秒为单位
        self.start_time = ursina.time.time()  # 记录游戏开始时间
        self.last_score_time = ursina.time.time()  # 记录上次加分时间

        #self.cursor.color = ursina.color.rgb(255, 0, 0, 122)
        self.cursor.color = ursina.color.rgb(255, 0, 0)
        self.gun = ursina.Entity(
            parent=ursina.camera.ui,
            position=ursina.Vec2(0.6, -0.45),
            scale=ursina.Vec3(0.01, 0.02, 0.065),
            rotation=ursina.Vec3(0, 10,0 ),
            model=os.path.join("models","AK-47.glb"),
            texture="white_cube",
            color=ursina.color.color(0, 0, 0.4)
        )

        self.healthbar_pos = ursina.Vec2(0, 0.45)
        self.healthbar_size = ursina.Vec2(0.8, 0.04)
        self.healthbar_bg = ursina.Entity(
            parent=ursina.camera.ui,
            model="quad",
            color=ursina.color.rgb(255, 0, 0),
            position=self.healthbar_pos,
            scale=self.healthbar_size
        )
        self.healthbar = ursina.Entity(
            parent=ursina.camera.ui,
            model="quad",
            color=ursina.color.rgb(0, 255, 0),
            position=self.healthbar_pos,
            scale=self.healthbar_size
        )

        self.health = 100
        self.death_message_shown = False

    def death(self):
        self.death_message_shown = True
        ursina.destroy(self.gun)
        self.rotation = 0
        self.camera_pivot.world_rotation_x = -45
        self.world_position = ursina.Vec3(0, 7, -35)
        self.cursor.color = ursina.color.rgb(0, 0, 0)
        ursina.Text(
            text="You are dead!",
            origin=ursina.Vec2(0, 0),
            scale=3
        )

    def update(self):
        self.healthbar.scale_x = self.health / 100 * self.healthbar_size.x
        if self.health <= 0:
            if not self.death_message_shown:
                self.death()
        else:
            # 更新存活时间
            current_time = ursina.time.time()
            self.survival_time = current_time - self.start_time

            # 每秒增加1分（只在整数秒变化时增加）
            if int(current_time) > int(self.last_score_time):
                self.score += 1
                self.last_score_time = current_time
            super().update()