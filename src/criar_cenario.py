import sys
import pygame

from src.constantes import Celula, CORES_CELULA, FPS
from src.recursos import carregar_imagens

# === CONSTANTES GLOBAIS ===

# Tamanho e cores da tela
LARGURA_TELA = 800
ALTURA_INPUT_TELA = 200
MIN_TAMANHO_CELULA = 10

COR_FUNDO = (30, 30, 30)
COR_GRADE = (60, 60, 60)
COR_DESTAQUE = (100, 100, 255)
COR_TEXTO = (200, 200, 200)

# Fonte
TAMANHO_FONTE = 36

# Posição e layout da tela de input
INPUT_TITULOS = [
    "Configurar Grid - Insira número de linhas",
    "Configurar Grid - Insira número de colunas"
]
INPUT_LABELS = ["Número de linhas:", "Número de colunas:"]
INPUT_Y_POSICOES = [70, 150]
INPUT_X = 20
N_INPUTS = 2
CARACTERE_CURSOR = "_"

# Texto principal da tela de grid
TITULO_TELA_CENARIO = "Criador de Cenário. Aperte espaço para fechar."

# Valores válidos de célula
VALIDAS = (
    Celula.VAZIA,
    Celula.BARREIRA,
    Celula.PERSONAGEM,
    Celula.SAIDA,
    Celula.FRUTA,
    Celula.SEMI_BARREIRA
)

# ==========================

pygame.init()


class Estado:
    fonte = pygame.font.SysFont(None, TAMANHO_FONTE)
    imagens_dict = {}
    tela = None
    cenario = None


def input_linhas_colunas_tela():
    tela = pygame.display.set_mode((LARGURA_TELA // 2, ALTURA_INPUT_TELA))

    campo_atual = 0
    inputs_txt = ["", ""]
    pygame.display.set_caption(INPUT_TITULOS[0])

    while True:
        tela.fill(COR_FUNDO)

        for i in range(N_INPUTS):
            cor = COR_DESTAQUE if i == campo_atual else COR_TEXTO
            label = Estado.fonte.render(INPUT_LABELS[i], True, COR_TEXTO)
            texto = Estado.fonte.render(inputs_txt[i] or CARACTERE_CURSOR, True, cor)

            tela.blit(label, (INPUT_X, INPUT_Y_POSICOES[i] - 40))
            tela.blit(texto, (INPUT_X, INPUT_Y_POSICOES[i]))

            if i == campo_atual:
                area = texto.get_rect(topleft=(INPUT_X, INPUT_Y_POSICOES[i]))
                pygame.draw.rect(tela, COR_DESTAQUE, area.inflate(10, 10), 2)

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_RETURN, pygame.K_TAB):
                    campo_atual = (campo_atual + 1) % N_INPUTS
                    pygame.display.set_caption(INPUT_TITULOS[campo_atual])

                    if evento.key == pygame.K_RETURN and all(txt.isdigit() and int(txt) > 0 for txt in inputs_txt):
                        return int(inputs_txt[0]), int(inputs_txt[1])

                elif evento.key == pygame.K_BACKSPACE:
                    inputs_txt[campo_atual] = inputs_txt[campo_atual][:-1]

                elif evento.unicode.isdigit():
                    inputs_txt[campo_atual] += evento.unicode


def proximo_valor_atual(valor, sentido):
    if valor not in VALIDAS:
        return VALIDAS[0]
    i = VALIDAS.index(valor)
    return VALIDAS[(i + sentido) % len(VALIDAS)]


def desenhar_celula(posicao, tamanho, cor_borda):
    linha, coluna = posicao
    celula = Estado.cenario[linha][coluna]
    area = pygame.Rect(coluna * tamanho, linha * tamanho, tamanho, tamanho)

    pygame.draw.rect(Estado.tela, CORES_CELULA[Celula.VAZIA], area)

    if celula != Celula.VAZIA:
        Estado.tela.blit(Estado.imagens_dict[celula], area.topleft)

    pygame.draw.rect(Estado.tela, cor_borda, area, 2)


def desenhar_grid(tamanho, selecao):
    Estado.tela.fill(COR_FUNDO)

    for linha in range(len(Estado.cenario)):
        for coluna in range(len(Estado.cenario[0])):
            cor = COR_DESTAQUE if selecao == (linha, coluna) else COR_GRADE
            desenhar_celula((linha, coluna), tamanho, cor)

    pygame.display.flip()


def mover_selecao(tamanho, anterior, nova):
    a_linha, a_coluna = anterior
    n_linha, n_coluna = nova

    desenhar_celula((a_linha, a_coluna), tamanho, COR_GRADE)
    desenhar_celula((n_linha, n_coluna), tamanho, COR_DESTAQUE)
    pygame.display.flip()


def obter_cenario_gui():
    linhas, colunas = input_linhas_colunas_tela()

    tamanho = max(MIN_TAMANHO_CELULA, LARGURA_TELA // colunas)
    Estado.imagens_dict = carregar_imagens(tamanho)

    altura = linhas * tamanho
    Estado.tela = pygame.display.set_mode((LARGURA_TELA, altura))
    pygame.display.set_caption(TITULO_TELA_CENARIO)

    Estado.cenario = [['_'] * colunas for _ in range(linhas)]
    sel_linha = sel_coluna = 0
    clock = pygame.time.Clock()

    while True:
        desenhar_grid(tamanho, (sel_linha, sel_coluna))

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                key = e.key

                if key == pygame.K_SPACE:
                    print("Cenário final:")
                    for linha in Estado.cenario:
                        print(repr(linha))
                    return Estado.cenario

                movimento = {
                    pygame.K_w: (-1, 0),
                    pygame.K_s: (1, 0),
                    pygame.K_a: (0, -1),
                    pygame.K_d: (0, 1),
                }

                if key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    atual = Estado.cenario[sel_linha][sel_coluna]
                    sentido = 1 if key in (pygame.K_RIGHT, pygame.K_UP) else -1
                    Estado.cenario[sel_linha][sel_coluna] = proximo_valor_atual(atual, sentido)

                elif key in movimento:
                    d_linha, d_coluna = movimento[key]
                    sel_linha += d_linha
                    sel_coluna += d_coluna

            elif e.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                nova_coluna = x // tamanho
                nova_linha = y // tamanho
                sel_linha, sel_coluna = nova_linha, nova_coluna

            elif e.type == pygame.MOUSEWHEEL:
                atual = Estado.cenario[sel_linha][sel_coluna]
                sentido = 1 if e.y > 0 else -1
                Estado.cenario[sel_linha][sel_coluna] = proximo_valor_atual(atual, sentido)

        clock.tick(FPS)
