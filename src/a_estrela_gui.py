import pygame
import os

from src.a_estrela import OPERACAO, Celula, Casa, PosicaoComContexto

TAMANHO_CELULA = 64


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
    Celula.PERSONAGEM: Cores.AZUL,
    Celula.SAIDA: Cores.VERDE,
    Celula.BARREIRA: Cores.PRETO,
    Celula.SEMI_BARREIRA: Cores.CINZA,
    Celula.FRUTA: Cores.LARANJA,
    OPERACAO.CASA_FECHADA: Cores.VERMELHO_TRANSPARENTE,
    OPERACAO.CASA_ABERTA: Cores.VERDE_TRANSPARENTE,
    'CAMINHO_FINAL': Cores.AZUL_TRANSPARENTE,
    'FONTE': Cores.FONTE,
}

CAMINHO_ABSOLUTO_DO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PASTA_IMG = os.path.join(CAMINHO_ABSOLUTO_DO_SCRIPT, '..', 'img')


def buscar_imagem_para_celula(nome_arquivo):
    caminho_imagem = os.path.join(CAMINHO_PASTA_IMG, nome_arquivo)
    if not os.path.exists(caminho_imagem):
        return None
    imagem = pygame.image.load(caminho_imagem)
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


IMAGENS = {
    Celula.PERSONAGEM: buscar_imagem_para_celula('personagem.png'),
    Celula.SAIDA: buscar_imagem_para_celula('saida.png'),
    Celula.BARREIRA: buscar_imagem_para_celula('barreira.png'),
    Celula.SEMI_BARREIRA: buscar_imagem_para_celula('semi_barreira.png'),
    Celula.FRUTA: buscar_imagem_para_celula('fruta.png')
}


def desenhar_celula(interface, posicao):
    x, y, celula = posicao.x, posicao.y, posicao.celula
    area_celula = pygame.Rect(x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
    pos_pixel = (x * TAMANHO_CELULA, y * TAMANHO_CELULA)

    if celula in IMAGENS and IMAGENS[celula]:
        interface.blit(IMAGENS[celula], pos_pixel)
    else:
        cor = CORES_CELULA[celula]
        pygame.draw.rect(interface, cor, area_celula)

    pygame.draw.rect(interface, Cores.PRETO, area_celula, 1)


def desenhar_cor_transparente(interface, casa, cor_rgba):
    x, y = casa.posicao.x, casa.posicao.y
    sobreposicao = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    sobreposicao.fill(cor_rgba)
    interface.blit(sobreposicao, (x * TAMANHO_CELULA, y * TAMANHO_CELULA))


def exibir_valores_celula(interface, casa, fonte):
    cor_fonte = CORES_CELULA['FONTE']
    x, y = casa.posicao.x, casa.posicao.y

    pos_x = x * TAMANHO_CELULA
    pos_y = y * TAMANHO_CELULA

    texto_g = fonte.render(f"g: {casa.g:.1f}", True, cor_fonte)
    texto_h = fonte.render(f"h: {casa.h:.1f}", True, cor_fonte)
    texto_f = fonte.render(f"f: {casa.f:.1f}", True, cor_fonte)

    interface.blit(texto_g, (pos_x + 2, pos_y + 2))
    interface.blit(texto_h, (pos_x + 2, pos_y + TAMANHO_CELULA // 2 - 8))
    interface.blit(texto_f, (pos_x + 2, pos_y + TAMANHO_CELULA - 18))


def desenhar_cenario(interface, cenario):
    interface.fill(Cores.BRANCO)
    for y in range(cenario.altura):
        for x in range(cenario.largura):
            tipo = cenario.obter_celula(x, y)
            posicao = PosicaoComContexto(x, y, tipo, None)
            desenhar_celula(interface, posicao)


def iniciar_interface(cenario):
    pygame.init()
    largura = cenario.largura * TAMANHO_CELULA
    altura = cenario.altura * TAMANHO_CELULA
    interface = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Algoritmo A* em game 2D")
    fonte = pygame.font.SysFont('Arial', 16)
    return interface, fonte


def mostrar_menor_caminho_gui(caminho, historico, cenario):
    interface, fonte = iniciar_interface(cenario)
    clock = pygame.time.Clock()
    item_historico_iter = iter(historico)
    mostrar_caminho = False

    desenhar_cenario(interface, cenario)
    pygame.display.flip()

    executando = True
    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False

        if not mostrar_caminho:
            try:
                casa, tipo_operacao = next(item_historico_iter)
                desenhar_cor_transparente(interface, casa, CORES_CELULA[tipo_operacao])
                exibir_valores_celula(interface, casa, fonte)
            except StopIteration:
                mostrar_caminho = True
        else:
            desenhar_cenario(interface, cenario)
            for casa in caminho:
                desenhar_cor_transparente(interface, casa, CORES_CELULA['CAMINHO_FINAL'])

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
