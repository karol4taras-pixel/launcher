import os
import sys
import subprocess
import pygame

pygame.init()
pygame.joystick.init()

joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()

CZARNY = (15, 15, 15)
SZARY = (40, 40, 40)
ZIELONY = (46, 204, 113)
BIALY = (255, 255, 255)

font = pygame.font.SysFont("Arial", 40, bold=True)
opcje = ["1. TRYB PC (PULPIT)", "2. KONSOLA (PLAYNITE)"]
wybrany = 0
cooldown = 0

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
    if cooldown > 0: cooldown -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: wybrany = 0
            if event.key == pygame.K_DOWN: wybrany = 1
            if event.key == pygame.K_RETURN: uruchom_wybor(wybrany)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                uruchom_wybor(wybrany)

    if joystick and cooldown == 0:
        axis = joystick.get_axis(1)
        hat = joystick.get_hat(0) if joystick.get_numhats() > 0 else (0,0)
        if axis > 0.5 or hat[1] == -1:
            wybrany = 1
            cooldown = 15
        elif axis < -0.5 or hat[1] == 1:
            wybrany = 0
            cooldown = 15

    for i, opcja in enumerate(opcje):
        kolor_tla = ZIELONY if i == wybrany else SZARY
        rect = pygame.Rect(width//2 - 300, height//2 - 150 + (i * 140), 600, 100)
        pygame.draw.rect(screen, kolor_tla, rect, border_radius=15)
        tekst = font.render(opcja, True, BIALY)
        text_rect = tekst.get_rect(center=rect.center)
        screen.blit(tekst, text_rect)

    pygame.display.flip()
    clock.tick(60)