import os
from enum import Enum, auto
from typing import Optional

import pygame
from pygame.font import Font

from src.a_estrela import OPERACAO, Celula

# Informações globais para a interface
TAMANHO_CELULA = 64
FPS = 30
FONTE_NOME = 'Arial'
FONTE_TAMANHO = 16
TITULO = "Algoritmo A* em game 2D"

TEMPO_ENTRE_ETAPAS_MS = 300


# Definir estados principais do algoritmo
class Etapas(Enum):
    PROCURANDO_CAMINHO = auto()
    MOSTRANDO_CAMINHO = auto()
    ESPERANDO = auto()


# Informações para controle do jogo
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
    buffer_tela = None
    tamanho_janela = None


# Cores para representar os elementos da interface
class Cores:
    BRANCO = (255, 255, 255)  # Casa vazia
    AZUL = (0, 0, 255)
    VERDE = (0, 255, 0)
    PRETO = (0, 0, 0)
    CINZA = (128, 128, 128)
    LARANJA = (255, 165, 0)
    VERMELHO_TRANSPARENTE = (255, 0, 0, 100)
    VERDE_TRANSPARENTE = (0, 255, 0, 100)
    AZUL_TRANSPARENTE = (0, 0, 255, 100)
    FONTE = PRETO


# Relacionar células/elementos com as cores
CORES_CELULA = {
    Celula.VAZIA: Cores.BRANCO,
    Celula.PERSONAGEM: Cores.AZUL,
    Celula.SAIDA: Cores.VERDE,
    Celula.FRUTA: Cores.LARANJA,
    Celula.BARREIRA: Cores.PRETO,
    Celula.SEMI_BARREIRA: Cores.CINZA,
    OPERACAO.CASA_FECHADA: Cores.VERMELHO_TRANSPARENTE,
    OPERACAO.CASA_ABERTA: Cores.VERDE_TRANSPARENTE,
    'CAMINHO_FINAL': Cores.AZUL_TRANSPARENTE,
    'FONTE': Cores.FONTE,
}

# Informações para localizar imagens do jogo
CAMINHO_ABSOLUTO_DO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PASTA_IMG = os.path.join(CAMINHO_ABSOLUTO_DO_SCRIPT, '..', 'img')
NOME_PADRAO_FRAME_ANIMACAO = 'pixil-frame-'


# Verificar se as imagens existem e já redimensionar para o tamanho correto
def buscar_imagem_para_celula(nome_arquivo, subpasta=''):
    caminho_imagem = os.path.join(CAMINHO_PASTA_IMG, subpasta, nome_arquivo)
    if not os.path.exists(caminho_imagem):
        return None
    imagem = pygame.image.load(caminho_imagem)
    return pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))


# Pegar todas as imagens usadas para a animação/gif do personagem
def carregar_frames_animacao(subpasta):
    frames = []
    numero = 0
    while True:
        imagem = buscar_imagem_para_celula(f'{NOME_PADRAO_FRAME_ANIMACAO}{numero}.png', subpasta)
        if not imagem:
            return frames
        frames.append(imagem)
        numero += 1


# Imagens usadas para o jogo
IMAGENS = {
    Celula.PERSONAGEM: buscar_imagem_para_celula('personagem.png'),
    Celula.SAIDA: buscar_imagem_para_celula('saida.png'),
    Celula.BARREIRA: buscar_imagem_para_celula('barreira.png'),
    Celula.SEMI_BARREIRA: buscar_imagem_para_celula('semi_barreira.png'),
    Celula.FRUTA: buscar_imagem_para_celula('fruta.png'),
    'ANIMACAO_PERSONAGEM': carregar_frames_animacao('frames'),
    'ANIMACAO_PERSONAGEM_FRUTA': carregar_frames_animacao('frames_com_fruta')
}


# Controla o tempo de espera entre as etapas
def esperar_proxima_acao():
    while Estado.tempo_acumulado < TEMPO_ENTRE_ETAPAS_MS:
        delta_ms = Estado.clock.tick(FPS)
        Estado.tempo_acumulado += delta_ms

    Estado.tempo_acumulado = 0


instrucoes = [
    "Pressione ESC para sair.",
    "Aperte espaço para ir para próxima etapa.",
    "Aperte m para usar modo de micro-etapas."
]


