import pygame
import os

from typing import Optional
from pygame.font import Font

from src.a_estrela import OPERACAO, Celula

TAMANHO_CELULA = 64
FPS = 10
FONTE_NOME = 'Arial'
FONTE_TAMANHO = 16
TITULO = "Algoritmo A* em game 2D"
fonte: Optional[Font] = None


class Cores:
    BRANCO = (255, 255, 255)
    AZUL = (0, 0, 255)
    VERDE = (0, 255, 0)
    PRETO = (0, 0, 0)
    CINZA = (128, 128, 128)
    LARANJA = (255, 165, 0)
    VERMELHO_TRANSPARENTE = (255, 0, 0, 100)
    VERDE_TRANSPARENTE = (0, 255, 0, 100)
    AZUL_TRANSPARENTE = (0, 0, 255, 100)
    FONTE = PRETO


CORES_CELULA = {
    Celula.VAZIA: Cores.BRANCO,
    OPERACAO.CASA_FECHADA: Cores.VERMELHO_TRANSPARENTE,
    OPERACAO.CASA_ABERTA: Cores.VERDE_TRANSPARENTE,
    'CAMINHO_FINAL': Cores.AZUL_TRANSPARENTE,
    'FONTE': Cores.FONTE,
}

CAMINHO_ABSOLUTO_DO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PASTA_IMG = os.path.join(CAMINHO_ABSOLUTO_DO_SCRIPT, '..', 'img')


def buscar_imagem_para_celula(nome_arquivo):
    caminho_imagem = os.path.join(CAMINHO_PASTA_IMG, nome_arquivo)
    imagem = pygame.image.load(caminho_imagem)
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


IMAGENS = {
    Celula.PERSONAGEM: buscar_imagem_para_celula('personagem.png'),
    Celula.SAIDA: buscar_imagem_para_celula('saida.png'),
    Celula.BARREIRA: buscar_imagem_para_celula('barreira.png'),
    Celula.SEMI_BARREIRA: buscar_imagem_para_celula('semi_barreira.png'),
    Celula.FRUTA: buscar_imagem_para_celula('fruta.png')
}


def desenhar_celula(tela, posicao):
    x, y, celula = posicao.x, posicao.y, posicao.celula
    area_celula = pygame.Rect(x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
    pos_pixel = (x * TAMANHO_CELULA, y * TAMANHO_CELULA)

    if celula in IMAGENS and IMAGENS[celula]:
        tela.blit(IMAGENS[celula], pos_pixel)
    elif celula == Celula.VAZIA:
        cor = CORES_CELULA[Celula.VAZIA]
        pygame.draw.rect(tela, cor, area_celula)

    pygame.draw.rect(tela, Cores.PRETO, area_celula, 1)


def desenhar_cor_transparente(tela, casa, cor_rgba):
    x, y = casa.posicao.x, casa.posicao.y
    sobreposicao = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    sobreposicao.fill(cor_rgba)
    tela.blit(sobreposicao, (x * TAMANHO_CELULA, y * TAMANHO_CELULA))


def exibir_valores_celula(tela, casa):
    cor_fonte = CORES_CELULA['FONTE']
    x, y = casa.posicao.x, casa.posicao.y

    pos_x = x * TAMANHO_CELULA
    pos_y = y * TAMANHO_CELULA

    global fonte
    texto_g = fonte.render(f"g: {casa.g:.1f}", True, cor_fonte)
    texto_h = fonte.render(f"h: {casa.h:.1f}", True, cor_fonte)
    texto_f = fonte.render(f"f: {casa.f:.1f}", True, cor_fonte)

    tela.blit(texto_g, (pos_x + 2, pos_y + 2))
    tela.blit(texto_h, (pos_x + 2, pos_y + TAMANHO_CELULA // 2 - 8))
    tela.blit(texto_f, (pos_x + 2, pos_y + TAMANHO_CELULA - 18))


def ouvir_eventos():
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()


def animar_busca(tela, cenario, historico):
    clock = pygame.time.Clock()
    desenhar_cenario(tela, cenario)
    for casa, tipo_operacao in historico:
        ouvir_eventos()
        posicao_atual = cenario.obter_posicao_com_contexto(casa.posicao.x, casa.posicao.y)
        desenhar_celula(tela, posicao_atual)
        desenhar_cor_transparente(tela, casa, CORES_CELULA[tipo_operacao])
        exibir_valores_celula(tela, casa)
        pygame.display.flip()
        clock.tick(FPS)


def desenhar_caminho_final(tela, cenario, caminho):
    desenhar_cenario(tela, cenario)
    for casa in caminho:
        desenhar_cor_transparente(tela, casa, CORES_CELULA['CAMINHO_FINAL'])
    pygame.display.flip()


def desenhar_cenario(tela, cenario):
    tela.fill(Cores.BRANCO)
    for posicao in cenario:
        desenhar_celula(tela, posicao)


def iniciar_tela(cenario):
    pygame.init()
    largura = cenario.largura * TAMANHO_CELULA
    altura = cenario.altura * TAMANHO_CELULA
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption(TITULO)
    global fonte
    fonte = pygame.font.SysFont(FONTE_NOME, FONTE_TAMANHO)

    return tela


def mostrar_menor_caminho_gui(caminho, historico, cenario):
    tela = iniciar_tela(cenario)

    animar_busca(tela, cenario, historico)
    desenhar_caminho_final(tela, cenario, caminho)

    while True:
        ouvir_eventos()
