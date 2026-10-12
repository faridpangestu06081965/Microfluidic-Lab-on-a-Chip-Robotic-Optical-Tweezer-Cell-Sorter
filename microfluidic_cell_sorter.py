@'
import pygame
import math
import random
import sys
from collections import deque

pygame.init()
pygame.font.init()

# Setup Layar HD 1280x720
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Microfluidic Lab-on-a-Chip : High-Precision Laser Cell Sorter Suite")
clock = pygame.time.Clock()

# Fonts
FONT_TITLE = pygame.font.SysFont("Segoe UI", 16, bold=True)
FONT_SUB = pygame.font.SysFont("Segoe UI", 11, bold=True)
FONT_DATA = pygame.font.SysFont("Consolas", 12, bold=True)
FONT_KEY = pygame.font.SysFont("Consolas", 10, bold=True)

# Palette Warna High-Tech Cyber-Lab
COLOR_BG = (8, 12, 18)
COLOR_PANEL_BG = (15, 21, 32, 225)
COLOR_PANEL_BORDER = (0, 180, 230, 150)
COLOR_CHANNEL_BG = (12, 18, 28)
COLOR_CHANNEL_WALL = (0, 220, 255)

COLOR_NORMAL = (0, 220, 255)       # Sel Normal (Cyan Glow)
COLOR_TARGET = (255, 30, 110)      # Sel Kanker CTC (Neon Magenta)
COLOR_LASER = (0, 255, 140)        # Laser Optik (Emerald Green)

TYPE_NORMAL = 0
TYPE_TARGET = 1

