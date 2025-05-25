import heapq
import math
from collections import namedtuple
import pygame
import os

# Estado de uma casa: aberto ou fechado
class OPERACAO:
    CASA_ABERTA = 'A'
    CASA_FECHADA = 'F'

# Tipos de casas no cenário
class Celula:
    VAZIA = '_'
    PERSONAGEM = 'C'
    SAIDA = 'S'
    BARREIRA = 'B' # Pode pular se tiver fruta
    SEMI_BARREIRA = 'A' # Pode ser pulada
    FRUTA = 'F'

    VALIDAS = {VAZIA, PERSONAGEM, SAIDA, BARREIRA, SEMI_BARREIRA, FRUTA}

PosicaoComContexto = namedtuple('PosicaoComContexto', 'x y celula pai')

# Uma posição no cenário
class Casa:
    __slots__ = ('posicao', 'f', 'g', 'h', 'tem_fruta')

    def __init__(self, posicao, f, g, h, tem_fruta):
        self.posicao = posicao
        self.f = f # Caminho total até a saída 
        self.g = g # Caminho percorrido até o momento
        self.h = h # Caminho em linha reta estimado até a saída
        self.tem_fruta = tem_fruta

    def __lt__(self, other):
        return self.f < other.f

# Tabuleiro completo em que o personagem vai se movimentar para achar a saída
class Cenario:
    __slots__ = ['saida_posicao', 'personagem_posicao', 'matriz_cenario', 'largura', 'altura']

    DIRECOES = [(dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0)]

    def __init__(self, matriz_cenario):
        self.saida_posicao = None
        self.personagem_posicao = None
        self.matriz_cenario = matriz_cenario
        self.largura = len(matriz_cenario[0])
        self.altura = len(matriz_cenario)
        self.localizar_personagem_e_saida()

    # Verificar qual o tipo da casa atual (vazia, barreira, personagem, fruta, saída)
    def obter_celula(self, x, y):
        fora_do_cenario = not (0 <= x < self.largura and 0 <= y < self.altura)
        return None if fora_do_cenario else self.matriz_cenario[y][x]

    # Encontrar os caminhos vizinhos dipoíveis para o personagem andar
    def obter_coordenadas_vizinhas(self, x, y):
        return [
            (x + dx, y + dy)
            for dx, dy in Cenario.DIRECOES
            if self.obter_celula(x + dx, y + dy) is not None
        ]

    # Encontrar coordenadas do personagem e saída
    def localizar_personagem_e_saida(self):
        for x in range(self.largura):
            for y in range(self.altura):
                if self.obter_celula(x, y) == Celula.PERSONAGEM:
                    self.personagem_posicao = {'x': x, 'y': y}
                elif self.obter_celula(x, y) == Celula.SAIDA:
                    self.saida_posicao = {'x': x, 'y': y}

# Lógica principal do algoritmo A*
class EstadoDaProcura:
    __slots__ = ['casas_abertas', 'casas_fechadas', 'menores_f', 'personagem', 'saida', "historico"]

    def __init__(self, casa_inicial, saida):
        self.casas_abertas = [] # Caminhos que precisam ser explorados
        heapq.heappush(self.casas_abertas, (casa_inicial.f, casa_inicial))
        self.casas_fechadas = set() # Caminhos já percorridos pelo personagem
        self.menores_f = {(casa_inicial.posicao.x, casa_inicial.posicao.y): casa_inicial.f}
        self.personagem = casa_inicial
        self.saida = saida
        self.historico = [] # Armazenar menor caminho encontrado 

    # Encontrar casa com menor caminho da lista de caminhos para explorar usando fila de prioridade
    def buscar_proximo(self):
        while self.casas_abertas:
            _, casa = heapq.heappop(self.casas_abertas)
            if (casa.posicao.x, casa.posicao.y) in self.casas_fechadas:
                continue
            self.casas_fechadas.add((casa.posicao.x, casa.posicao.y))
            self.historico.append((casa, OPERACAO.CASA_FECHADA))
            self.personagem = casa
            return casa
        return None

    # Verificar se o personagem chegou na saída
    def achou_saida(self):
        return self.personagem.posicao.x == self.saida.x and self.personagem.posicao.y == self.saida.y

    # Personagem achou a saída
    def pegar_saida(self):
        return self.personagem if self.personagem.posicao.celula == Celula.SAIDA else None

    # Pegar uma casa no cenário já explorada
    def casa_fechada(self, posicao_vizinha):
        return (posicao_vizinha.x, posicao_vizinha.y) in self.casas_fechadas

    # Casa encontrada pode ser um novo caminho para ser percorrido
    def registrar_casa_aberta(self, casa):
        chave = (casa.posicao.x, casa.posicao.y)
        f_existente = self.menores_f.get(chave, None)
        if not f_existente or casa.f < f_existente:
            self.menores_f[chave] = casa.f
            heapq.heappush(self.casas_abertas, (casa.f, casa))
            self.historico.append((casa, OPERACAO.CASA_ABERTA))


