import pygame
import sys
import random
import os
import json

# 1. Inicialização
pygame.init()

info_tela = pygame.display.Info()
LARGURA = info_tela.current_w if info_tela.current_w > 0 else 360
ALTURA = info_tela.current_h if info_tela.current_h > 0 else 640

tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("Pixel Farm Idle")
relogio = pygame.time.Clock()

# 2. Cores
VERDE_GRAMA = (40, 160, 50)
MARROM_PAINEL = (90, 50, 20)
CINZA_ABA = (70, 70, 70)
AMARELO = (255, 215, 0)
BRANCO = (255, 255, 255)
LARANJA = (230, 120, 20)
VERMELHO = (220, 50, 50)

# Função auxiliar para carregar imagem ou criar uma temporária caso não exista
def carregar_ou_criar(nome, cor_temp, tamanho=(160, 160)):
    if os.path.exists(nome):
        return pygame.image.load(nome)
    else:
        surf = pygame.Surface(tamanho)
        surf.fill(cor_temp)
        return surf

# 3. Carregar Sprites
img_trigo_broto = carregar_ou_criar("broto.png", (100, 200, 100))
img_trigo_medio = carregar_ou_criar("trigo_medio.png", (150, 200, 50))
img_trigo_maduro = carregar_ou_criar("trigo.png", AMARELO)

img_cenoura_broto = carregar_ou_criar("cenoura_broto.png", (100, 180, 80))
img_cenoura_madura = carregar_ou_criar("cenoura.png", LARANJA)

img_tomate_broto = carregar_ou_criar("tomate_broto.png", (100, 180, 80))
img_tomate_maduro = carregar_ou_criar("tomate.png", VERMELHO)

enxada_img = pygame.transform.scale(carregar_ou_criar("enxada.png", BRANCO, (36, 36)), (36, 36))
espantalho_img = pygame.transform.scale(carregar_ou_criar("espantalho.png", BRANCO, (36, 36)), (36, 36))
trator_img = pygame.transform.scale(carregar_ou_criar("trator.png", BRANCO, (36, 36)), (36, 36))
estufa_img = pygame.transform.scale(carregar_ou_criar("estufa.png", BRANCO, (36, 36)), (36, 36))
praga_img = pygame.transform.scale(carregar_ou_criar("praga.png", BRANCO, (48, 48)), (48, 48))

# 4. Variáveis do Jogo
moedas = 0
moedas_por_clique = 1
preco_adubo = 15

espantalhos = 0
preco_espantalho = 10
prod_espantalho = 1

tratores = 0
preco_trator = 50
prod_trator = 5

estufas = 0
preco_estufa = 200
prod_estufa = 25

cultura_atual = "trigo"
cenoura_desbloqueada = False
tomate_desbloqueado = False

preco_desbloqueio_cenoura = 100
preco_desbloqueio_tomate = 500

estagio_planta = 0
cliques_estagio = 0

# --- SISTEMA DE SAVE / LOAD ---
ARQUIVO_SAVE = "save.json"

def salvar_jogo():
    dados = {
        "moedas": moedas,
        "moedas_por_clique": moedas_por_clique,
        "preco_adubo": preco_adubo,
        "espantalhos": espantalhos,
        "preco_espantalho": preco_espantalho,
        "tratores": tratores,
        "preco_trator": preco_trator,
        "estufas": estufas,
        "preco_estufa": preco_estufa,
        "cenoura_desbloqueada": cenoura_desbloqueada,
        "tomate_desbloqueado": tomate_desbloqueado
    }
    with open(ARQUIVO_SAVE, "w") as f:
        json.dump(dados, f)

def carregar_jogo():
    global moedas, moedas_por_clique, preco_adubo
    global espantalhos, preco_espantalho, tratores, preco_trator, estufas, preco_estufa
    global cenoura_desbloqueada, tomate_desbloqueado

    if os.path.exists(ARQUIVO_SAVE):
        try:
            with open(ARQUIVO_SAVE, "r") as f:
                dados = json.load(f)
                moedas = dados.get("moedas", 0)
                moedas_por_clique = dados.get("moedas_por_clique", 1)
                preco_adubo = dados.get("preco_adubo", 15)
                espantalhos = dados.get("espantalhos", 0)
                preco_espantalho = dados.get("preco_espantalho", 10)
                tratores = dados.get("tratores", 0)
                preco_trator = dados.get("preco_trator", 50)
                estufas = dados.get("estufas", 0)
                preco_estufa = dados.get("preco_estufa", 200)
                cenoura_desbloqueada = dados.get("cenoura_desbloqueada", False)
                tomate_desbloqueado = dados.get("tomate_desbloqueado", False)
        except Exception:
            pass

