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

# Pełny ekran
screen = pygame.display.set_mode(
    (0, 0), 
    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
)
width, height = screen.get_size()

# Paleta kolorów - tylko czerń, szarości i biel
CLR_BG = (0, 0, 0)          # Czarne tło
CLR_BOX_OFF = (40, 40, 40)  # Ciemnoszary kafelek
CLR_BOX_ON = (100, 100, 100) # Jasnoszary kafelek (aktywny)
CLR_TEXT = (255, 255, 255)  # Biały napis

font = pygame.font.SysFont("Arial", 60, bold=True)
options = ["PC", "PLAYNITE"]
selected = 0

# Bezpieczne odświeżanie padów
def refresh_joysticks():
    try:
        pygame.joystick.quit()
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
    except:
        pass

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
    mouse_pos = pygame.mouse.get_pos()
    
    for i, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos):
            selected = i

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        
        # Automatyczne podpinanie padów w dowolnym momencie
        if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
            refresh_joysticks()
        
        # Sterowanie klawiaturą
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected = 0
            if event.key == pygame.K_DOWN:
                selected = 1
            if event.key == pygame.K_RETURN:
                trigger_launch(selected)
                
        # Sterowanie myszką
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        trigger_launch(i)

        # Kliknięcie dowolnego przycisku na padzie zatwierdza
        if event.type == pygame.JOYBUTTONDOWN:
            trigger_launch(selected)

        # BEZPIECZNE STEROWANIE GAŁKĄ (Brak crashów przy włączaniu pada)
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 1: # Pionowa oś lewej gałki
                if event.value > 0.5:
                    selected = 1
                elif event.value < -0.5:
                    selected = 0

        # BEZPIECZNE STEROWANIE KRZYŻAKIEM
        if event.type == pygame.JOYHATMOTION:
            if event.value[1] == -1: # W dół
                selected = 1
            elif event.value[1] == 1: # W górę
                selected = 0

    # Rysowanie interfejsu (Czysty minimalizm)
    for i, rect in enumerate(button_rects):
        box_color = CLR_BOX_ON if i == selected else CLR_BOX_OFF
        pygame.draw.rect(screen, box_color, rect)
        
        txt_surf = font.render(options[i], True, CLR_TEXT)
        text_rect = txt_surf.get_rect(center=rect.center)
        screen.blit(txt_surf, text_rect)

    pygame.display.flip()
    clock.tick(60)
