import os
import sys
import subprocess
import pygame

# Poprawka na ostrość obrazu
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.joystick.init()

joysticks = []

def odswiez_kontrolery():
    """Bezpiecznie inicjuje i aktualizuje listę podpiętych padów."""
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

# Wyszukanie kontrolerów na starcie
odswiez_kontrolery()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Boot Menu")

# Oryginalne kolory z Twojego kodu
CZARNY = (10, 10, 12)
SZARY = (30, 30, 35)
ZIELONY = (0, 184, 148)
BIALY = (255, 255, 255)

font = pygame.font.SysFont("Segoe UI", 42, bold=True)
opcje = ["1. TRYB PC (PULPIT)", "2. KONSOLA (PLAYNITE)"]
wybrany = 0
cooldown = 0

rect_pc = pygame.Rect(width//2 - 300, height//2 - 150, 600, 110)
rect_konsola = pygame.Rect(width//2 - 300, height//2 + 10, 600, 110)
rects = [rect_pc, rect_konsola]

def uruchom_wybor(indeks):
    pygame.quit()
    if indeks == 0:
        sys.exit()
    elif indeks == 1:
        sciezka_playnite = r"D:\Programs\Playnite\Playnite.FullscreenApp.exe"
        subprocess.Popen([sciezka_playnite, "--fullscreen"])
        sys.exit()

clock = pygame.time.Clock()

while True:
    screen.fill(CZARNY)
    if cooldown > 0:
        cooldown -= 1

    mouse_pos = pygame.mouse.get_pos()
    for i, rect in enumerate(rects):
        if rect.collidepoint(mouse_pos):
            wybrany = i

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            
        # Wykrywanie podłączenia/włączenia pada w locie
        if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
            odswiez_kontrolery()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: wybrany = 0
            if event.key == pygame.K_DOWN: wybrany = 1
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                uruchom_wybor(wybrany)
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        uruchom_wybor(i)

        if event.type == pygame.JOYBUTTONDOWN:
            uruchom_wybor(wybrany)

    # Bezpieczne odpytywanie stanu gałek i d-pada (odporne na błędy get())
    if cooldown == 0:
        for joy in joysticks:
            try:
                num_axes = joy.get_numaxes()
                num_hats = joy.get_numhats()
                
                axis = joy.get_axis(1) if num_axes > 1 else 0
                hat = joy.get_hat(0) if num_hats > 0 else (0,0)
                
                if axis > 0.5 or hat[1] == -1:
                    wybrany = 1
                    cooldown = 15
                    break
                elif axis < -0.5 or hat[1] == 1:
                    wybrany = 0
                    cooldown = 15
                    break
            except:
                # W razie chwilowego błędu systemu przy konfiguracji pada
                odswiez_kontrolery()
                break

    # Rysowanie kafelków – dokładnie tak, jak w Twoim kodzie pierwotnym
    for i, opcja in enumerate(opcje):
        kolor_tla = ZIELONY if i == wybrany else SZARY
        pygame.draw.rect(screen, kolor_tla, rects[i], border_radius=20)
        
        if i == wybrany:
            pygame.draw.rect(screen, BIALY, rects[i], width=3, border_radius=20)
            
        tekst = font.render(opcja, True, BIALY)
        text_rect = tekst.get_rect(center=rects[i].center)
        screen.blit(tekst, text_rect)

    pygame.display.flip()
    clock.tick(60)
