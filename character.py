import pygame
import get_image
import get_audio
import framework as fw
from variable import Variable

class Player(pygame.sprite.Sprite):
    class Magic_object(pygame.sprite.Sprite):
        def __init__(self, 
                     screen: fw.Screen, 
                     x_axis: int, 
                     y_axis: int, 
                     direction: str, 
                     distance_speed: int):
            super().__init__()
            # รับข้อมูลการตั้งค่าของหน้าจอในปัจจุบัน
            self.__screen: fw.Screen = screen
            self.image = pygame.Surface([self.__screen.width(10), self.__screen.height(10)])
            self.image.fill((0, 0, 255))
            self.rect = self.image.get_rect(center=(x_axis, y_axis))
            # ทิศทางการยิงของเวทย์
            self.direction = direction
            self.speed = distance_speed

        def update(self):
            if self.direction == 'L':
                self.rect.x -= self.speed
            if self.direction == 'R':
                self.rect.x += self.speed
            self.speed += 1

            if self.rect.x < 0 or self.rect.x > self.__screen.SCREEN_WIDTH:
                self.kill()

    def __init__(self, 
                 screen: fw.Screen, 
                 player_width: int, 
                 player_height: int):
        super().__init__()
        # รับข้อมูลการตั้งค่าของหน้าจอในปัจจุบัน
        self.__screen: fw.Screen = screen
        # ความเร็วในการเคลื่อนที่ทั้งหมด
        self.__distance_speed = self.calculate_distance_speed()
        # ชื่อของตัวละคร เช่น เดล
        self.name = "test"
        # กำหนดความกว้างของตัวละคร
        self.__player_width = player_width
        # กำหนดความสูงของตัวละคร
        self.__player_height = player_height
        # การกระทำจะมี idle, walk, action
        # self.action = 'idle'
        self.action = 'walk'
        # key frame ปัจจุบันของตัวละคร
        self.key_frame = 1
        self.image = pygame.image.load(get_image.chibi_debirun_normal(self.action, self.key_frame))
        self.image = pygame.transform.scale(self.image, (self.__screen.width(self.__player_width), self.__screen.height(self.__player_height)))
        self.rect = self.image.get_rect()
        # ใช้เพื่อ cooldown เวลาในการเปลี่ยนของแต่ละ frame
        self.__cooldown_frame = fw.TimeGame()
        # ค่าการเคลื่อนที่ของตัวละคร
        self.speed = 0
        # ทิศทางที่ผู้เล่นหันอยู่ในแกน x ปัจจุบัน
        self.direction_x = 'L'
        # ทิศทางที่ผู้เล่นหันอยู่ในแกน y ปัจจุบัน
        self.direction_y = 'U'
        # ค่าเก็บข้อมูล sprite ของเวทย์
        self.magic_sprites = pygame.sprite.Group()

    def calculate_distance_speed(self):
        distance_speed = 1
        while True:
            distance_speed += 1
            if (self.__screen.width(1)//distance_speed) <= 8:
                break

        return distance_speed

    def update(self, var: Variable, events):
        # ดึงค่า keyboard ที่กดอยู่ในปัจจุบัน
        keys = pygame.key.get_pressed()
        # ตรวจสอบการกดปุ่ม
        self.pressing_button(var, keys, events)
        # ความคุมการเคลื่อนที่
        self.movement()
        # ป้องกันการเดินทะลุ map
        self.check_map_collision()
        # การแสดงผลรูปภาพของตัวละคร
        self.picture_display()
        # ตัวจับเวลา
        self.__cooldown_frame.update_time()
        
    def pressing_button(self, var: Variable, keys, events):
        # ปุ่มที่กดค้างได้
        # การควมคุมของผู้เล่น
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # ซ้าย
            self.speed = -self.__distance_speed
            self.direction_x = 'L'
            self.direction_y = None
            self.set_action('walk')
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # ขวา
            self.speed = self.__distance_speed
            self.direction_x = 'R'
            self.direction_y = None
            self.set_action('walk')
        elif keys[pygame.K_UP] or keys[pygame.K_w]:  # บน
            self.speed = -self.__distance_speed
            self.direction_x = None
            self.direction_y = 'U'
            self.set_action('walk')
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:  # ล่าง
            self.speed = self.__distance_speed
            self.direction_x = None
            self.direction_y = 'D'
            self.set_action('walk')
        # ปุ่มที่กดครั้งเดียว
        # ยิงเวทย์ 
        if keys[pygame.K_SPACE]:
            self.set_action('action')
            self.use_magic(var)
        # for event in events:
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_SPACE:
        #             # ยิงเวทย์ 
        #             self.set_action('action')
        #             self.use_magic(var)

    def movement(self):
        # ผู้เล่นจะเคลื่อนที่ในแนวแกน x ตามค่าความเร็ว
        if self.direction_x == 'L' or self.direction_x == 'R':
            self.rect.x += self.speed
        # ผู้เล่นจะเคลื่อนที่ในแนวแกน y ตามค่าความเร็ว
        if self.direction_y == 'U' or self.direction_y == 'D':
            self.rect.y += self.speed
        # ความเร็วของผู้เล่นจะลดลงค่า 1 ทุก ๆ ครั้ง
        self.speed += int(sign(self.speed) * -1)

    def use_magic(self, var: Variable):
        if self.direction_x == 'L':
            rect = self.rect.left
        if self.direction_x == 'R':
            rect = self.rect.right
        magic = self.Magic_object(self.__screen , rect, self.rect.centery, self.direction_x, self.__distance_speed)
        self.magic_sprites.add(magic)
        var.all_sprites.add(magic)

    def check_map_collision(self):
        # ป้องกันผู้เล่นทะลุจอ ด้านขวา ด้านซ้าย ด้านบน ด้านล่าง
        self.rect.right = min(self.rect.right, self.__screen.SCREEN_WIDTH)
        self.rect.left = max(self.rect.left, 0)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.__screen.SCREEN_HEIGHT)

    def set_action(self, action_name):
        # การกระทำจะมี idle, walk, action
        if action_name == 'idle' and self.action != 'idle':
            self.key_frame = 0
            self.action = 'idle'
        elif action_name == 'walk' and self.action != 'walk':
            self.key_frame = 0
            self.action = 'walk'
        # elif action_name == 'action':
        #     self.key_frame = 0
        #     self.action = 'action'
    
    def picture_display(self):
        # เนื่องจาก 1 วินาทีมี 1000 มิลลิวินาที จึงใส่ค่า 250 เพื่อให้ได้เท่ากับ 4 frame ต่อ 1 วินาที
        if self.__cooldown_frame.check_elapsed_time(250, is_Second=False):
            # ให้เริ่มจับเวลาใหม่
            self.__cooldown_frame.reset_time()
            # เปลี่ยน key frame
            self.key_frame += 1

        # ป้องกันค่า key frame ต่ำกว่า 1
        self.key_frame = max(self.key_frame, 1)
        
        # เก็บค่าตำแหน่ง x y เดิมไว้
        centerx = self.rect.centerx
        centery = self.rect.centery
        try:
            self.image = pygame.image.load(get_image.chibi_debirun_normal(self.action, self.key_frame))
            self.image = pygame.transform.scale(self.image, (self.__screen.width(self.__player_width), self.__screen.height(self.__player_height)))
            if self.direction_x == "L":
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(center=(centerx, centery))
        except:
            self.key_frame = 0
            self.picture_display()

# # เอลฟ์สาว
# class Narelle(Player):
#     def __init__(self, screen, maps, player_width=1, player_height=2.5):
#         super().__init__(screen, maps, player_width, player_height)

#     def update(self, var, events):
#         return super().update(var, events)
    
#     def picture_display(self):
#         return super().picture_display()
    
def sign(x):
    """
    ฟังก์ชันนี้จะรับตัวเลข (x) และคืนค่าเครื่องหมายของตัวเลขนั้น

    Args:
        x: ตัวเลขที่ต้องการหาเครื่องหมาย

    Returns:
        1 ถ้า x เป็นบวก
        0 ถ้า x เป็นศูนย์
        -1 ถ้า x เป็นลบ
    """

    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