class ParticleVFX:
    """Efek percikan foton saat laser mengunci sel"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-2.5, 2.5)
        self.radius = random.uniform(2.0, 4.0)
        self.life = 1.0
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 0.05

    def draw(self, surface):
        if self.life > 0:
            alpha = int(self.life * 255)
            s = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))

class FluidStreamline:
    """Visualisasi Hydrodynamics Laminer"""
    def __init__(self, y_min, y_max, max_x=910):
        self.x = random.uniform(0, max_x)
        self.y = random.uniform(y_min + 6, y_max - 6)
        self.length = random.uniform(15, 35)
        self.base_speed = random.uniform(2.2, 3.2)

    def update(self, y_min, y_max, max_x=910):
        center_y = (y_min + y_max) / 2.0
        half_h = (y_max - y_min) / 2.0
        factor = max(0.15, 1.0 - ((abs(self.y - center_y) / half_h) ** 2))
        self.x += self.base_speed * factor
        if self.x - self.length > max_x:
            self.x = 0
            self.y = random.uniform(y_min + 6, y_max - 6)

    def draw(self, surface):
        end_x = max(0, self.x - self.length)
        pygame.draw.line(surface, (0, 160, 220, 40), (self.x, self.y), (end_x, self.y), 1)

class Cell:
    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.type = cell_type
        self.radius = 12 if cell_type == TYPE_TARGET else 9
        self.vx = random.uniform(2.3, 2.8)
        self.vy = 0.0
        self.pulse = random.uniform(0, 6.28)

    def update(self, y_min, y_max, split_x):
        center_y = (y_min + y_max) / 2.0
        half_h = (y_max - y_min) / 2.0
        dist_factor = max(0.2, 1.0 - ((abs(self.y - center_y) / half_h) ** 2))
        
        self.x += self.vx * dist_factor
        self.y += self.vy
        self.vy *= 0.80  # Stokes Drag Resistance

        if self.x < split_x:
            self.y = max(y_min + self.radius + 4, min(y_max - self.radius - 4, self.y))
        else:
            if self.y < center_y:
                self.y = max(y_min + self.radius + 4, min(center_y - 15 - self.radius, self.y))
            else:
                self.y = max(center_y + 15 + self.radius, min(y_max - self.radius - 4, self.y))

        self.pulse += 0.08

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        if self.type == TYPE_TARGET:
            pulse_val = math.sin(self.pulse)
            glow_r = self.radius + 6 + int(3 * pulse_val)
            glow_surf = pygame.Surface((glow_r * 2 + 4, glow_r * 2 + 4), pygame.SRCALPHA)
            
            pygame.draw.circle(glow_surf, (255, 30, 110, 45), (glow_r + 2, glow_r + 2), glow_r)
            pygame.draw.circle(glow_surf, (255, 60, 130, 95), (glow_r + 2, glow_r + 2), self.radius + 3)
            surface.blit(glow_surf, (px - glow_r - 2, py - glow_r - 2))
            
            pygame.draw.circle(surface, COLOR_TARGET, (px, py), self.radius)
            pygame.draw.circle(surface, (255, 230, 245), (px, py), self.radius - 4)
            pygame.draw.circle(surface, (255, 255, 255), (px - 2, py - 2), 2)
        else:
            pygame.draw.circle(surface, (0, 150, 220, 60), (px, py), self.radius + 3)
            pygame.draw.circle(surface, COLOR_NORMAL, (px, py), self.radius)
            pygame.draw.circle(surface, (190, 245, 255), (px, py), self.radius - 3)
            pygame.draw.circle(surface, (255, 255, 255), (px - 2, py - 2), 2)

class GalvoLaserScanner:
    def __init__(self, target_x):
        self.x = target_x
        self.active = False
        self.target_cell = None
        self.current_force_pN = 0.0

    def update(self, cells, auto_mode, y_max, vfx_list):
        self.target_cell = None
        if not auto_mode:
            self.active = False
            self.current_force_pN = 0.0
            return

        candidates = [c for c in cells if c.type == TYPE_TARGET and 320 < c.x < 520]
        if candidates:
            candidates.sort(key=lambda c: c.x)
            self.target_cell = candidates[0]
            
            target_y = y_max - 45
            dy = target_y - self.target_cell.y
            self.target_cell.vy += dy * 0.16
            self.active = True
            self.current_force_pN = min(48.5, max(32.0, abs(dy) * 0.85))

            if random.random() < 0.6:
                vfx_list.append(ParticleVFX(self.target_cell.x, self.target_cell.y, COLOR_LASER))
        else:
            self.active = False
            self.current_force_pN = 0.0

    def draw(self, surface, y_min, y_max):
        head_x, head_y = 420, y_min - 28
        pygame.draw.rect(surface, (28, 38, 54), (head_x - 35, head_y, 70, 22), border_radius=5)
        pygame.draw.rect(surface, COLOR_LASER, (head_x - 35, head_y, 70, 22), width=1, border_radius=5)
        pygame.draw.circle(surface, COLOR_LASER, (head_x, head_y + 11), 3)

        if self.active and self.target_cell:
            tx, ty = int(self.target_cell.x), int(self.target_cell.y)
            
            beam_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(beam_surf, (0, 255, 140, 35), [(head_x, head_y + 22), (tx - 14, ty), (tx + 14, ty)])
            pygame.draw.line(beam_surf, COLOR_LASER, (head_x, head_y + 22), (tx, ty), 2)
            
            pygame.draw.circle(beam_surf, COLOR_LASER, (tx, ty), 18, width=2)
            pygame.draw.circle(beam_surf, (255, 255, 255), (tx, ty), 4)
            pygame.draw.line(beam_surf, COLOR_LASER, (tx - 22, ty), (tx + 22, ty), 1)
            pygame.draw.line(beam_surf, COLOR_LASER, (tx, ty - 22), (tx, ty + 22), 1)
            
            surface.blit(beam_surf, (0, 0))

class UIButton:
    def __init__(self, rect, text, color_accent):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color_accent
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def draw(self, surface):
        bg_col = (40, 55, 80) if self.is_hovered else (25, 34, 50)
        border_col = (255, 255, 255) if self.is_hovered else self.color
        
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=1, border_radius=6)
        
        txt_surf = FONT_SUB.render(self.text, True, (240, 245, 255))
        tx = self.rect.x + (self.rect.width - txt_surf.get_width()) // 2
        ty = self.rect.y + (self.rect.height - txt_surf.get_height()) // 2
        surface.blit(txt_surf, (tx, ty))

def draw_glass_panel(surface, rect, border_color=(0, 180, 220, 150), bg_color=(15, 21, 32, 225)):
    panel_surf = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, bg_color, (0, 0, rect[2], rect[3]), border_radius=8)
    pygame.draw.rect(panel_surf, border_color, (0, 0, rect[2], rect[3]), width=1, border_radius=8)
    surface.blit(panel_surf, (rect[0], rect[1]))

def draw_donut_chart(surface, center, outer_r, inner_r, val1, val2):
    total = max(1, val1 + val2)
    angle1 = (val1 / total) * 360
    
    cx, cy = center
    rect = (cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2)
    
    if total == 0:
        pygame.draw.circle(surface, (40, 50, 70), center, outer_r)
    else:
        pygame.draw.arc(surface, COLOR_NORMAL, rect, 0, math.radians(angle1), outer_r)
        pygame.draw.arc(surface, COLOR_TARGET, rect, math.radians(angle1), math.radians(360), outer_r)
    
    pygame.draw.circle(surface, COLOR_BG, center, inner_r)

def main():
    running = True
    auto_mode = True
    spawn_timer = 0
    inlet_flash = 0
    
    total_normal = 0
    total_target = 0
    sorted_waste = 0
    sorted_harvest = 0

    purity_history = deque(maxlen=90)

    ch_y_min, ch_y_max = 160, 500
    split_x = 610
    center_y = (ch_y_min + ch_y_max) / 2.0

    cells = []
    vfx_list = []
    streamlines = [FluidStreamline(ch_y_min, ch_y_max, max_x=910) for _ in range(70)]
    scanner = GalvoLaserScanner(420)

    btn_auto = UIButton((20, 660, 140, 36), "AUTO LASER [SPACE]", COLOR_LASER)
    btn_inject = UIButton((170, 660, 140, 36), "INJECT CTC [CLICK]", COLOR_TARGET)
    btn_reset = UIButton((320, 660, 110, 36), "RESET [C]", COLOR_NORMAL)

    while running:
        clock.tick(60)
        spawn_timer += 1
        if inlet_flash > 0:
            inlet_flash -= 1

        mouse_pos = pygame.mouse.get_pos()
        btn_auto.check_hover(mouse_pos)
        btn_inject.check_hover(mouse_pos)
        btn_reset.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    auto_mode = not auto_mode
                elif event.key == pygame.K_c:
                    cells.clear()
                    total_normal = total_target = sorted_waste = sorted_harvest = 0
                    purity_history.clear()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_auto.rect.collidepoint((mx, my)):
                    auto_mode = not auto_mode
                elif btn_inject.rect.collidepoint((mx, my)):
                    cells.append(Cell(30, random.uniform(ch_y_min + 20, ch_y_max - 20), TYPE_TARGET))
                    total_target += 1
                    inlet_flash = 12
                elif btn_reset.rect.collidepoint((mx, my)):
                    cells.clear()
                    total_normal = total_target = sorted_waste = sorted_harvest = 0
                    purity_history.clear()
                elif 12 <= mx <= 120 and ch_y_min < my < ch_y_max:
                    cells.append(Cell(mx, my, TYPE_TARGET))
                    total_target += 1
                    inlet_flash = 12

        if spawn_timer % 15 == 0:
            c_type = TYPE_TARGET if random.random() < 0.25 else TYPE_NORMAL
            cells.append(Cell(30, random.uniform(ch_y_min + 20, ch_y_max - 20), c_type))
            if c_type == TYPE_TARGET:
                total_target += 1
            else:
                total_normal += 1

        for s in streamlines:
            s.update(ch_y_min, ch_y_max, max_x=910)

        for vfx in vfx_list[:]:
            vfx.update()
            if vfx.life <= 0:
                vfx_list.remove(vfx)

        scanner.update(cells, auto_mode, ch_y_max, vfx_list)

        for cell in cells[:]:
            cell.update(ch_y_min, ch_y_max, split_x)
            if cell.x > 910:
                if cell.y < center_y:
                    sorted_waste += 1
                else:
                    sorted_harvest += 1
                cells.remove(cell)

        purity = (sorted_harvest / max(1, (sorted_harvest + (total_target - sorted_harvest)))) * 100.0
        purity_history.append(purity)

        screen.fill(COLOR_BG)

        pygame.draw.rect(screen, COLOR_CHANNEL_BG, (0, ch_y_min, split_x, ch_y_max - ch_y_min))
        pygame.draw.rect(screen, COLOR_CHANNEL_BG, (split_x, ch_y_min, 920 - split_x, center_y - 15 - ch_y_min))
        pygame.draw.rect(screen, COLOR_CHANNEL_BG, (split_x, center_y + 15, 920 - split_x, ch_y_max - (center_y + 15)))
        pygame.draw.polygon(screen, COLOR_BG, [(split_x, center_y - 15), (split_x + 75, center_y), (split_x, center_y + 15)])

        for gx in range(0, 920, 35):
            pygame.draw.line(screen, (18, 26, 38), (gx, ch_y_min), (gx, ch_y_max), 1)

        for s in streamlines:
            s.draw(screen)

        pygame.draw.line(screen, COLOR_CHANNEL_WALL, (0, ch_y_min), (920, ch_y_min), 3)
        pygame.draw.line(screen, COLOR_CHANNEL_WALL, (0, ch_y_max), (920, ch_y_max), 3)
        pygame.draw.line(screen, COLOR_CHANNEL_WALL, (split_x, center_y - 15), (920, center_y - 15), 2)
        pygame.draw.line(screen, COLOR_CHANNEL_WALL, (split_x, center_y + 15), (920, center_y + 15), 2)

        inlet_alpha = 90 if inlet_flash > 0 else 30
        inlet_surf = pygame.Surface((110, ch_y_max - ch_y_min), pygame.SRCALPHA)
        inlet_surf.fill((0, 255, 140, inlet_alpha))
        screen.blit(inlet_surf, (12, ch_y_min))
        pygame.draw.rect(screen, (0, 255, 140), (12, ch_y_min, 110, ch_y_max - ch_y_min), width=2, border_radius=4)
        screen.blit(FONT_SUB.render("SAMPLE INLET", True, (0, 255, 140)), (16, ch_y_min - 22))

        det_surf = pygame.Surface((200, ch_y_max - ch_y_min), pygame.SRCALPHA)
        det_surf.fill((0, 180, 220, 20))
        screen.blit(det_surf, (320, ch_y_min))
        pygame.draw.rect(screen, (0, 180, 220, 120), (320, ch_y_min, 200, ch_y_max - ch_y_min), width=1)
        screen.blit(FONT_SUB.render("DETECTION & SORTING ZONE", True, (0, 200, 255)), (325, ch_y_min - 22))

        screen.blit(FONT_SUB.render("WASTE OUTLET ➔", True, COLOR_NORMAL), (770, ch_y_min + 12))
        screen.blit(FONT_SUB.render("HARVEST CHAMBER ➔", True, COLOR_TARGET), (750, center_y + 24))

        for cell in cells:
            cell.draw(screen)
        for vfx in vfx_list:
            vfx.draw(screen)
        scanner.draw(screen, ch_y_min, ch_y_max)

        draw_glass_panel(screen, (15, 12, 900, 120))
        screen.blit(FONT_TITLE.render("MICROFLUIDIC LAB-ON-A-CHIP : OPTICAL TWEEZER CELL SORTER", True, (0, 220, 255)), (30, 22))

        mode_str = "AUTOMATED GALVO-LASER SORTING" if auto_mode else "MANUAL PASS-THROUGH (NO SORT)"
        mode_col = COLOR_LASER if auto_mode else (255, 200, 0)
        screen.blit(FONT_DATA.render(f"Control Mode : {mode_str}", True, mode_col), (30, 48))
        screen.blit(FONT_DATA.render(f"Laser Force  : {scanner.current_force_pN:.1f} pN (Optical Gradient Force)", True, (200, 220, 240)), (30, 68))
        screen.blit(FONT_DATA.render(f"Fluid Flow   : 2.5 mm/s (Laminar Poiseuille Hydrodynamics)", True, (200, 220, 240)), (30, 88))

        pygame.draw.circle(screen, (0, 255, 140), (500, 54), 5)
        screen.blit(FONT_KEY.render("LAMINAR FLOW OK", True, (0, 255, 140)), (512, 48))

        laser_led_col = COLOR_LASER if scanner.active else (100, 110, 120)
        pygame.draw.circle(screen, laser_led_col, (500, 74), 5)
        screen.blit(FONT_KEY.render("TRAP ENGAGED" if scanner.active else "LASER READY", True, laser_led_col), (512, 68))

        draw_glass_panel(screen, (930, 12, 335, 690))
        screen.blit(FONT_TITLE.render("REAL-TIME ANALYTICS", True, (0, 220, 255)), (950, 25))

        screen.blit(FONT_SUB.render("SAMPLE COMPOSITION RATIO", True, (180, 200, 220)), (950, 60))
        draw_donut_chart(screen, (1020, 130), 45, 25, total_normal, total_target)
        
        screen.blit(FONT_DATA.render(f"Normal : {total_normal}", True, COLOR_NORMAL), (1085, 110))
        screen.blit(FONT_DATA.render(f"Target : {total_target}", True, COLOR_TARGET), (1085, 130))

        screen.blit(FONT_SUB.render("HARVEST PURITY HISTORY (%)", True, (180, 200, 220)), (950, 195))
        graph_rect = (950, 220, 295, 130)
        pygame.draw.rect(screen, (10, 15, 24), graph_rect, border_radius=6)
        pygame.draw.rect(screen, (40, 55, 75), graph_rect, width=1, border_radius=6)

        for gy in range(220, 350, 25):
            pygame.draw.line(screen, (20, 30, 45), (950, gy), (1245, gy), 1)

        if len(purity_history) >= 2:
            pts = []
            for idx, p_val in enumerate(purity_history):
                gx = 950 + int((idx / 90.0) * 295)
                gy = 350 - int((p_val / 100.0) * 120)
                pts.append((gx, gy))
            pygame.draw.lines(screen, COLOR_LASER, False, pts, 2)

        screen.blit(FONT_DATA.render(f"CURRENT PURITY: {purity:.1f}%", True, COLOR_LASER), (950, 360))

        screen.blit(FONT_SUB.render("HYDRODYNAMIC PARAMETERS", True, (180, 200, 220)), (950, 400))
        param_box = (950, 425, 295, 220)
        pygame.draw.rect(screen, (10, 15, 24), param_box, border_radius=6)
        pygame.draw.rect(screen, (40, 55, 75), param_box, width=1, border_radius=6)

        screen.blit(FONT_DATA.render("Reynolds Number (Re): 0.025", True, (200, 220, 240)), (965, 445))
        screen.blit(FONT_DATA.render("Fluid Regime : Creeping Laminar", True, (0, 255, 140)), (965, 470))
        screen.blit(FONT_DATA.render("Wall Shear Stress: 1.2 Pa", True, (200, 220, 240)), (965, 495))
        screen.blit(FONT_DATA.render("Laser Beam Wavelength: 1064 nm", True, (200, 220, 240)), (965, 520))
        screen.blit(FONT_DATA.render("Trap Stiffness: 0.08 pN/nm", True, (200, 220, 240)), (965, 545))
        screen.blit(FONT_DATA.render("Sorting Throughput: ~120 cells/s", True, (200, 220, 240)), (965, 570))

        btn_auto.draw(screen)
        btn_inject.draw(screen)
        btn_reset.draw(screen)

        screen.blit(FONT_KEY.render("[ESC] EXIT SIMULATION", True, (140, 160, 180)), (450, 672))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
'@ | Out-File -Encoding utf8 microfluidic_cell_sorter.py
python microfluidic_cell_sorter.py