def exibir_buffer(buffer):
    # Dimensões do buffer original
    largura, altura = buffer.get_size()

    # Altura extra para instruções (ex: 60px)
    altura_extra = 60

    # Cria um novo buffer com espaço extra no topo
    buffer_completo = pygame.Surface((largura, altura + altura_extra))

    # Preenche o topo com fundo preto (ou outra cor, se preferir)
    buffer_completo.fill(Cores.BRANCO, pygame.Rect(0, 0, largura, altura_extra))

    # Renderiza as instruções
    fonte = pygame.font.SysFont(None, 24)
    for i, texto in enumerate(instrucoes):
        img_texto = fonte.render(texto, True, Cores.PRETO)
        buffer_completo.blit(img_texto, (10, i * 20))

    # Copia o buffer principal abaixo das instruções
    buffer_completo.blit(buffer, (0, altura_extra))

    # Exibe na tela principal redimensionando para caber
    Estado.tela.blit(pygame.transform.scale(buffer_completo, Estado.tela.get_size()), (0, 0))
    pygame.display.flip()


# Exibir os valores da distância percorrida (g), distância em linha reta (h) e distância total percorrida/heurística (f)
def exibir_valores_celula(buffer, casa):
    cor_fonte = CORES_CELULA['FONTE']
    x, y = casa.posicao.x, casa.posicao.y

    pos_x = x * TAMANHO_CELULA
    pos_y = y * TAMANHO_CELULA

    texto_g = Estado.fonte.render(f"g: {casa.g:.1f}", True, cor_fonte)
    texto_h = Estado.fonte.render(f"h: {casa.h:.1f}", True, cor_fonte)
    texto_f = Estado.fonte.render(f"f: {casa.f:.1f}", True, cor_fonte)

    buffer.blit(texto_g, (pos_x + 2, pos_y + 2))
    buffer.blit(texto_h, (pos_x + 2, pos_y + TAMANHO_CELULA // 2 - 8))
    buffer.blit(texto_f, (pos_x + 2, pos_y + TAMANHO_CELULA - 18))


# Definir como o jogo transita de uma etapa para outra
transicoes_etapas = {
    Etapas.ESPERANDO: (Etapas.PROCURANDO_CAMINHO,
                       lambda: animar_busca(Estado.buffer_tela, Estado.cenario, Estado.historico)),
    Etapas.PROCURANDO_CAMINHO: (Etapas.MOSTRANDO_CAMINHO,
                                lambda: desenhar_caminho_final(Estado.buffer_tela, Estado.cenario, Estado.caminho)),
    Etapas.MOSTRANDO_CAMINHO: (Etapas.ESPERANDO, lambda: desenhar_cenario(Estado.buffer_tela, Estado.cenario)),
}


# Pegar a próxima etapa do jogo e o que fazer nessa etapa
def executar_proxima_etapa():
    Estado.etapa_atual, acao = transicoes_etapas[Estado.etapa_atual]
    acao()


# Esperando interação do usuário para iniciar o jogo
def ouvir_eventos(processando_etapa=True):
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()

        if evento.type == pygame.VIDEORESIZE:
            Estado.tamanho_tela_atual = evento.size
            exibir_buffer(Estado.buffer_tela)
        # Espaço executa o algoritmo e "m" altera o modo: executar passo a passo ou não
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


# Desenhar uma célula/quadradinho da interface usando imagens, se não tiver, usa a cor correspondente
def desenhar_celula(buffer, posicao):
    x, y, celula = posicao.x, posicao.y, posicao.celula
    area_celula = pygame.Rect(x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
    pos_pixel = (x * TAMANHO_CELULA, y * TAMANHO_CELULA)

    pygame.draw.rect(buffer, CORES_CELULA[Celula.VAZIA], area_celula)

    if celula in IMAGENS and IMAGENS[celula]:
        buffer.blit(IMAGENS[celula], pos_pixel)
    else:
        pygame.draw.rect(buffer, CORES_CELULA.get(celula), area_celula)

    pygame.draw.rect(buffer, Cores.PRETO, area_celula, 1)  # Grade para dividir as células


# Desennar cor transparente para não sobrepor as imagens
def desenhar_cor_transparente(buffer, casa, cor_rgba):
    x, y = casa.posicao.x, casa.posicao.y
    sobreposicao = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
    sobreposicao.fill(cor_rgba)
    buffer.blit(sobreposicao, (x * TAMANHO_CELULA, y * TAMANHO_CELULA))


# Animação de buscar o caminho, colorindo as células/quadradinhos e verificando modo escolhido pelo usuário
def animar_busca(buffer, cenario, historico):
    desenhar_cenario(buffer, cenario)

    for casa, tipo_operacao in historico:
        if Estado.passo_a_passo:
            Estado.esperando_proximo_passo = True
        else:
            ouvir_eventos()

        while Estado.esperando_proximo_passo:
            ouvir_eventos()

        posicao_atual = cenario.obter_posicao_com_contexto(casa.posicao.x, casa.posicao.y)
        desenhar_celula(buffer, posicao_atual)
        desenhar_cor_transparente(buffer, casa, CORES_CELULA[tipo_operacao])
        exibir_valores_celula(buffer, casa)
        exibir_buffer(buffer)

        if not Estado.passo_a_passo:
            esperar_proxima_acao()


# Desenhar a animação do personagem percorrendo o menor caminho encontrado pelo algoritmo
def desenhar_caminho_final(buffer, cenario, caminho):
    cenario_fundo = pygame.Surface((buffer.get_width(), buffer.get_height()))
    desenhar_cenario(cenario_fundo, cenario)

    # Correção visual para o personagem não ficar na posição inicial depois de começar a andar
    posicao_personagem = caminho[0].posicao._replace(celula=Celula.VAZIA)
    desenhar_celula(cenario_fundo, posicao_personagem)

    for casa in caminho:
        desenhar_cor_transparente(cenario_fundo, casa, CORES_CELULA['CAMINHO_FINAL'])

    exibir_buffer(buffer)

    frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM']
    posicao = None

    for casa in caminho:
        posicao = (casa.posicao.x * TAMANHO_CELULA, casa.posicao.y * TAMANHO_CELULA)

        # Mudar aparência do personagem para indicar que ele pegou a fruta + tirar fruta da tela
        if not casa.tem_fruta:
            frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM']
        elif casa.posicao.celula == Celula.FRUTA:
            posicao_fruta = casa.posicao._replace(celula=Celula.VAZIA)
            desenhar_celula(cenario_fundo, posicao_fruta)
            desenhar_cor_transparente(cenario_fundo, casa, CORES_CELULA['CAMINHO_FINAL'])
            frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM_FRUTA']

        # Animar o personagem
        for frame in frames_animacao:
            buffer.blit(cenario_fundo, (0, 0))
            buffer.blit(frame, posicao)
            exibir_buffer(buffer)
            esperar_proxima_acao()
            ouvir_eventos(True)

    buffer.blit(cenario_fundo, (0, 0))
    buffer.blit(frames_animacao[0], posicao)
    exibir_buffer(buffer)
    esperar_proxima_acao()


# Desenhar interface completa e seus elementos
def desenhar_cenario(buffer, cenario):
    buffer.fill(Cores.BRANCO)
    for posicao in cenario:
        desenhar_celula(buffer, posicao)
    exibir_buffer(buffer)


# Iniciar interface gráfica com base na matriz do cenário
def iniciar_tela(cenario):
    pygame.init()
    largura = cenario.largura * TAMANHO_CELULA
    altura = cenario.altura * TAMANHO_CELULA
    Estado.tamanho_janela = (largura, altura)
    Estado.buffer_tela = pygame.Surface(Estado.tamanho_janela)
    Estado.tela = pygame.display.set_mode(Estado.tamanho_janela, pygame.RESIZABLE)
    pygame.display.set_caption(TITULO)
    Estado.fonte = pygame.font.SysFont(FONTE_NOME, FONTE_TAMANHO)


# Mostrar visualmente algoritmo procurando o menor caminho
def mostrar_menor_caminho_gui(caminho, historico, cenario):
    iniciar_tela(cenario)
    Estado.caminho = caminho
    Estado.historico = historico
    Estado.cenario = cenario

    desenhar_cenario(Estado.buffer_tela, cenario)

    while True:
        ouvir_eventos(False)
        Estado.clock.tick(FPS)