# Função heurística, caminho total percorrido pelo personagem até a saída
def calcular_fe(g, h):
    return g + h


# Distância percorrida até o momento
def calcular_g(casa_pai, posicao_vizinha):
    andou_reto = casa_pai.posicao.x == posicao_vizinha.x or casa_pai.posicao.y == posicao_vizinha.y
    tem_barreira = posicao_vizinha.celula in (Celula.BARREIRA, Celula.SEMI_BARREIRA)
    dist = 1 if andou_reto else 1.4 # Andou na diagonal
    if tem_barreira:
        dist += 1 # Andou reto
    return casa_pai.g + dist


# Distância em linha reta para o final usando pitágoras
def calcular_h(casa_atual, casa_saida):
    base = casa_saida.x - casa_atual.x
    altura = casa_saida.y - casa_atual.y
    return round(math.hypot(base, altura), 1)

# Verificar se a casa vizinha é valida
def validar_casa(posicao_vizinha, estado_da_procura):
    if posicao_vizinha.celula not in Celula.VALIDAS:
        return False

    barreira_impassavel = posicao_vizinha.celula == Celula.BARREIRA and not posicao_vizinha.pai.tem_fruta
    if estado_da_procura.casa_fechada(posicao_vizinha) or barreira_impassavel:
        return False

    return True

# Criar personagem e saída
def inicializar_estado_da_procura(cenario):
    if not cenario.personagem_posicao or not cenario.saida_posicao:
        return None

    personagem_pos = PosicaoComContexto(cenario.personagem_posicao['x'], cenario.personagem_posicao['y'],
                                        Celula.PERSONAGEM, None)
    saida = PosicaoComContexto(cenario.saida_posicao['x'], cenario.saida_posicao['y'], Celula.SAIDA, None)
    personagem_h = calcular_h(personagem_pos, saida)
    personagem = Casa(personagem_pos, personagem_h, personagem_h, personagem_h, False)

    return EstadoDaProcura(personagem, saida)

# Iniciar algoritmo A*
def achar_caminho(cenario):

    # Personagem e saída sendo criados para inicar a procuta
    estado_da_procura = inicializar_estado_da_procura(cenario)
    if estado_da_procura is None:
        return []

    # Percorrer casas encontradas durantre o caminho
    while estado_da_procura.casas_abertas:
        personagem = estado_da_procura.buscar_proximo() # Personagem andou uma casa (a que tem menor fe)
        if estado_da_procura.achou_saida():
            break

        # Encontrar e preencher valores das casas vizinhas que o personagem pode andar
        for x, y in cenario.obter_coordenadas_vizinhas(personagem.posicao.x, personagem.posicao.y):
            posicao_vizinha = PosicaoComContexto(x, y, cenario.obter_celula(x, y), personagem)

            if not validar_casa(posicao_vizinha, estado_da_procura):
                continue

            g = calcular_g(personagem, posicao_vizinha)
            h = calcular_h(posicao_vizinha, estado_da_procura.saida)
            f = calcular_fe(g, h)
            tem_fruta = ((personagem.tem_fruta and posicao_vizinha.celula != Celula.BARREIRA)
                         or posicao_vizinha.celula == Celula.FRUTA)
            casa_vizinha = Casa(posicao_vizinha, f, g, h, tem_fruta)

            # Nova casa adicionada para ser explorada
            estado_da_procura.registrar_casa_aberta(casa_vizinha) 

    # Reconstruir menor caminho encontrado do início até a saída
    caminho_resultante = []
    atual = estado_da_procura.pegar_saida()

    while atual is not None:
        caminho_resultante.append({'x': atual.posicao.x, 'y': atual.posicao.y})
        atual = atual.posicao.pai

    return list(reversed(caminho_resultante)), estado_da_procura.historico

# Exibir menor caminho encontrado
def mostrar_menor_caminho_console(caminho):
    if not caminho:
        print('Não foi achado um caminho!')
        return

    caminho_formatado = [f'[x:{casa["x"]}, y:{casa["y"]}]' for casa in caminho]
    print('===============\nMelhor caminho: ')
    print(' -> '.join(caminho_formatado))


# ===============================
# A* GUI
# ===============================

TAMANHO_CELULA = 64

CORES_CELULA = {
    '_': (255, 255, 255),   # Branco
    'C': (0, 0, 255),       # Azul
    'S': (0, 255, 0),       # Verde
    'B': (0, 0, 0),         # Preto
    'A': (128, 128, 128),   # Cinza
    'F': (255, 165, 0),     # Laranja
    'FECHADO': (255, 0, 0, 100),       # Vermelho transparente
    'ABERTO': (0, 255, 0, 100),        # Verde transparente
    'MENOR_CAMINHO': (0, 0, 255, 100), # Azul transparente
    'FONTE': (0, 0, 0),     
    'GRADE': (0, 0, 0)      
}

