import os
import sys
import subprocess
import time
import pygame

# 1. BEZPIECZEŃSTWO STARTU: Czekamy 3 sekundy na załadowanie sterowników USB/pada przez Windows
time.sleep(3)

# Poprawka na ostrość obrazu
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.joystick.init()

# Bezpieczna inicjalizacja padów na starcie
def zainicjuj_pady():
    try:
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
    except:
        pass

zainicjuj_pady()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Boot Menu")

# Twoje oryginalne kolory i wygląd
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
        folder_playnite = os.path.dirname(sciezka_playnite)
        try:
            # Uruchomienie z jawnym wskazaniem folderu roboczego zapobiega WinError 2
            subprocess.Popen([sciezka_playnite, "--fullscreen"], cwd=folder_playnite)
        except:
            pass
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
            
        # Bezpieczne odświeżanie po wykryciu zmiany sprzętu
        if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
            zainicjuj_pady()
            
        # Klawiatura
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: wybrany = 0
            if event.key == pygame.K_DOWN: wybrany = 1
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                uruchom_wybor(wybrany)
                
        # Myszka
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        uruchom_wybor(i)

        # Pad: Zatwierdzenie przyciskiem
        if event.type == pygame.JOYBUTTONDOWN:
            uruchom_wybor(wybrany)

        # Pad: Bezpieczne sterowanie gałką przez system zdarzeń (brak błędów typu get)
        if event.type == pygame.JOYAXISMOTION:
            if cooldown == 0 and event.axis == 1:
                if event.value > 0.5:
                    wybrany = 1
                    cooldown = 15
                elif event.value < -0.5:
                    wybrany = 0
                    cooldown = 15

        # Pad: Bezpieczne sterowanie krzyżakiem (D-Pad)
        if event.type == pygame.JOYHATMOTION:
            if cooldown == 0:
                if event.value[1] == -1:
                    wybrany = 1
                    cooldown = 15
                elif event.value[1] == 1:
                    wybrany = 0
                    cooldown = 15

    # Rysowanie kafelków (Dokładnie Twój oryginalny design)
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
