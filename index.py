import sys
import time
from scipy.spatial.distance import cityblock

# Classe No com 3 atributos: estado, pai e ação
class No():
    def __init__(self, estado, pai, acao, objetivo):
        self.estado = estado
        self.pai = pai
        self.acao = acao
        self.heuristica = cityblock(self.estado, objetivo)
    
    def __repr__(self):
        # return "[estado = " + str(self.estado) + "; pai = " + str(self.pai) + "; acao = " + str(self.acao) + "] "
        return "{ pos = " + str(self.estado) + "; f(n) = " + str(self.calculaCustoAtual()) + " + " + str(self.heuristica) + " = " + str(self.calculaFuncaoAvaliacao()) + " }"

    def calculaCustoAtual(self):
        custo = 0
        no = self
        while no.pai != None:
            custo += 1
            no = no.pai
        return custo

    def calculaFuncaoAvaliacao(self):
        return self.calculaCustoAtual() + self.heuristica
 
# Classe para tratar Nós Fronteira
# Deep First Search (DFS)
class PilhaFronteira():
    # Inicializa Fronteira vazia
    def __init__(self):
        self.fronteira = []

    def __repr__(self):
        # return "<__main__.Pilha: fronteira = " + str(self.fronteira) + ">\n"
        return str(self.fronteira) + "\n"
    
    # Insere na pilha	
    def add(self, no):
        self.fronteira.append(no)

    
    # Procura no pilha por um estado
    def contem_estado(self, estado):
        return any(no.estado == estado for no in self.fronteira)

    # Verifica se Fronteira está vazia
    def empty(self):
        return len(self.fronteira) == 0

    # Remove estado da Fronteira do tipo Pilha
    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            no = self.fronteira[-1]
            self.fronteira = self.fronteira[:-1]
            return no

# Breadth First Search (BFS) herdando métodos da DFS
# Só muda a remoção do nó da fronteira
class FilaFronteira(PilhaFronteira):

    # Remove estado da Fronteira do tipo Fila
    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            no = self.fronteira[0]
            self.fronteira = self.fronteira[1:]
            return no

class AStarFronteira(PilhaFronteira):
    def remove(self):
        if self.empty():
            raise Exception("fronteira vazia")
        else:
            noMenorFuncaoAvaliacao = self.fronteira[0]
            for node in self.fronteira:
                if node.calculaFuncaoAvaliacao() < noMenorFuncaoAvaliacao.calculaFuncaoAvaliacao():
                    noMenorFuncaoAvaliacao = node

            self.fronteira.remove(noMenorFuncaoAvaliacao)
            return noMenorFuncaoAvaliacao