carregar_jogo()

# Controle de Abas ("fazenda" ou "loja")
aba_atual = "fazenda"

# Efeitos Visuais
textos_flutuantes = []
tamanho_trigo_normal = 160
tamanho_trigo = tamanho_trigo_normal
tempo_animacao = 0

# Evento Rápido (Corvo)
praga_ativa = False
praga_rect = pygame.Rect(0, 0, 0, 0)
praga_timer = 0
tempo_proxima_praga = random.randint(300, 600)

EVENTO_GERAR_MOEDAS = pygame.USEREVENT + 1
pygame.time.set_timer(EVENTO_GERAR_MOEDAS, 1000)

# 5. Fontes
fonte_titulo = pygame.font.SysFont(None, int(ALTURA * 0.045))
fonte = pygame.font.SysFont(None, int(ALTURA * 0.03))
fonte_pequena = pygame.font.SysFont(None, int(ALTURA * 0.022))

# Layout
CENTRO_X = LARGURA // 2
CENTRO_Y = ALTURA // 2 - 20

# Botões de Abas
LARGURA_ABA = int(LARGURA * 0.42)
ALTURA_ABA = int(ALTURA * 0.05)
btn_aba_fazenda = pygame.Rect(int(LARGURA * 0.06), int(ALTURA * 0.14), LARGURA_ABA, ALTURA_ABA)
btn_aba_loja = pygame.Rect(int(LARGURA * 0.52), int(ALTURA * 0.14), LARGURA_ABA, ALTURA_ABA)

# Botões da Seletor de Planta
btn_sel_trigo = pygame.Rect(int(LARGURA * 0.08), int(ALTURA * 0.78), int(LARGURA * 0.26), int(ALTURA * 0.06))
btn_sel_cenoura = pygame.Rect(int(LARGURA * 0.37), int(ALTURA * 0.78), int(LARGURA * 0.26), int(ALTURA * 0.06))
btn_sel_tomate = pygame.Rect(int(LARGURA * 0.66), int(ALTURA * 0.78), int(LARGURA * 0.26), int(ALTURA * 0.06))

# Botões da Loja
LARGURA_BTN = int(LARGURA * 0.84)
ALTURA_BTN = int(ALTURA * 0.07)
ESPACO_BTN = int(ALTURA * 0.015)
X_BTN = (LARGURA - LARGURA_BTN) // 2
Y_INICIAL_BTNS = int(ALTURA * 0.22)

btn_adubo = pygame.Rect(X_BTN, Y_INICIAL_BTNS, LARGURA_BTN, ALTURA_BTN)
btn_espantalho = pygame.Rect(X_BTN, Y_INICIAL_BTNS + (ALTURA_BTN + ESPACO_BTN), LARGURA_BTN, ALTURA_BTN)
btn_trator = pygame.Rect(X_BTN, Y_INICIAL_BTNS + (ALTURA_BTN + ESPACO_BTN) * 2, LARGURA_BTN, ALTURA_BTN)
btn_estufa = pygame.Rect(X_BTN, Y_INICIAL_BTNS + (ALTURA_BTN + ESPACO_BTN) * 3, LARGURA_BTN, ALTURA_BTN)
btn_desb_cenoura = pygame.Rect(X_BTN, Y_INICIAL_BTNS + (ALTURA_BTN + ESPACO_BTN) * 4, LARGURA_BTN, ALTURA_BTN)
btn_desb_tomate = pygame.Rect(X_BTN, Y_INICIAL_BTNS + (ALTURA_BTN + ESPACO_BTN) * 5, LARGURA_BTN, ALTURA_BTN)

