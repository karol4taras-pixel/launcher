import os
import sys
import subprocess
import pygame
import pygame.gfxdraw

# --- KONFIGURACJA ---
PATH_PLAYNITE = r"D:\Programs\Playnite\Playnite.FullscreenApp.exe"

try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.joystick.init()

# --- INICJALIZACJA INTERFEJSU ---
screen = pygame.display.set_mode(
    (0, 0), 
    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
)
width, height = screen.get_size()
pygame.display.set_caption("Windows / Xbox Style Boot Menu")

# --- KOLORY INTERFEJSU ---
CLR_BG = (12, 12, 15)
CLR_TEXT = (240, 240, 240)
CLR_FRAME = (255, 255, 255)

CLR_GRADIENT_OFF = [(35, 35, 40), (20, 20, 25)]
CLR_GRADIENT_ON = [(0, 161, 80), (0, 120, 60)]

CLR_GLOW = (46, 204, 113)
GLOW_WIDTH = 25
GLOW_ALPHA = 100

BTN_W, BTN_H = 650, 130
BTN_CORNER_RAD = 30

# --- CZCIONKA ---
preferred_fonts = ["Segoe UI Semibold", "Segoe UI", "Arial"]
found_font = "Arial"
available_fonts = pygame.font.get_fonts()
for pf in preferred_fonts:
    if pf.lower().replace(" ", "") in available_fonts:
        found_font = pf
        break
font = pygame.font.SysFont(found_font, 48, bold=True)

# --- CACHE ELEMENTÓW ---
def create_gradient_surface(w, h, gradient_colors):
    base = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        r_diff = gradient_colors[1][0] - gradient_colors[0][0]
        g_diff = gradient_colors[1][1] - gradient_colors[0][1]
        b_diff = gradient_colors[1][2] - gradient_colors[0][2]
        
        r = gradient_colors[0][0] + r_diff * y / h
        g = gradient_colors[0][1] + g_diff * y / h
        b = gradient_colors[0][2] + b_diff * y / h
        base.fill((int(r), int(g), int(b), 255), (0, y, w, 1))
    return base

def create_button_surface(w, h, colors, is_active=False):
    total_w = int(w + (GLOW_WIDTH * 2) if is_active else w)
    total_h = int(h + (GLOW_WIDTH * 2) if is_active else h)
    surface = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

    if is_active:
        glow_surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        for r in range(GLOW_WIDTH):
            alpha = int(GLOW_ALPHA * (1 - (r / GLOW_WIDTH)**0.7))
            g_rect = (GLOW_WIDTH - r, GLOW_WIDTH - r, w + (2*r), h + (2*r))
            g_color = (CLR_GLOW[0], CLR_GLOW[1], CLR_GLOW[2], alpha)
            pygame.gfxdraw.box(glow_surf, g_rect, g_color)
        surface.blit(glow_surf, (0, 0))

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    white_mask = (255, 255, 255, 255)
    mask_rect = (0, 0, w, h)
    pygame.draw.rect(
        mask, 
        white_mask, 
        mask_rect, 
        border_radius=BTN_CORNER_RAD
    )
    
    gradient_surf = create_gradient_surface(w, h, colors)
    gradient_surf.blit(
        mask, 
        (0, 0), 
        special_flags=pygame.BLEND_RGBA_MULT
    )

    if is_active:
        pygame.draw.rect(
            gradient_surf, 
            CLR_FRAME, 
            (0, 0, w, h), 
            width=3, 
            border_radius=BTN_CORNER_RAD
        )

    pos_x = GLOW_WIDTH if is_active else 0
    pos_y = GLOW_WIDTH if is_active else 0
    surface.blit(gradient_surf, (pos_x, pos_y))
    return surface

SURF_PC_OFF = create_button_surface(BTN_W, BTN_H, CLR_GRADIENT_OFF, False)
SURF_PC_ON = create_button_surface(BTN_W, BTN_H, CLR_GRADIENT_ON, True)
SURF_PN_OFF = create_button_surface(BTN_W, BTN_H, CLR_GRADIENT_OFF, False)
SURF_PN_ON = create_button_surface(BTN_W, BTN_H, CLR_GRADIENT_ON, True)

cache_surfaces = [[SURF_PC_OFF, SURF_PC_ON], [SURF_PN_OFF, SURF_PN_ON]]

SURF_BG = pygame.Surface((width, height))
SURF_BG.fill(CLR_BG)
for r in range(height//2, height):
    color_val = CLR_BG[0] + ((50 - CLR_BG[0]) * (1 - r/height))
    color_rgb = (int(color_val), int(color_val), int(color_val*1.1))
    pygame.draw.circle(SURF_BG, color_rgb, (width//2, height//2), r, width=2)

rect_pc = pygame.Rect(
    width//2 - BTN_W//2, 
    height//2 - BTN_H - 15, 
    BTN_W, 
    BTN_H
)
rect_konsola = pygame.Rect(
    width//2 - BTN_W//2, 
    height//2 + 15, 
    BTN_W, 
    BTN_H
)
button_rects = [rect_pc, rect_konsola]

options = ["TRYB PC (PULPIT)", "PLAYNITE (KONSOLA)"]
selected = 0
cooldown = 0

joysticks = []
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)

def trigger_launch(index):
    pygame.quit()
    if index == 0:
        sys.exit()
    elif index == 1:
        subprocess.Popen([PATH_PLAYNITE, "--fullscreen"])
        sys.exit()

clock = pygame.time.Clock()

while True:
    screen.blit(SURF_BG, (0, 0))
    if cooldown > 0: cooldown -= 1

    mouse_pos = pygame.mouse.get_pos()
    for i, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos):
            selected = i

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: selected = 0
            if event.key == pygame.K_DOWN: selected = 1
            if event.key == pygame.K_RETURN: trigger_launch(selected)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        trigger_launch(i)

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0 or event.button == 7:
                trigger_launch(selected)

    for joy in joysticks:
        if cooldown == 0:
            axis = joy.get_axis(1) if joy.get_numaxes() > 1 else 0
            hat = joy.get_hat(0) if joy.get_numhats() > 0 else (0,0)
            
            if axis > 0.5 or hat[1] == -1:
                selected = 1
                cooldown = 15
            elif axis < -0.5 or hat[1] == 1:
                selected = 0
                cooldown = 15

    for i, (surf_off, surf_on) in enumerate(cache_surfaces):
        is_active = (i == selected)
        active_surf = surf_on if is_active else surf_off
        
        b_rect = button_rects[i]
        pos_x = b_rect.x - GLOW_WIDTH if is_active else b_rect.x
        pos_y = b_rect.y - GLOW_WIDTH if is_active else b_rect.y
        screen.blit(active_surf, (pos_x, pos_y))
        
        txt_surf = font.render(options[i], True, CLR_TEXT)
        text_rect = txt_surf.get_rect(center=b_rect.center)
        screen.blit(txt_surf, text_rect)

    pygame.display.flip()
    clock.tick(60)
