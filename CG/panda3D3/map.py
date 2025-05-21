import os
import ursina


class Wall(ursina.Entity):
    def __init__(self, position, parent=None):  # 添加parent参数
        super().__init__(
            parent=parent,  # 传递parent参数给父类
            position=position,
            scale=2,
            model="cube",
            texture=os.path.join("textures", "wall.png"),
            origin_y=-0.5
        )
        self.texture.filtering = None
        self.collider = ursina.BoxCollider(self, size=ursina.Vec3(1, 2, 1))


class Map(ursina.Entity):
    def __init__(self):
        super().__init__()  #parent=ursina.scene,enabled=True# 初始化父类，显式指定父级为场景
        # 设置父级和激活状态
        self.parent = ursina.scene  # 确保附加到主场景
        self.enabled = True

        # 迷宫矩阵（7x7格局，1表示墙体）
        maze_layout1 = [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1]
        ]

        # 14x14迷宫矩阵（1为墙体，0为通道）
        maze_layout = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1]
        ]

        # 根据矩阵生成3D墙体
        for row in range(len(maze_layout)):
            for col in range(len(maze_layout[0])):
                if maze_layout[row][col] == 1:
                    # 将矩阵坐标转换为3D世界坐标（居中布局）
                    x = (col - 3) * 2  # 列转x轴，偏移量-3使迷宫居中
                    z = (row - 3) * 2  # 行转z轴
                    Wall(ursina.Vec3(x, 1, z), parent=self)
        '''
        for y in range(1, 4, 2):
            Wall(ursina.Vec3(6, y, 0), parent=self)  # 添加parent参数
            Wall(ursina.Vec3(6, y, 2), parent=self)
            Wall(ursina.Vec3(6, y, 4), parent=self)
            Wall(ursina.Vec3(6, y, 6), parent=self)
            Wall(ursina.Vec3(6, y, 8), parent=self)

            Wall(ursina.Vec3(4, y, 8), parent=self)
            Wall(ursina.Vec3(2, y, 8), parent=self)
            Wall(ursina.Vec3(0, y, 8), parent=self)
            Wall(ursina.Vec3(-2, y, 8), parent=self)
        '''
        #导航网格系统
        self.grid_size = 2  # 对应地板块尺寸
        self.grid = {}
        self.obstacles = []

        # 根据实际墙体位置生成网格
        min_range = -14 #-6  # 7x7迷宫的最小坐标（-3 * 2）
        max_range = 14 #6  # 7x7迷宫的最大坐标（3 * 2）
        for x in range(min_range, max_range + 1, self.grid_size):
            for z in range(min_range, max_range + 1, self.grid_size):
                self.grid[(x, z)] = True  # 默认可通行

        # 标记障碍物
        for wall in self.children:
            grid_x = round(wall.position.x / self.grid_size) * self.grid_size
            grid_z = round(wall.position.z / self.grid_size) * self.grid_size
            self.grid[(grid_x, grid_z)] = False
            self.obstacles.append((grid_x, grid_z))

        '''
        # 初始化可通行区域
        for x in range(-20, 20, self.grid_size):
            for z in range(-20, 20, self.grid_size):
                self.grid[(x, z)] = True
        
        # 标记墙体为不可通行
        for wall in self.children:
            x = round(wall.position.x / self.grid_size) * self.grid_size
            z = round(wall.position.z / self.grid_size) * self.grid_size
            self.grid[(x, z)] = False
            self.obstacles.append((x, z))
        '''


    def get_neighbors(self, node):
        """获取可通行的相邻网格"""
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        neighbors = []
        for dx, dz in directions:
            check_node = (node[0] + dx, node[1] + dz)
            if self.grid.get(check_node, False):
                neighbors.append(check_node)
        return neighbors

    def get_grid_info(self):
        """返回地图网格信息，用于小地图"""
        return {
            'grid': self.grid,
            'obstacles': self.obstacles
        }