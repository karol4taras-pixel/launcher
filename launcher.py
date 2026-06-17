import os
import sys
import subprocess
import pygame

# Ścieżka do Playnite
PATH_PLAYNITE = r"D:\Programs\Playnite\Playnite.FullscreenApp.exe"

try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.joystick.init()

# Pełny ekran w natywnej rozdzielczości
screen = pygame.display.set_mode(
    (0, 0), 
    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
)
width, height = screen.get_size()

# Paleta - surowy minimalizm i odcienie szarości
CLR_BG = (0, 0, 0)          # Idealna czerń
CLR_BOX_OFF = (40, 40, 40)  # Ciemnoszary kafelek
CLR_BOX_ON = (90, 90, 90)   # Jasnoszary kafelek
CLR_TEXT = (255, 255, 255)  # Czysta biel

font = pygame.font.SysFont("Arial", 55, bold=True)
options = ["PC", "PLAYNITE"]
selected = 0
cooldown = 0

joysticks = []

def refresh_joysticks():
    """Całkowite odświeżenie i bezpieczna ponowna inicjalizacja padów."""
    global joysticks
    try:
        pygame.joystick.quit()
        pygame.joystick.init()
        joysticks = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            joysticks.append(joy)
    except:
        pass

# Szukaj padów na starcie
refresh_joysticks()

# Wymiary klocków
BTN_W, BTN_H = 450, 90
rect_pc = pygame.Rect(
    width//2 - BTN_W//2, 
    height//2 - BTN_H - 25, 
    BTN_W, 
    BTN_H
)
rect_pn = pygame.Rect(
    width//2 - BTN_W//2, 
    height//2 + 25, 
    BTN_W, 
    BTN_H
)
button_rects = [rect_pc, rect_pn]

def trigger_launch(index):
    pygame.quit()
    if index == 0:
        sys.exit()
    elif index == 1:
        subprocess.Popen([PATH_PLAYNITE, "--fullscreen"])
        sys.exit()

clock = pygame.time.Clock()

while True:
    screen.fill(CLR_BG)
    if cooldown > 0:
        cooldown -= 1

    mouse_pos = pygame.mouse.get_pos()
    for i, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos):
            selected = i

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        
        # Wykrywanie wpięcia/włączenia pada w locie
        if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
            refresh_joysticks()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected = 0
            if event.key == pygame.K_DOWN:
                selected = 1
            if event.key == pygame.K_RETURN:
                trigger_launch(selected)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        trigger_launch(i)

        if event.type == pygame.JOYBUTTONDOWN:
            trigger_launch(selected)

    # Bezpieczna obsługa ruchu na padzie (odporna na błędy Windowsa)
    for joy in joysticks:
        if cooldown == 0:
            try:
                axis = joy.get_axis(1) if joy.get_numaxes() > 1 else 0
                hat = joy.get_hat(0) if joy.get_numhats() > 0 else (0, 0)
                
                if axis > 0.5 or hat[1] == -1:
                    selected = 1
                    cooldown = 15
                elif axis < -0.5 or hat[1] == 1:
                    selected = 0
                    cooldown = 15
            except:
                # W razie jakiegokolwiek błędu odczytu, resetujemy urządzenia i jedziemy dalej
                refresh_joysticks()
                break

    # Rysowanie kafelków
    for i, rect in enumerate(button_rects):
        box_color = CLR_BOX_ON if i == selected else CLR_BOX_OFF
        pygame.draw.rect(screen, box_color, rect)
        
        txt_surf = font.render(options[i], True, CLR_TEXT)
        text_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, text_rect)

    pygame.display.flip()
    clock.tick(60)