class Interface:

    def __init__(self, cenario):

        # Configurações iniciais da interface
        pygame.init()
        self.cenario = cenario
        self.largura = cenario.largura * TAMANHO_CELULA
        self.altura = cenario.altura * TAMANHO_CELULA
        self.interface = pygame.display.set_mode((self.largura, self.altura))
        pygame.display.set_caption("Algoritmo A* em game 2D")
        self.interface.fill(CORES_CELULA['_'])
        self.fonte = pygame.font.SysFont('Arial', 16)

        self.imagens = self.carregar_imagens()

    # Exibe os valores da distancia percorrida (g), distância em linha reta (h) e distância total percorrida/heurística (f)
    def exibir_valores_celula(self, casa):
        cor_fonte = CORES_CELULA['FONTE']
        pos_x = casa.posicao.x * TAMANHO_CELULA
        pos_y = casa.posicao.y * TAMANHO_CELULA

        # Tratar casas decimais do texto
        texto_g = self.fonte.render(f"g: {casa.g:.1f}", True, cor_fonte)
        texto_h = self.fonte.render(f"h: {casa.h:.1f}", True, cor_fonte)
        texto_f = self.fonte.render(f"f: {casa.f:.1f}", True, cor_fonte)

        self.interface.blit(texto_g, (pos_x + 2, pos_y + 2))  
        self.interface.blit(texto_h, (pos_x + 2, pos_y + TAMANHO_CELULA // 2 - 8)) 
        self.interface.blit(texto_f, (pos_x + 2, pos_y + TAMANHO_CELULA - 18))  

    # CArregas todas as imagens necessárias para o jogo
    def carregar_imagens(self):
        return {
            'C': self.buscar_imagem_para_celula('img/frames/pixil-frame-0.png'),
            'S': self.buscar_imagem_para_celula('img/saida.png'),
            'B': self.buscar_imagem_para_celula('img/barreira.png'),
            'A': self.buscar_imagem_para_celula('img/semi_barreira.png'),
            'F': self.buscar_imagem_para_celula('img/fruta.png'),
            'FRAMES': self.carregar_frames_personagem('img/frames/'),
            'FRAMES_COM_FRUTA': self.carregar_frames_personagem('img/frames_com_fruta/')
        }
    
    # Redimensionar tamanho da imagem 
    def buscar_imagem_para_celula(self, caminho):
        if not os.path.exists(caminho):
            return None
        imagem = pygame.image.load(caminho)
        imagem = pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))
        return imagem

    # Retornar frames do personagem, caso não encontrar usar a imagem padrão
    def carregar_frames_personagem(self, pasta):
        frames = []
        numero = 1
        while True:
            caminho = os.path.join(pasta, f'pixil-frame-{numero}.png')
            if not os.path.exists(caminho):
                break
            imagem = pygame.image.load(caminho)
            imagem = pygame.transform.scale(imagem, (TAMANHO_CELULA, TAMANHO_CELULA))
            frames.append(imagem)
            numero += 1
        return frames if frames else [self.imagens['C']]
    
    # Desenhar uma célula (quadradinho) na interface usando imagens, se não encontrar usa cores
    def desenhar_celula(self, x, y, celula, frame=None):
        area = pygame.Rect(x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA)
        posicao = (x * TAMANHO_CELULA, y * TAMANHO_CELULA)

        if celula == 'FRAMES' and frame:
            self.interface.blit(frame, posicao)
        elif celula in self.imagens and self.imagens[celula]:
            self.interface.blit(self.imagens[celula], posicao)
        else:
            pygame.draw.rect(self.interface, CORES_CELULA.get(celula, (255, 0, 255)), area)

        pygame.draw.rect(self.interface, CORES_CELULA['GRADE'], area, 1)  # Grade para dividir as células

    # Desennhar cor transparente para não sobrepor as imagens
    def desenhar_cor_transparente(self, x, y, cor_transparente):
        sobreposicao = pygame.Surface((TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
        posicao = (x * TAMANHO_CELULA, y * TAMANHO_CELULA)
        sobreposicao.fill(cor_transparente)
        self.interface.blit(sobreposicao, posicao)

    # Transformar cenário em formato de matriz em uma interface gráfica
    def criar_interface_cenario(self):
        for y in range(self.cenario.altura):
            for x in range(self.cenario.largura):
                celula = self.cenario.obter_celula(x, y) # Valor da célula na matriz do cenário
                self.desenhar_celula(x, y, celula)

    # Colorir os caminhos já percorridos pelo personagem
    def executar_aestrela(self, historico, OPERACAO):
        for casa, tipo_op in historico:
            x, y = casa.posicao.x, casa.posicao.y

            # Redesenhar célula de fundo para ajudar na sobreposição 
            tipo_celula = self.cenario.obter_celula(x, y)
            self.desenhar_celula(x, y, tipo_celula)

            if tipo_op == OPERACAO.CASA_ABERTA:
                self.desenhar_cor_transparente(x, y, CORES_CELULA['ABERTO'])
            elif tipo_op == OPERACAO.CASA_FECHADA:
                self.desenhar_cor_transparente(x, y, CORES_CELULA['FECHADO'])

            self.exibir_valores_celula(casa)
            pygame.display.flip()
            pygame.time.delay(200)

    # Desenhar o menor caminho encontrado pelo personagem
    def mostrar_menor_caminho_interface(self, caminho):
        for casa in caminho:
            x, y = casa['x'], casa['y']
            self.desenhar_cor_transparente(x, y, CORES_CELULA['MENOR_CAMINHO'])
            pygame.display.flip()
            pygame.time.delay(100)

    # Mostrar personagem andando pelo menor caminho encontrado -> apagar posição anterior e desenhar na posição atual
    def mover_personagem(self, caminho):
        personagem_posicao_anterior = caminho[0]
        pegou_fruta = False

        for posicao in caminho:
            x, y = posicao['x'], posicao['y']
            x_anterior, y_anterior = personagem_posicao_anterior['x'], personagem_posicao_anterior['y']

            celula_anterior = self.cenario.obter_celula(x_anterior, y_anterior)
            if celula_anterior == 'C': # Limpar imagem do personagem na posição onde ele está no cenário 
                self.desenhar_celula(x_anterior, y_anterior, '_')
            elif celula_anterior == 'F': # Personagem pegou fruta, tirar ela da interface
                self.desenhar_celula(x_anterior, y_anterior, '_') 
                pegou_fruta = True
            elif celula_anterior == 'B' and pegou_fruta:
                pegou_fruta = False
                self.desenhar_celula(x_anterior, y_anterior, 'B')
            else:
                self.desenhar_celula(x_anterior, y_anterior, celula_anterior)

            frames = self.imagens['FRAMES_COM_FRUTA'] if pegou_fruta else self.imagens['FRAMES']

            for frame in frames:
                celula_atual = self.cenario.obter_celula(x, y)
                self.desenhar_celula(x, y, celula_atual) # Limpar frame anterior do gif
                self.desenhar_celula(x, y, 'FRAMES', frame)

                pygame.display.flip()
                pygame.time.delay(200)

            personagem_posicao_anterior = posicao

    # Iniciar interface mostrando visualmente o funcionamento do A*
    def iniciar(self, historico, caminho, OPERACAO):
        self.interface.fill(CORES_CELULA['_'])
        self.criar_interface_cenario()
        pygame.display.flip()

        manter_tela_aberta = True
        while manter_tela_aberta:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    manter_tela_aberta = False

                
                # Animação de procura do menor caminho
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                    self.interface.fill(CORES_CELULA['_'])  
                    self.criar_interface_cenario()

                    self.executar_aestrela(historico, OPERACAO) 
                    self.mostrar_menor_caminho_interface(caminho)
                    
                    self.interface.fill(CORES_CELULA['_'])  
                    self.criar_interface_cenario()
                    self.mover_personagem(caminho)

        pygame.quit()


# Cenário 6x6 de exemplo
def obter_cenario():
    return Cenario([
        ['C', '_', '_', '_', 'B', '_'],
        ['_', 'B', '_', '_', '_', '_'],
        ['_', '_', 'F', '_', '_', '_'],
        ['_', '_', '_', 'B', 'B', '_'],
        ['_', '_', '_', 'A', '_', '_'],
        ['_', '_', '_', '_', '_', 'S'],
    ])

        # Teste para passar pela barreira
        #['C', '_', 'F', 'B', '_', '_'],
        #['B', 'B', 'B', 'B', 'B', '_'],
        #['B', 'B', 'B', 'B', 'B', '_'],
        #['B', 'B', 'B', 'B', 'B', 'A'],
        #['B', 'B', 'B', 'A', 'B', '_'],
        #['B', 'B', 'B', 'B', 'B', 'S'],


def main():
    cenario = obter_cenario()
    if not cenario.personagem_posicao or not cenario.saida_posicao:
        print('Erro! Sem personagem ou sem saída!')
    caminho, historico = achar_caminho(cenario)
    mostrar_menor_caminho_console(caminho)

    interface = Interface(cenario)
    interface.iniciar(historico, caminho, OPERACAO)


if __name__ == '__main__':
    main()
