import os.path
import queue
import ursina
# 添加优先队列实现
import heapq


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return not self.elements

    def put(self, item):
        heapq.heappush(self.elements, item)

    def get(self):
        return heapq.heappop(self.elements)

class Enemy(ursina.Entity):
    def __init__(self, position: ursina.Vec3, identifier: str, username: str, player):  # 添加player参数
        super().__init__(
            position=position,
            model=os.path.join("models", "just_a_girl.glb"),
            origin_y=-0.5,
            collider="box",
            texture="white_cube",
            color=ursina.color.color(0, 0, 1),
            scale=ursina.Vec3(0.02, 0.02, 0.02),

        )
        self.name_tag = ursina.Text(
            parent=self,
            text=username,
            position=ursina.Vec3(0, 1.3, 0),
            scale=ursina.Vec2(5, 3),
            billboard=True,
            origin=ursina.Vec2(0, 0)
        )

        self.health = 100
        self.id = identifier
        self.username = username
        self.player = player  # 保存玩家引用
        self.speed = 3  # 移动速度
        self.attack_damage = 30  # 攻击伤害
        self.attack_interval = 1.0  # 攻击间隔（秒）
        self.attack_timer = 0.0  # 攻击计时器

        # 寻路属性
        self.path = []
        self.current_target_index = 0
        self.repath_interval = 1.0  # 重新计算路径间隔
        self.last_repath_time = 0.0

    def a_star_search(self, start, goal, map_grid):
        """A*路径搜索算法"""
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()[1]

            if current == goal:
                break

            for next_node in map_grid.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self.heuristic(goal, next_node)
                    frontier.put((priority, next_node))
                    came_from[next_node] = current

        return self.reconstruct_path(came_from, start, goal)

    def heuristic(self, a, b):
        """曼哈顿距离启发式函数"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, start, goal):
        """重建路径"""
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from.get(current, start)
        path.reverse()
        return path

    def update_path(self):
        """更新移动路径"""
        if self.player is None:
            return

        # 将3D坐标转换为网格坐标
        start_x = round(self.position.x / 2) * 2
        start_z = round(self.position.z / 2) * 2
        goal_x = round(self.player.position.x / 2) * 2
        goal_z = round(self.player.position.z / 2) * 2

        # 如果目标点在障碍物中，寻找最近可通行点
        if (goal_x, goal_z) in self.game_map.obstacles:
            closest = None
            min_dist = float('inf')
            for dx, dz in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                check = (goal_x + dx, goal_z + dz)
                if self.game_map.grid.get(check, False):
                    dist = self.heuristic((start_x, start_z), check)
                    if dist < min_dist:
                        closest = check
                        min_dist = dist
            if closest:
                goal_x, goal_z = closest

        self.path = self.a_star_search((start_x, start_z), (goal_x, goal_z), self.game_map)
        self.current_target_index = 0

    def update(self):
        try:
            color_saturation = 1 - self.health / 100
        except AttributeError:
            self.health = 100
            color_saturation = 1 - self.health / 100

        self.color = ursina.color.color(0, color_saturation, 1)

        if self.health <= 0:
            self.enabled=False
            ursina.destroy(self)
        else:
            # 计算移动方向并移动
            direction = (self.player.position - self.position).normalized()
            self.position += direction * self.speed * ursina.time.dt

            # 攻击检测
            distance = (self.position - self.player.position).length()
            if distance < 1.5:  # 攻击范围
                self.attack_timer += ursina.time.dt
                if self.attack_timer >= self.attack_interval:
                    self.player.health -= self.attack_damage
                    self.attack_timer = 0
            else:
                self.attack_timer = 0  # 超出范围重置计时器
        # 路径跟随逻辑
        if self.health > 0 and self.player.health > 0:
            # 定期重新计算路径
            if ursina.time.time() - self.last_repath_time > self.repath_interval:
                self.update_path()
                self.last_repath_time = ursina.time.time()

            # 跟随路径移动
            if self.path:
                target_pos = ursina.Vec3(
                    self.path[self.current_target_index][0],
                    self.position.y,
                    self.path[self.current_target_index][1]
                )

                direction = (target_pos - self.position).normalized()
                self.position += direction * self.speed * ursina.time.dt

                # 检查是否到达当前路径点
                if (self.position - target_pos).length() < 0.5:
                    self.current_target_index += 1
                    if self.current_target_index >= len(self.path):
                        self.path = []