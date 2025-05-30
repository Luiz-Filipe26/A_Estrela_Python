from enum import Enum, auto
from typing import Optional

import pygame
from pygame.font import Font

from src.constantes import Celula, TAMANHO_CELULA, TEMPO_ENTRE_ETAPAS_MS, FPS, TITULO, FONTE_NOME, \
    FONTE_TAMANHO, INSTRUCOES, Cores, CORES_CELULA
from src.recursos import carregar_imagens

IMAGENS = carregar_imagens(TAMANHO_CELULA)


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
    tamanho_tela_atual = None


# Controla o tempo de espera entre as etapas
def esperar_proxima_acao():
    while Estado.tempo_acumulado < TEMPO_ENTRE_ETAPAS_MS:
        delta_ms = Estado.clock.tick(FPS)
        Estado.tempo_acumulado += delta_ms

    Estado.tempo_acumulado = 0


def exibir_buffer(buffer):
    largura, altura = buffer.get_size()

    altura_extra = 60

    # Cria um novo buffer com espaço extra no topo
    buffer_completo = pygame.Surface((largura, altura + altura_extra))

    buffer_completo.fill(Cores.BRANCO, pygame.Rect(0, 0, largura, altura_extra))

    # Mostrar texto
    fonte = pygame.font.SysFont(None, 24)
    for i, texto in enumerate(INSTRUCOES):
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
                if Estado.esperando_proximo_passo:
                    Estado.esperando_proximo_passo = False
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
        pygame.draw.rect(buffer, CORES_CELULA[celula], area_celula)

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

    for casa in Estado.caminho:
        posicao_atual = cenario.obter_posicao_com_contexto(casa.posicao.x, casa.posicao.y)
        desenhar_celula(buffer, posicao_atual)
        desenhar_cor_transparente(buffer, casa, CORES_CELULA['CAMINHO_FINAL'])
        exibir_valores_celula(buffer, casa)
        exibir_buffer(buffer)


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

    for casa_atual, casa_posterior in zip(caminho, caminho[1:]):
        posicao = (
            casa_posterior.posicao.x * TAMANHO_CELULA,
            casa_posterior.posicao.y * TAMANHO_CELULA
        )

        # Mudar aparência do personagem para indicar que ele pegou a fruta + tirar fruta da tela
        if not casa_atual.tem_fruta:
            frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM']
        elif casa_atual.posicao.celula == Celula.FRUTA:
            posicao_fruta = casa_atual.posicao._replace(celula=Celula.VAZIA)
            desenhar_celula(cenario_fundo, posicao_fruta)
            desenhar_cor_transparente(cenario_fundo, casa_atual, CORES_CELULA['CAMINHO_FINAL'])
            frames_animacao = IMAGENS['ANIMACAO_PERSONAGEM_FRUTA']

        tempo_passado = 0
        tempo_espera = TEMPO_ENTRE_ETAPAS_MS * len(frames_animacao)

        # Animar o personagem
        for frame in frames_animacao:
            tempo_local = 0
            while tempo_local < TEMPO_ENTRE_ETAPAS_MS:
                tick = Estado.clock.tick(FPS)
                tempo_local += tick
                tempo_passado += tick

                progresso = tempo_passado / tempo_espera
                progresso = min(progresso, 1.0)

                x1, y1 = casa_atual.posicao.x * TAMANHO_CELULA, casa_atual.posicao.y * TAMANHO_CELULA
                x2, y2 = casa_posterior.posicao.x * TAMANHO_CELULA, casa_posterior.posicao.y * TAMANHO_CELULA
                x_interpolado = x1 + (x2 - x1) * progresso
                y_interpolado = y1 + (y2 - y1) * progresso

                buffer.blit(cenario_fundo, (0, 0))
                buffer.blit(frame, (x_interpolado, y_interpolado))
                exibir_buffer(buffer)
                ouvir_eventos(True)

    # Exibir o personagem parado na última posição
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