# Classe do Problema de Busca
class Labirinto():

    # Inicializa instância do problema com o arquivo TXT filename
    def __init__(self, filename):

        # Lê arquivo e configura altura e largura do labirinto
        with open(filename) as f:
            contents = f.read()

        # Valida Largada e Chegada
        if contents.count("A") != 1:
            raise Exception("labirinto deve ter exatamente um ponto de partida")
        if contents.count("B") != 1:
            raise Exception("labirinto deve ter exatamente uma chegada")

        # Determina altura e largura do labirinto
        contents = contents.splitlines()
        self.altura = len(contents)
        self.largura = max(len(line) for line in contents)

        # Manter as paredes
        self.paredes = []
        for i in range(self.altura):
            row = []
            for j in range(self.largura):
                try:
                    if contents[i][j] == "A":
                        self.inicio = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.objetivo = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.paredes.append(row)

        self.solucao = None

    # Imprime na tela a solução
    def print(self):
        solucao = self.solucao[1] if self.solucao is not None else None
        print()
        for i, row in enumerate(self.paredes):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.inicio:
                    print("A", end="")
                elif (i, j) == self.objetivo:
                    print("B", end="")
                elif solucao is not None and (i, j) in solucao:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()


    # Identifica os vizinhos do estado 
    def vizinhos(self, estado):
        linha, coluna = estado
        candidatos = [
            ("up", (linha - 1, coluna)),
            ("down", (linha + 1, coluna)),
            ("left", (linha, coluna - 1)),
            ("right", (linha, coluna + 1))
        ]

        resultado = []
        for acao, (l, c) in candidatos:
            if 0 <= l < self.altura and 0 <= c < self.largura and not self.paredes[l][c]:
                resultado.append((acao, (l, c)))
        return resultado


    # Invoca o método solve() para encontrar a solução 
    def solve(self, tipoFronteira):
        """Encontrar uma solução para labirinto, se existe."""

        # Acompanhar o número de estados explorados
        self.num_explored = 0

        # Inicializa a fronteira apenas para o posição inicial
        inicio = No(estado=self.inicio, pai=None, acao=None, objetivo=self.objetivo)
        
        if tipoFronteira == "pilha":
            fronteira = PilhaFronteira()
        elif tipoFronteira == "fila":
            fronteira = FilaFronteira()
        elif tipoFronteira == "a*":
            fronteira = AStarFronteira()
        
        fronteira.add(inicio)

        # Inicializa um conjunto vazio de estados não explorados
        self.explored = set()

        # Mantem laço até encontrar solução
        while True:
            # print(fronteira)
            
            # Se não sobrar nada na fronteira, então não há caminho
            if fronteira.empty():
                raise Exception("sem solução")

            # Escolha um nó da fronteira
            no = fronteira.remove()
            self.num_explored += 1

            # Se o nó é objetivo, então temos uma solução
            if no.estado == self.objetivo:
                self.custoTotal = no.calculaCustoAtual()
                acoes = []
                celulas = []
                while no.pai is not None:
                    acoes.append(no.acao)
                    celulas.append(no.estado)
                    no = no.pai
                acoes.reverse()
                celulas.reverse()
                self.solucao = (acoes, celulas)
                return

            # Marca nó como explorado
            self.explored.add(no.estado)

            # Adiciona vizinhos a fronteira
            for acao, estado in self.vizinhos(no.estado):
                if not fronteira.contem_estado(estado) and estado not in self.explored:
                    filho = No(estado=estado, pai=no, acao=acao, objetivo=self.objetivo)
                    fronteira.add(filho)

    # Imprime o labirinto com os estados explorados
    def output_image(self, filename, show_solution=True, show_explored=False):
        from PIL import Image, ImageDraw
        cell_size = 50
        cell_border = 2

        # Cria uma tela preta
        img = Image.new(
            "RGBA",
            (self.largura * cell_size, self.altura * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solucao = self.solucao[1] if self.solucao is not None else None
        for i, row in enumerate(self.paredes):
            for j, col in enumerate(row):

                # Paredes
                if col:
                    fill = (40, 40, 40)

                # Inicio
                elif (i, j) == self.inicio:
                    fill = (255, 0, 0)

                # Objetivo
                elif (i, j) == self.objetivo:
                    fill = (0, 171, 28)

                # Solução
                elif solucao is not None and show_solution and (i, j) in solucao:
                    fill = (220, 235, 113)

                # Exploroda
                elif solucao is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Celula Vazia
                else:
                    fill = (237, 240, 252)

                # Desenha celula
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


# ----------------------
# Programa Principal 
# ----------------------

def executarTodasAsBuscas(filename):
    imageTag = filename.replace(".txt", "")
    imageTag = imageTag.replace("labs/", "")
    lab = Labirinto(filename)
    print("----------------------------------")
    print("Executando busca em profundidade...")
    executarBusca(lab, ["pilha", "profundidade"], imageTag)
    print("\n----------------------------------")

    print("Executando busca em largura...")
    executarBusca(lab, ["fila", "largura"], imageTag)
    print("\n----------------------------------")

    print("Executando busca informada A*...")
    executarBusca(lab, ["a*", "a-star"], imageTag)
    print("----------------------------------")

def executarBusca(lab, tipoBusca, imageTag):
    t1 = time.time()
    lab.solve(tipoFronteira=tipoBusca[0])
    t2 = time.time()
    tempo_execucao = t2 - t1 
    print("Tempo de Execução: ", tempo_execucao)
    print("Estados Explorados:", lab.num_explored)
    print("Custo total:", lab.custoTotal)
    lab.output_image("images/" + tipoBusca[1] + "-" + imageTag + ".png", show_explored=True)

# executa todas as buscas para o arquivo recebido via linha de comando
# if len(sys.argv) != 2:
#     sys.exit("Uso: python index.py labs/nome_labirinto.txt")

# print("Solucionando...\n")
# filename = sys.argv[1]
# executarTodasAsBuscas(filename)

# executa todas as buscas para os arquivos biglab1 e biglab2
print("Solucionando...\n")

print("Solução para o biglab1.txt:")
executarTodasAsBuscas("biglab1.txt")

print()
print("Solução para o biglab2.txt:")
executarTodasAsBuscas("biglab2.txt")


# print("Labirinto: ")
# m.print()

# print("Solução: ")
# m.print()

