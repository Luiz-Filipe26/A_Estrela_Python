import os
from enum import Enum, auto
from typing import Optional

import pygame
from pygame.font import Font

from src.a_estrela import OPERACAO, Celula

TAMANHO_CELULA = 64
FPS = 30
FONTE_NOME = 'Arial'
FONTE_TAMANHO = 16
TITULO = "Algoritmo A* em game 2D"

TEMPO_ENTRE_ETAPAS_MS = 300


class Etapas(Enum):
    PROCURANDO_CAMINHO = auto()
    MOSTRANDO_CAMINHO = auto()
    ESPERANDO = auto()


class Estado:
    fonte: Optional[Font] = None
    etapa_atual = Etapas.ESPERANDO
    tela = None
    cenario = None
    historico = None
    caminho = None
    passo_a_passo = False
    esperando_proximo_passo = False
    clock = pygame.time.Clock()
    tempo_acumulado = 0


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
NOME_PADRAO_FRAME_ANIMACAO = 'pixil-frame-'


def buscar_imagem_para_celula(nome_arquivo, subpasta=''):
    caminho_imagem = os.path.join(CAMINHO_PASTA_IMG, subpasta, nome_arquivo)
    if not os.path.exists(caminho_imagem):
        return None
    imagem = pygame.image.load(caminho_imagem)
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


def carregar_frames_animacao(subpasta):
    frames = []
    numero = 0
    while True:
        imagem = buscar_imagem_para_celula(f'{NOME_PADRAO_FRAME_ANIMACAO}{numero}.png', subpasta)
        if not imagem:
            return frames
        frames.append(imagem)
        numero += 1


IMAGENS = {
    Celula.PERSONAGEM: buscar_imagem_para_celula('personagem.png'),
    Celula.SAIDA: buscar_imagem_para_celula('saida.png'),
    Celula.BARREIRA: buscar_imagem_para_celula('barreira.png'),
    Celula.SEMI_BARREIRA: buscar_imagem_para_celula('semi_barreira.png'),
    Celula.FRUTA: buscar_imagem_para_celula('fruta.png'),
    'ANIMACAO_PERSONAGEM': carregar_frames_animacao('frames'),
    'ANIMACAO_PERSONAGEM_FRUTA': carregar_frames_animacao('frames_com_fruta')
}


def esperar_proxima_acao(modo_espera):
    while Estado.tempo_acumulado < TEMPO_ENTRE_ETAPAS_MS:
        delta_ms = Estado.clock.tick(FPS)
        Estado.tempo_acumulado += delta_ms

        if not modo_espera:
            return

    Estado.tempo_acumulado = 0


