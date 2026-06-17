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
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Boot Menu")

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
    
    # Ścieżka do nircmd.exe (zakładamy, że jest w tym samym folderze co launcher)
    nircmd_path = "nircmd.exe"
    
    # Odczytujemy zapisane urządzenia z pliku ustawienia.txt
    audio_pc = ""
    audio_pn = ""
    if os.path.exists("ustawienia.txt"):
        try:
            with open("ustawienia.txt", "r", encoding="utf-8") as f:
                linie = [linia.strip() for linia in f.readlines() if linia.strip()]
                if len(linie) >= 1: audio_pc = linie[0]
                if len(linie) >= 2: audio_pn = linie[1]
        except:
            pass

    if indeks == 0:
        # Przełącz dźwięk na PC, jeśli urządzenie zostało zdefiniowane
        if audio_pc:
            subprocess.Popen([nircmd_path, "setdefaultsounddevice", audio_pc])
        sys.exit()
        
    elif indeks == 1:
        # Przełącz dźwięk na Playnite, jeśli urządzenie zostało zdefiniowane
        if audio_pn:
            subprocess.Popen([nircmd_path, "setdefaultsounddevice", audio_pn])
            
        # Odpalenie Playnite
        sciezka_playnite = r"D:\Programs\Playnite\Playnite.FullscreenApp.exe"
        folder_playnite = os.path.dirname(sciezka_playnite)
        try:
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

    for joy in joysticks:
        if cooldown == 0:
            axis = joy.get_axis(1) if joy.get_numaxes() > 1 else 0
            hat = joy.get_hat(0) if joy.get_numhats() > 0 else (0,0)
            
            if axis > 0.5 or hat[1] == -1:
                wybrany = 1
                cooldown = 15
            elif axis < -0.5 or hat[1] == 1:
                wybrany = 0
                cooldown = 15

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
