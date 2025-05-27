import heapq
import math
from collections import namedtuple


# Estado de uma casa: aberto ou fechado
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


PosicaoComContexto = namedtuple('PosicaoComContexto', 'x y celula pai')


# Uma posição no cenário
class Casa:
    __slots__ = ('posicao', 'f', 'g', 'h', 'tem_fruta')

    def __init__(self, posicao, f, g, h, tem_fruta):
        self.posicao = posicao
        self.f = f  # Caminho total até a saída
        self.g = g  # Caminho percorrido até o momento
        self.h = h  # Caminho em linha reta estimado até a saída
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

    def obter_posicao_com_contexto(self, x, y):
        tipo = self.obter_celula(x, y)
        return PosicaoComContexto(x, y, tipo, None)

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

    def __iter__(self):
        for y in range(self.altura):
            for x in range(self.largura):
                yield self.obter_posicao_com_contexto(x, y)


# Lógica principal do algoritmo A*
class EstadoDaProcura:
    __slots__ = ['casas_abertas', 'casas_fechadas', 'menores_f', 'personagem', 'saida', "historico"]

    def __init__(self, casa_inicial, saida):
        self.casas_abertas = []  # Caminhos que precisam ser explorados
        heapq.heappush(self.casas_abertas, (casa_inicial.f, casa_inicial))
        self.casas_fechadas = set()  # Caminhos já percorridos pelo personagem
        self.menores_f = {(casa_inicial.posicao.x, casa_inicial.posicao.y): casa_inicial.f}
        self.personagem = casa_inicial
        self.saida = saida
        self.historico = []  # Armazenar menor caminho encontrado

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
    dist = 1 if andou_reto else 1.4  # Andou reto ou diagonal
    if tem_barreira:
        dist += 1  # Criar lentidão de 1 via heurística
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
        personagem = estado_da_procura.buscar_proximo()  # Personagem andou uma casa (a que tem menor fe)
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
        caminho_resultante.append(atual)
        atual = atual.posicao.pai

    return list(reversed(caminho_resultante)), estado_da_procura.historico


# Exibir menor caminho encontrado
def mostrar_menor_caminho_console(caminho):
    if not caminho:
        print('Não foi achado um caminho!')
        return

    caminho_formatado = [f'[x:{casa.posicao.x}, y:{casa.posicao.y}]' for casa in caminho]
    print('===============\nMelhor caminho: ')
    print(' -> '.join(caminho_formatado))


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


def main():
    cenario = obter_cenario()
    if not cenario.personagem_posicao or not cenario.saida_posicao:
        print('Erro! Sem personagem ou sem saída!')
    caminho, historico = achar_caminho(cenario)
    mostrar_menor_caminho_console(caminho)
    from src.a_estrela_gui import mostrar_menor_caminho_gui
    mostrar_menor_caminho_gui(caminho, historico, cenario)


if __name__ == '__main__':
    main()
