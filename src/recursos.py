import os

import pygame

from src.constantes import CAMINHO_PASTA_IMG, NOME_PADRAO_FRAME_ANIMACAO, Celula


# Verificar se as imagens existem e já redimensionar para o tamanho correto
def buscar_imagem_para_celula(nome_arquivo, tamanho, subpasta=''):
    caminho_imagem = os.path.join(CAMINHO_PASTA_IMG, subpasta, nome_arquivo)
    if not os.path.exists(caminho_imagem):
        return None
    imagem = pygame.image.load(caminho_imagem)
    return pygame.transform.scale(imagem, (tamanho, tamanho))


# Pegar todas as imagens usadas para a animação/gif do personagem
def carregar_frames_animacao(subpasta, tamanho):
    frames = []
    numero = 0
    while True:
        imagem = buscar_imagem_para_celula(f'{NOME_PADRAO_FRAME_ANIMACAO}{numero}.png', tamanho, subpasta)
        if not imagem:
            return frames
        frames.append(imagem)
        numero += 1


def carregar_imagens(tamanho):
    # Imagens usadas para o jogo
    return {
        Celula.PERSONAGEM: buscar_imagem_para_celula('personagem.png', tamanho),
        Celula.SAIDA: buscar_imagem_para_celula('saida.png', tamanho),
        Celula.BARREIRA: buscar_imagem_para_celula('barreira.png', tamanho),
        Celula.SEMI_BARREIRA: buscar_imagem_para_celula('semi_barreira.png', tamanho),
        Celula.FRUTA: buscar_imagem_para_celula('fruta.png', tamanho),
        'ANIMACAO_PERSONAGEM': carregar_frames_animacao('frames', tamanho),
        'ANIMACAO_PERSONAGEM_FRUTA': carregar_frames_animacao('frames_com_fruta', tamanho)
    }