rodando = True
while rodando:
    praga_timer += 1
    
    if not praga_ativa and praga_timer >= tempo_proxima_praga:
        praga_ativa = True
        praga_x = random.randint(40, LARGURA - 80)
        praga_y = random.randint(int(ALTURA * 0.22), int(ALTURA * 0.4))
        praga_rect = pygame.Rect(praga_x, praga_y, 48, 48)
        praga_timer = 0
        tempo_proxima_praga = random.randint(300, 600)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            salvar_jogo()
            rodando = False
            
        if evento.type == EVENTO_GERAR_MOEDAS:
            moedas += (espantalhos * prod_espantalho) + (tratores * prod_trator) + (estufas * prod_estufa)
            salvar_jogo()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = evento.pos

            if btn_aba_fazenda.collidepoint(pos):
                aba_atual = "fazenda"
            elif btn_aba_loja.collidepoint(pos):
                aba_atual = "loja"

            if aba_atual == "fazenda":
                if btn_sel_trigo.collidepoint(pos):
                    cultura_atual = "trigo"
                    estagio_planta = 0
                    cliques_estagio = 0
                elif btn_sel_cenoura.collidepoint(pos) and cenoura_desbloqueada:
                    cultura_atual = "cenoura"
                    estagio_planta = 0
                    cliques_estagio = 0
                elif btn_sel_tomate.collidepoint(pos) and tomate_desbloqueado:
                    cultura_atual = "tomate"
                    estagio_planta = 0
                    cliques_estagio = 0

                trigo_rect_atual = img_planta_atual.get_rect(center=(CENTRO_X, CENTRO_Y))
                if trigo_rect_atual.collidepoint(pos):
                    tamanho_trigo = 140
                    tempo_animacao = 3
                    cliques_estagio += 1
                    
                    if cultura_atual == "trigo":
                        max_estagios = 2
                        cliques_req = 3
                        mult_colheita = 10
                    elif cultura_atual == "cenoura":
                        max_estagios = 1
                        cliques_req = 5
                        mult_colheita = 25
                    elif cultura_atual == "tomate":
                        max_estagios = 1
                        cliques_req = 8
                        mult_colheita = 60

                    if estagio_planta < max_estagios:
                        moedas += moedas_por_clique
                        textos_flutuantes.append({"texto": f"+{moedas_por_clique}", "x": pos[0], "y": pos[1], "opacity": 255})
                        if cliques_estagio >= cliques_req:
                            estagio_planta += 1
                            cliques_estagio = 0
                    else:
                        ganho_colheita = moedas_por_clique * mult_colheita
                        moedas += ganho_colheita
                        textos_flutuantes.append({"texto": f"COLHEITA! +{ganho_colheita}", "x": pos[0] - 20, "y": pos[1], "opacity": 255})
                        estagio_planta = 0
                        cliques_estagio = 0
                        salvar_jogo()

                if praga_ativa and praga_rect.collidepoint(pos):
                    moedas += 25 * moedas_por_clique
                    praga_ativa = False
                    salvar_jogo()

            elif aba_atual == "loja":
                if btn_adubo.collidepoint(pos) and moedas >= preco_adubo:
                    moedas -= preco_adubo
                    moedas_por_clique += 1
                    preco_adubo = int(preco_adubo * 1.8)
                    salvar_jogo()

                elif btn_espantalho.collidepoint(pos) and moedas >= preco_espantalho:
                    moedas -= preco_espantalho
                    espantalhos += 1
                    preco_espantalho = int(preco_espantalho * 1.5)
                    salvar_jogo()

                elif btn_trator.collidepoint(pos) and moedas >= preco_trator:
                    moedas -= preco_trator
                    tratores += 1
                    preco_trator = int(preco_trator * 1.6)
                    salvar_jogo()

                elif btn_estufa.collidepoint(pos) and moedas >= preco_estufa:
                    moedas -= preco_estufa
                    estufas += 1
                    preco_estufa = int(preco_estufa * 1.7)
                    salvar_jogo()

                elif btn_desb_cenoura.collidepoint(pos) and not cenoura_desbloqueada and moedas >= preco_desbloqueio_cenoura:
                    moedas -= preco_desbloqueio_cenoura
                    cenoura_desbloqueada = True
                    salvar_jogo()

                elif btn_desb_tomate.collidepoint(pos) and not tomate_desbloqueado and moedas >= preco_desbloqueio_tomate:
                    moedas -= preco_desbloqueio_tomate
                    tomate_desbloqueado = True
                    salvar_jogo()

    if tempo_animacao > 0:
        tempo_animacao -= 1
    else:
        tamanho_trigo = tamanho_trigo_normal

    if cultura_atual == "trigo":
        img_base = img_trigo_broto if estagio_planta == 0 else (img_trigo_medio if estagio_planta == 1 else img_trigo_maduro)
    elif cultura_atual == "cenoura":
        img_base = img_cenoura_broto if estagio_planta == 0 else img_cenoura_madura
    elif cultura_atual == "tomate":
        img_base = img_tomate_broto if estagio_planta == 0 else img_tomate_maduro

    img_planta_atual = pygame.transform.scale(img_base, (tamanho_trigo, tamanho_trigo))
    trigo_rect = img_planta_atual.get_rect(center=(CENTRO_X, CENTRO_Y))

    # --- DESENHO NA TELA ---
    tela.fill(VERDE_GRAMA)

    mps = (espantalhos * prod_espantalho) + (tratores * prod_trator) + (estufas * prod_estufa)
    txt_moedas = fonte_titulo.render(f"{moedas} Moedas", True, AMARELO)
    tela.blit(txt_moedas, txt_moedas.get_rect(center=(CENTRO_X, int(ALTURA * 0.05))))

    txt_mps = fonte_pequena.render(f"+{mps}/s | Clique: +{moedas_por_clique}", True, BRANCO)
    tela.blit(txt_mps, txt_mps.get_rect(center=(CENTRO_X, int(ALTURA * 0.09))))

    cor_aba_fazenda = MARROM_PAINEL if aba_atual == "fazenda" else CINZA_ABA
    cor_aba_loja = MARROM_PAINEL if aba_atual == "loja" else CINZA_ABA

    pygame.draw.rect(tela, cor_aba_fazenda, btn_aba_fazenda, border_radius=6)
    pygame.draw.rect(tela, cor_aba_loja, btn_aba_loja, border_radius=6)

    t_faz = fonte.render("Fazenda", True, BRANCO)
    t_loj = fonte.render("Loja", True, BRANCO)
    tela.blit(t_faz, t_faz.get_rect(center=btn_aba_fazenda.center))
    tela.blit(t_loj, t_loj.get_rect(center=btn_aba_loja.center))

    if aba_atual == "fazenda":
        tela.blit(img_planta_atual, trigo_rect)
        
        txt_est = fonte.render(f"Plantação: {cultura_atual.capitalize()}", True, BRANCO)
        tela.blit(txt_est, txt_est.get_rect(center=(CENTRO_X, CENTRO_Y + 100)))

        pygame.draw.rect(tela, MARROM_PAINEL if cultura_atual == "trigo" else CINZA_ABA, btn_sel_trigo, border_radius=6)
        pygame.draw.rect(tela, MARROM_PAINEL if cultura_atual == "cenoura" else (CINZA_ABA if cenoura_desbloqueada else (40, 40, 40)), btn_sel_cenoura, border_radius=6)
        pygame.draw.rect(tela, MARROM_PAINEL if cultura_atual == "tomate" else (CINZA_ABA if tomate_desbloqueado else (40, 40, 40)), btn_sel_tomate, border_radius=6)

        tela.blit(fonte_pequena.render("Trigo", True, BRANCO), fonte_pequena.render("Trigo", True, BRANCO).get_rect(center=btn_sel_trigo.center))
        tela.blit(fonte_pequena.render("Cenoura" if cenoura_desbloqueada else "Bloqueado", True, BRANCO), fonte_pequena.render("Cenoura" if cenoura_desbloqueada else "Bloqueado", True, BRANCO).get_rect(center=btn_sel_cenoura.center))
        tela.blit(fonte_pequena.render("Tomate" if tomate_desbloqueado else "Bloqueado", True, BRANCO), fonte_pequena.render("Tomate" if tomate_desbloqueado else "Bloqueado", True, BRANCO).get_rect(center=btn_sel_tomate.center))

        if praga_ativa:
            tela.blit(praga_img, praga_rect.topleft)

    elif aba_atual == "loja":
        botoes = [
            (btn_adubo, f"Enxada (Nv. {moedas_por_clique})", f"Custo: {preco_adubo} moedas", enxada_img),
            (btn_espantalho, f"Espantalho ({espantalhos})", f"Custo: {preco_espantalho} | +1/s", espantalho_img),
            (btn_trator, f"Trator ({tratores})", f"Custo: {preco_trator} | +5/s", trator_img),
            (btn_estufa, f"Estufa Agricola ({estufas})", f"Custo: {preco_estufa} | +25/s", estufa_img),
            (btn_desb_cenoura, "Semente Cenoura", "COMPRADO" if cenoura_desbloqueada else f"Custo: {preco_desbloqueio_cenoura} moedas", enxada_img),
            (btn_desb_tomate, "Semente Tomate", "COMPRADO" if tomate_desbloqueado else f"Custo: {preco_desbloqueio_tomate} moedas", enxada_img)
        ]

        for rect_b, titulo, sub, img in botoes:
            pygame.draw.rect(tela, MARROM_PAINEL, rect_b, border_radius=8)
            tela.blit(img, (rect_b.x + 8, rect_b.y + (rect_b.height - 36) // 2))
            tela.blit(fonte.render(titulo, True, BRANCO), (rect_b.x + 50, rect_b.y + 4))
            tela.blit(fonte_pequena.render(sub, True, AMARELO), (rect_b.x + 50, rect_b.y + rect_b.height - 20))

    for tf in textos_flutuantes[:]:
        txt_f = fonte.render(tf["texto"], True, AMARELO)
        tela.blit(txt_f, (tf["x"], tf["y"]))
        tf["y"] -= 2
        tf["opacity"] -= 10
        if tf["opacity"] <= 0:
            textos_flutuantes.remove(tf)

    pygame.display.flip()
    relogio.tick(30)

pygame.quit()
sys.exit()