def exibir_valores_celula(tela, casa):
    cor_fonte = CORES_CELULA['FONTE']
    x, y = casa.posicao.x, casa.posicao.y

    pos_x = x * TAMANHO_CELULA
    pos_y = y * TAMANHO_CELULA

    texto_g = Estado.fonte.render(f"g: {casa.g:.1f}", True, cor_fonte)
    texto_h = Estado.fonte.render(f"h: {casa.h:.1f}", True, cor_fonte)
    texto_f = Estado.fonte.render(f"f: {casa.f:.1f}", True, cor_fonte)

    tela.blit(texto_g, (pos_x + 2, pos_y + 2))
    tela.blit(texto_h, (pos_x + 2, pos_y + TAMANHO_CELULA // 2 - 8))
    tela.blit(texto_f, (pos_x + 2, pos_y + TAMANHO_CELULA - 18))


transicoes_etapas = {
    Etapas.ESPERANDO: (Etapas.PROCURANDO_CAMINHO, lambda: animar_busca(Estado.tela, Estado.cenario, Estado.historico)),
    Etapas.PROCURANDO_CAMINHO: (Etapas.MOSTRANDO_CAMINHO,
                                lambda: desenhar_caminho_final(Estado.tela, Estado.cenario, Estado.caminho)),
    Etapas.MOSTRANDO_CAMINHO: (Etapas.ESPERANDO, lambda: desenhar_cenario(Estado.tela, Estado.cenario)),
}


def executar_proxima_etapa():
    Estado.etapa_atual, acao = transicoes_etapas[Estado.etapa_atual]
    acao()


def ouvir_eventos(processando_etapa=True):
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_m:
                Estado.passo_a_passo = not Estado.passo_a_passo
            if evento.key == pygame.K_SPACE:
                if processando_etapa:
                    Estado.esperando_proximo_passo = False
                else:
                    executar_proxima_etapa()
            if evento.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()


def desenhar_celula(tela, posicao):
    x, y, celula = posicao.x, posicao.y, posicao.celula
    area_celula = pygame.Rect(x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
    pos_pixel = (x * TAMANHO_CELULA, y * TAMANHO_CELULA)

    pygame.draw.rect(tela, CORES_CELULA[Celula.VAZIA], area_celula)

    if celula in IMAGENS and IMAGENS[celula]:
        tela.blit(IMAGENS[celula], pos_pixel)

    pygame.draw.rect(tela, Cores.PRETO, area_celula, 1)


def desenhar_cor_transparente(tela, casa, cor_rgba):
    x, y = casa.posicao.x, casa.posicao.y
    sobreposicao = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    sobreposicao.fill(cor_rgba)
    tela.blit(sobreposicao, (x * TAMANHO_CELULA, y * TAMANHO_CELULA))


def animar_busca(tela, cenario, historico):
    desenhar_cenario(tela, cenario)

    for casa, tipo_operacao in historico:
        if Estado.passo_a_passo:
            Estado.esperando_proximo_passo = True
        else:
            ouvir_eventos()

        while Estado.esperando_proximo_passo:
            ouvir_eventos()
            esperar_proxima_acao(False)

        posicao_atual = cenario.obter_posicao_com_contexto(casa.posicao.x, casa.posicao.y)
        desenhar_celula(tela, posicao_atual)
        desenhar_cor_transparente(tela, casa, CORES_CELULA[tipo_operacao])
        exibir_valores_celula(tela, casa)
        pygame.display.flip()

        if not Estado.passo_a_passo:
            esperar_proxima_acao(True)


def desenhar_caminho_final(tela, cenario, caminho):
    cenario_fundo = pygame.Surface((tela.get_width(), tela.get_height()))
    desenhar_cenario(cenario_fundo, cenario)

    for casa in caminho:
        desenhar_cor_transparente(cenario_fundo, casa, CORES_CELULA['CAMINHO_FINAL'])

    pygame.display.flip()

    frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM']
    posicao = None

    for casa in caminho:
        posicao = (casa.posicao.x * TAMANHO_CELULA, casa.posicao.y * TAMANHO_CELULA)

        if not casa.tem_fruta:
            frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM']
        else:
            if casa.posicao.celula == Celula.FRUTA:
                posicao_fruta = casa.posicao._replace(celula=Celula.VAZIA)
                desenhar_celula(cenario_fundo, posicao_fruta)
                desenhar_cor_transparente(cenario_fundo, casa, CORES_CELULA['CAMINHO_FINAL'])
            frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM_FRUTA']

        for frame in frames_animacao:
            tela.blit(cenario_fundo, (0, 0))
            tela.blit(frame, posicao)
            pygame.display.flip()
            esperar_proxima_acao(True)

    tela.blit(cenario_fundo, (0, 0))
    tela.blit(frames_animacao[0], posicao)
    pygame.display.flip()


def desenhar_cenario(tela, cenario):
    tela.fill(Cores.BRANCO)
    for posicao in cenario:
        desenhar_celula(tela, posicao)
    pygame.display.flip()


def iniciar_tela(cenario):
    pygame.init()
    largura = cenario.largura * TAMANHO_CELULA
    altura = cenario.altura * TAMANHO_CELULA
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption(TITULO)
    Estado.fonte = pygame.font.SysFont(FONTE_NOME, FONTE_TAMANHO)

    return tela


def mostrar_menor_caminho_gui(caminho, historico, cenario):
    tela = iniciar_tela(cenario)
    Estado.tela = tela
    Estado.caminho = caminho
    Estado.historico = historico
    Estado.cenario = cenario

    desenhar_cenario(tela, cenario)

    while True:
        ouvir_eventos(False)
