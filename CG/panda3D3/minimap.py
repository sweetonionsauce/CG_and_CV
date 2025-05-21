import ursina


class Minimap(ursina.Entity):
    def __init__(self, game_map, player, enemies):
        super().__init__(parent=ursina.camera.ui)
        self.scale = (0.2, 0.2)  # 小地图大小
        self.position = (0.4, 0.4)  # 右上角位置
        self.game_map = game_map
        self.player = player
        self.enemies = enemies

        # 创建小地图背景
        self.background = ursina.Entity(
            parent=self,
            model='quad',
            scale=(1, 1),
            color=ursina.color.color(0, 0, 0.3),
            position=(0, 0)
        )

        # 存储小地图格子
        self.tiles = []

        # 创建玩家位置标记
        self.player_marker = ursina.Entity(
            parent=self,
            model='quad',
            scale=(0.05, 0.05),
            color=ursina.color.red,
            position=(0, 0)
        )

        # 创建敌人位置标记列表
        self.enemy_markers = []

        # 初始化小地图格子
        self.create_map()

    def create_map(self):
        """根据游戏地图创建小地图"""
        # 获取地图范围
        min_x = min(self.game_map.grid.keys(), key=lambda p: p[0])[0]
        max_x = max(self.game_map.grid.keys(), key=lambda p: p[0])[0]
        min_z = min(self.game_map.grid.keys(), key=lambda p: p[1])[1]
        max_z = max(self.game_map.grid.keys(), key=lambda p: p[1])[1]

        # 计算小地图格子大小
        tile_size = 0.05  # 每个格子的大小

        # 创建小地图格子
        for x in range(min_x, max_x + 1, 2):  # 步长为2，与地图网格一致
            for z in range(min_z, max_z + 1, 2):
                # 计算在小地图中的位置 (归一化到 -0.5 到 0.5 范围)
                pos_x = (x - min_x) / (max_x - min_x) - 0.5
                pos_z = (z - min_z) / (max_z - min_z) - 0.5

                # 创建格子
                tile = ursina.Entity(
                    parent=self,
                    model='quad',
                    scale=(tile_size, tile_size),
                    position=(pos_x, pos_z),
                    color=ursina.color.gray  # 默认为地面
                )

                # 如果是墙，设置为黑色
                if (x, z) in self.game_map.obstacles:
                    tile.color = ursina.color.black

                self.tiles.append(tile)

    def update_positions(self):
        """更新玩家和敌人的位置"""
        # 获取地图范围
        min_x = min(self.game_map.grid.keys(), key=lambda p: p[0])[0]
        max_x = max(self.game_map.grid.keys(), key=lambda p: p[0])[0]
        min_z = min(self.game_map.grid.keys(), key=lambda p: p[1])[1]
        max_z = max(self.game_map.grid.keys(), key=lambda p: p[1])[1]

        # 更新玩家位置
        player_x = self.player.position.x
        player_z = self.player.position.z
        pos_x = (player_x - min_x) / (max_x - min_x) - 0.5
        pos_z = (player_z - min_z) / (max_z - min_z) - 0.5
        self.player_marker.position = (pos_x, pos_z)

        # 更新敌人位置
        # 先清除旧的敌人标记
        for marker in self.enemy_markers:
            ursina.destroy(marker)
        self.enemy_markers = []
        '''
        for enemy in self.enemies:
            enemy_x = enemy.position.x
            enemy_z = enemy.position.z
            pos_x = (enemy_x - min_x) / (max_x - min_x) - 0.5
            pos_z = (enemy_z - min_z) / (max_z - min_z) - 0.5
            marker = ursina.Entity(
                parent=self,
                model='quad',
                scale=(0.03, 0.03),
                color=ursina.color.blue,
                position=(pos_x, pos_z)
            )
            self.enemy_markers.append(marker)
            
        '''
        # 只处理有效的敌人
        for enemy in self.enemies:
            # 检查敌人是否仍然有效（未被销毁）
            if enemy.enabled:
                enemy_x = enemy.position.x
                enemy_z = enemy.position.z
                pos_x = (enemy_x - min_x) / (max_x - min_x) - 0.5
                pos_z = (enemy_z - min_z) / (max_z - min_z) - 0.5
                marker = ursina.Entity(
                    parent=self,
                    model='quad',
                    scale=(0.03, 0.03),
                    color=ursina.color.blue,
                    position=(pos_x, pos_z)
                )
                self.enemy_markers.append(marker)
    def refresh_map(self):
        """刷新小地图显示"""
        # 清除现有格子
        for tile in self.tiles:
            ursina.destroy(tile)
        self.tiles = []

        # 重新创建地图
        self.create_map()