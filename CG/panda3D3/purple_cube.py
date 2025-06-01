import ursina
import random
# 紫色方块类
class PurpleCube(ursina.Entity):        #purple方块是金色的也很合理吧
    def __init__(self, game_map):
        super().__init__(
            model="cube",
            color=ursina.color.gold,
            scale=1.5,
            collider="box"
        )
        self.game_map = game_map
        self.spawn_new_location()

    def spawn_new_location(self):
        """在随机位置生成紫色方块（避开墙体）"""
        # 获取所有可通行位置
        walkable_positions = [pos for pos, walkable in self.game_map.grid.items() if walkable]

        if walkable_positions:
            # 随机选择一个位置
            x, z = random.choice(walkable_positions)
            self.position = ursina.Vec3(x, 1, z)
            self.enabled = True
            return True
        return False

    def check_player_collision(self, player):
        """检查玩家是否靠近"""
        if self.enabled and ursina.distance(self.position,player.position) < 2.5:
            self.enabled = False
            return True
        return False