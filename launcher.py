import os
import sys
import subprocess
import pygame
import pygame.gfxdraw  # Potrzebne do zaawansowanych cieni

# --- KONFIGURACJA ---
# Twoja dokładna ścieżka do Playnite:
PATH_PLAYNITE = r"D:\Programs\Playnite\Playnite.FullscreenApp.exe"

# Poprawka na ostrość obrazu na Windows
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass

pygame.init()
pygame.joystick.init()

# --- INICJALIZACJA INTERFEJSU ---
# Pełny ekran w natywnej rozdzielczości monitora
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
width, height = screen.get_size()
pygame.display.set_caption("Windows / Xbox Style Boot Menu")

# --- KOLORY INTERFEJSU (Fluent Design) ---
CLR_BG = (12, 12, 15)  # Bardzo głębokie tło
CLR_TEXT = (240, 240, 240)  # Off-white dla czcionki
CLR_FRAME = (255, 255, 255) # Biała ramka dla aktywnego

# Gradienty kafelka: [Start, Stop]
CLR_GRADIENT_OFF = [(35, 35, 40), (20, 20, 25)]  # Ciemny grafit
CLR_GRADIENT_ON = [(0, 161, 80), (0, 120, 60)]    # Xboxowy zielony

# Cień (Glow): [Kolor, Max_Alpha, Szerokosc]
CLR_GLOW = (46, 204, 113)  # Jaśniejsza zieleń
GLOW_WIDTH = 25
GLOW_ALPHA = 100

# Wymiary kafelków
BTN_W, BTN_H = 650, 130
BTN_CORNER_RAD = 30  # Duże zaokrąglenia

# --- CZCIONKA ---
preferred_fonts = ["Segoe UI Semibold", "Segoe UI", "Arial"]
found_font = "Arial"
available_fonts = pygame.font.get_fonts()
for pf in preferred_fonts:
    if pf.lower().replace(" ", "") in available_fonts:
        found_font = pf
        break
font = pygame.font.SysFont(found_font, 48, bold=True)

# --- CACHE GENEROWANIA ELEMENTÓW (Dla wydajności) ---
def create_gradient_surface(w, h, gradient_colors):
    """Generuje gradient poziomy w pamięci."""
    base = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        r = gradient_colors[0][0] + (gradient_colors[1][0] - gradient_colors[0][0]) * y / h
        g = gradient_colors[0][1] + (gradient_colors[1][1] - gradient_colors[0][1]) * y / h
        b = gradient_colors[0][2] + (gradient_colors[1][2] - gradient_colors[0][2]) * y / h
        base.fill((int(r), int(g), int(b), 255), (0, y, w, 1))
    return base

def create_button_surface(w, h, colors, is_active=False):
    """Generuje kafelek z zaokrągleniami, gradientem i (opcjonalnie) glow."""
    total_w = w + (GLOW_WIDTH * 2) if is_active else w
    total_w = int(total_w)
    total_h = h + (GLOW_WIDTH * 2) if is_active else h
    total_h = int(total_h)
    surface = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

    # 1. Rysujemy Cień (Glow) jeśli kafelek jest aktywny
    if is_active:
        glow_surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        for r in range(GLOW_WIDTH):
            alpha = int(GLOW_ALPHA * (1 - (r / GLOW_WIDTH)**0.7))
            rect_coords = (GLOW_WIDTH - r, GLOW_WIDTH - r, w + (2*r), h + (2*r))
            pygame.gfxdraw.box(glow_surf, rect_coords, (CLR_GLOW[0], CLR_GLOW[1], CLR_GLOW[2], alpha))
        surface.blit(glow_surf, (0, 0))

    # 2. Tworzymy zaokrągloną maskę (kształt kafelka)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255
