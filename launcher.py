import os
import sys
import subprocess
import pygame

# POPRAWKA NA JAKOŚĆ: Wymuszenie ostrej rozdzielczości na Windowsie
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.joystick.init()

# Inicjalizacja WSZYSTKICH podpiętych padów
joysticks = []
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)

# Uruchomienie w pełnym ekranie z natywną rozdzielczością monitora
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Boot Menu")

# Kolory (bardziej nowoczesne, mroczne)
CZARNY = (10, 10, 12)
SZARY = (30, 30, 35)
ZIELONY = (0, 184, 148)
BIALY = (255, 255, 255)

font = pygame.font.SysFont("Segoe UI", 42, bold=True)
opcje = ["1. TRYB PC (PULPIT)", "2. KONSOLA (PLAYNITE)"]
wybrany = 0
cooldown = 0

# Definiujemy pozycje kafelków (potrzebne też do klikania myszką)
rect_pc = pygame.Rect(width//2 - 300, height//2 - 150, 600, 110)
rect_konsola = pygame.Rect(width//2 - 300, height//2 + 10, 600, 110)
rects = [rect_pc, rect_konsola]

def uruchom_wybor(indeks):
    pygame.quit()
    if indeks == 0:
        sys.exit()
    elif indeks == 1:
        os.system("taskkill /f /im explorer.exe")
        sciezka_playnite = os.path.expandvars(r"%LOCALAPPDATA%\Playnite\Playnite.FullscreenApp.exe")
        subprocess.Popen([sciezka_playnite, "--fullscreen"])
        sys.exit()

clock = pygame.time.Clock()

while True:
    screen.fill(CZARNY)
    if cooldown > 0:
        cooldown -= 1

    # Automatyczne najechanie myszką też podświetla kafelki
    mouse_pos = pygame.mouse.get_pos()
    for i, rect in enumerate(rects):
        if rect.collidepoint(mouse_pos):
            wybrany = i

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            
        # OBSŁUGA KLAWIATURY
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: wybrany = 0
            if event.key == pygame.K_DOWN: wybrany = 1
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                uruchom_wybor(wybrany)
                
        # OBSŁUGA MYSZKI (w razie czego kliknięcie też zadziała)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Lewy klik
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        uruchom_wybor(i)

        # OBSŁUGA PADA (Dowolny przycisk: A, X, Start, itp. zatwierdza)
        if event.type == pygame.JOYBUTTONDOWN:
            uruchom_wybor(wybrany)

    # REAKCJA NA GAŁKĘ / KRZYŻAK PADA
    for joy in joysticks:
        if cooldown == 0:
            axis = joy.get_axis(1) if joy.get_numaxes() > 1 else 0
            hat = joy.get_hat(0) if joy.get_numhats() > 0 else (0,0)
            
            if axis > 0.5 or hat[1] == -1: # W dół
                wybrany = 1
                cooldown = 15
            elif axis < -0.5 or hat[1] == 1: # W górę
                wybrany = 0
                cooldown = 15

    # RYSOWANIE INTERFEJSU
    for i, opcja in enumerate(opcje):
        kolor_tla = ZIELONY if i == wybrany else SZARY
        pygame.draw.rect(screen, kolor_tla, rects[i], border_radius=20)
        
        # Ramka wokół aktywnego wyboru
        if i == wybrany:
            pygame.draw.rect(screen, BIALY, rects[i], width=3, border_radius=20)
            
        tekst = font.render(opcja, True, BIALY)
        text_rect = tekst.get_rect(center=rects[i].center)
        screen.blit(tekst, text_rect)

    pygame.display.flip()
    clock.tick(60)
