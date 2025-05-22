import pygame
import os

from src.a_estrela import OPERACAO

TAMANHO_CELULA = 64

CORES_CELULA = {
    '_': (255, 255, 255),  # Branco
    'C': (0, 0, 255),  # Azul
    'S': (0, 255, 0),  # Verde
    'B': (0, 0, 0),  # Preto
    'A': (128, 128, 128),  # Cinza
    'F': (255, 165, 0),  # Laranja
    'FECHADO': (255, 0, 0, 100),  # Vermelho transparente
    'ABERTO': (0, 255, 0, 100),  # Verde transparente
    'MENOR_CAMINHO': (0, 0, 255, 100),  # Azul transparente
    'FONTE': (0, 0, 0)  # Preto
}


# Exibe os valores da distancia percorrida (g), distância em linha reta (h) e distância total percorrida/heurística (f)
def exibir_valores_celula(interface, casa, fonte):
    cor_fonte = CORES_CELULA.get('FONTE')
    pos_x = casa.posicao.x * TAMANHO_CELULA
    pos_y = casa.posicao.y * TAMANHO_CELULA

    # Tratar casas decimais no texto
    texto_g = fonte.render(f"g: {casa.g:.1f}", True, cor_fonte)
    texto_h = fonte.render(f"h: {casa.h:.1f}", True, cor_fonte)
    texto_f = fonte.render(f"f: {casa.f:.1f}", True, cor_fonte)

    # Desenhart textos à esquerda, um em baixo do outro
    interface.blit(texto_g, (pos_x + 2, pos_y + 2))
    interface.blit(texto_h, (pos_x + 2, pos_y + TAMANHO_CELULA // 2 - 8))
    interface.blit(texto_f, (pos_x + 2, pos_y + TAMANHO_CELULA - 18))


# Redimensionar tamanho da imagem
def buscar_imagem_para_celula(url_imagem):
    if not os.path.exists(url_imagem):
        return None
    imagem = pygame.image.load(url_imagem)
    tamanho_imagem = (TAMANHO_CELULA, TAMANHO_CELULA)
    return pygame.transform.scale(imagem, tamanho_imagem),


# Imagens já redimensionadas para usar na interface
IMAGENS = {
    'C': buscar_imagem_para_celula('img/personagem.png'),
    'S': buscar_imagem_para_celula('img/saida.png'),
    'B': buscar_imagem_para_celula('img/barreira.png'),
    'A': buscar_imagem_para_celula('img/semi_barreira.png'),
    'F': buscar_imagem_para_celula('img/fruta.png')
}


# Desenhar uma célula (quadradinho) na interface
def desenhar_celula(interface, x, y, celula):
    area_celula = pygame.Rect(x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
    posicao = (x * TAMANHO_CELULA, y * TAMANHO_CELULA)

    # Usar cor para representar os elementos se não achar a imagem correspondente
    if celula in IMAGENS and IMAGENS[celula]:
        imagem = IMAGENS[celula]
        interface.blit(imagem[0], posicao)
    else:
        cor_elemento = CORES_CELULA[celula]
        pygame.draw.rect(interface, cor_elemento, area_celula)

    pygame.draw.rect(interface, (0, 0, 0), area_celula, 1)  # Grade para dividir as células


# Desennhar cor transparente para não sobrepor as imagens
def desenhar_cor_transparente(interface, x, y, cor_rgba):
    sobreporsicao = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    sobreporsicao.fill(cor_rgba)
    interface.blit(sobreporsicao, (x * TAMANHO_CELULA, y * TAMANHO_CELULA))


# Desenhar interface completa do cenário
def criar_interface(interface, cenario):
    for y in range(cenario.altura):
        for x in range(cenario.largura):
            celula = cenario.obter_celula(x, y)  # Valor da célula na matriz do cenário
            desenhar_celula(interface, x, y, celula)


# Colorir os caminhos já percorridos
def mostrar_procura_aestrela(caminho, historico, interface, cenario, fonte):
    for casa, tipo_op in historico:
        x, y = casa.posicao.x, casa.posicao.y

        # Redesenhar a célula de fundo
        tipo_celula = cenario.obter_celula(x, y)
        desenhar_celula(interface, x, y, tipo_celula)

        # Colorir caminho do personagem com cor transparente
        if tipo_op == OPERACAO.CASA_ABERTA:
            desenhar_cor_transparente(interface, x, y, CORES_CELULA.get('ABERTO'))
        elif tipo_op == OPERACAO.CASA_FECHADA:
            desenhar_cor_transparente(interface, x, y, CORES_CELULA.get('FECHADO'))

            # Exibir valores de f, g e h
        exibir_valores_celula(interface, casa, fonte)

        pygame.display.flip()
        pygame.time.delay(200)

    mostrar_resultado_final(caminho, interface, cenario)


# Desenhar o menor caminho encontrado pelo personagem
def mostrar_resultado_final(caminho, interface, cenario):
    for casa in caminho:
        x, y = casa['x'], casa['y']

        tipo_celula = cenario.obter_celula(x, y)
        desenhar_celula(interface, x, y, tipo_celula)
        desenhar_cor_transparente(interface, x, y, CORES_CELULA.get('MENOR_CAMINHO'))

        pygame.display.flip()
        pygame.time.delay(100)


def iniciar_interface(cenario):
    # Configurações iniciais da interface
    pygame.init()
    largura = cenario.largura * TAMANHO_CELULA
    altura = cenario.altura * TAMANHO_CELULA
    interface = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Algoritmo A* em game 2D")
    interface.fill((255, 255, 255))  # Pintar tudo de branco
    fonte = pygame.font.SysFont('Arial', 16)

    # Criar cenário inicial
    criar_interface(interface, cenario)
    pygame.display.flip()

    return interface, fonte


# Iniciar interface monstreando o A* funcionando
def mostrar_menor_caminho_gui(caminho, historico, cenario):
    interface, fonte = iniciar_interface(cenario)
    # Animação de procura do menor caminho
    mostrar_procura_aestrela(caminho, historico, interface, cenario, fonte)

    # Manter a tela aberta enquanto personagem estiver procurando a saída
    procurando_caminho = True
    while procurando_caminho:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                procurando_caminho = False

    pygame.quit()
