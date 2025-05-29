# Estado de uma casa: aberto ou fechado
import os


class OPERACAO:
    CASA_ABERTA = 'A'
    CASA_FECHADA = 'F'


# Tipos de casas no cenário
class Celula:
    VAZIA = '_'
    PERSONAGEM = 'C'
    SAIDA = 'S'
    BARREIRA = 'B'  # Pode pular se tiver fruta
    SEMI_BARREIRA = 'A'  # Pode ser pulada
    FRUTA = 'F'

    VALIDAS = {VAZIA, PERSONAGEM, SAIDA, BARREIRA, SEMI_BARREIRA, FRUTA}


CENARIO_PADRAO = [
    ['C', '_', '_', '_', 'B', '_'],
    ['_', 'B', '_', '_', 'F', '_'],
    ['_', '_', 'F', '_', 'F', '_'],
    ['_', '_', '_', 'B', 'B', '_'],
    ['_', '_', '_', 'A', '_', '_'],
    ['_', '_', '_', '_', '_', 'S'],
]

# Informações globais para a interface
TAMANHO_CELULA = 64
FPS = 30
FONTE_NOME = 'Arial'
FONTE_TAMANHO = 16
TITULO = "Algoritmo A* em game 2D"

TEMPO_ENTRE_ETAPAS_MS = 300

INSTRUCOES = [
    "Pressione ESC para sair.",
    "Aperte espaço para próxima etapa.",
    "Aperte m para modo de micro-etapas."
]




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