#   Referências
#
#   Python Classes https://docs.python.org/3/tutorial/classes.html
#   Python built in functions https://docs.python.org/3/library/functions.html#open (arquivos)
#   Python std types https://docs.python.org/3/library/stdtypes.html
#   Trie https://en.wikipedia.org/wiki/Trie
#   LZ78 https://pt.wikipedia.org/wiki/LZ78#Exemplo

import sys

class Node_trie():

    #construtor
    def __init__(self, codigo = int, prefixo = str, filho = {}):  
        self.codigo = codigo #para output do LZ78 {código: prefixo}
        self.prefixo = prefixo
        self.filho = filho

    #função que identifica se filho do nó tem c
    def procura_char(self, c):
        if c in self.filho:
            return True
        else:
            return False    
        
#Função de compactação LZ78, (arquivo a ser compactado, nome do arquivo de saída)
def compactar(arquivo_1,arquivo_2):

    #quantidade de bytes para usar na compactação
    qtd_bytes_codigo = 3
    qtd_bytes_char = 1
    maior_char = 0

    if arquivo_2 == "":
        arquivo_2 = arquivo_1.split('.',1)[0] + ".z78"
    else:
        arquivo_2 = arquivo_2

    #Analisa arquivo, cria output, escreve em binário na saída
    with open(arquivo_1, 'r', encoding='utf-8') as entrada, open(arquivo_2, "bw") as saida:     

        root = Node_trie()
        root.codigo = 0
        root.prefixo = ""

        no_atual = root

        cadeia = ""
        iterador = 0 

        output_codigo = []
        output_char = []

        for char in entrada.read():

            cadeia = cadeia + char 

            if(no_atual.procura_char(char)): 
                no_atual = no_atual.filho[char]

            else:
                output_codigo.append(no_atual.codigo)
                output_char.append(char)

                #Quantidade de bytes necessárias para representar o prefixo em {código: prefixo}
                #se existir 1 letra do alfabeto fora do ASCII, 1 byte, (0,255), armazenamento em formato UNICODE UTF-8 2 bytes, (0, (2^16)-1), e assim por diante
                if(int(ord(char)) > maior_char):
                    maior_char = int(ord(char))      

                iterador += 1

                no_atual.filho[char] = Node_trie(iterador, cadeia, {})

                #reseta pro início da árvore {0:''} 
                no_atual = root 
                cadeia = ""

        if(maior_char > 255):
            qtd_bytes_char = 2
        elif(maior_char >= pow(2,16)):
            qtd_bytes_char = 3
        elif(maior_char >= pow(2,24)):
            qtd_bytes_char = 4  
        elif(maior_char >= pow(2,32)):
            qtd_bytes_char = 5  

        #Quantidade de bytes necessárias para representar o código em {código: prefixo}
        if iterador < pow(2,8):
            qtd_bytes_codigo = 1
        elif iterador < pow(2,16):
            qtd_bytes_codigo = 2
        elif iterador < pow(2,24): #suficiente para arquivos de até 2MB
            qtd_bytes_codigo = 3
        elif iterador < pow(2,32): #arquivos maiores que 2MB
            qtd_bytes_codigo = 4
        elif iterador < pow(2,40): 
            qtd_bytes_codigo = 5
        elif iterador >= pow(2,48): 
            qtd_bytes_codigo = 6
        elif iterador >= pow(2,56): 
            qtd_bytes_codigo = 7
        elif iterador >= pow(2,64): 
            qtd_bytes_codigo = 8

        #Primeiros 2 bytes reservados para formato de escrita em bytes do {código: prefixo}
        saida.write(qtd_bytes_codigo.to_bytes(1, 'little', signed=False))
        saida.write(qtd_bytes_char.to_bytes(1, 'little', signed=False))

        index = 0

        for i in output_codigo:

            saida.write(i.to_bytes(qtd_bytes_codigo, 'little', signed=False))
            saida.write(int(ord(output_char[index])).to_bytes(qtd_bytes_char, 'little', signed=False))
            
            index += 1

        #se terminar com cadeia não vazia, adiciona +1 cadeia
        if cadeia != "":
            saida.write(no_atual.codigo.to_bytes(qtd_bytes_codigo, 'little', signed=False))
            saida.write(int(0).to_bytes(qtd_bytes_char, 'little', signed=False))
                

#Função de descompactação LZ78, (arquivo a ser descompactado, nome do arquivo de saída)
def descompactar(arquivo_1,arquivo_2):

    if arquivo_2 == "":
        arquivo_2 = arquivo_1.split('.', 1)[0] + ".txt"
    else:
        arquivo_2 = arquivo_2

    qtd_bytes_codigo_bin = 1
    qtd_bytes_codigo = 1
    qtd_bytes_char_bin = 1
    qtd_bytes_char = 1

    with open(arquivo_1, 'rb') as entrada, open(arquivo_2, "w") as saida:

        codigo_bin = 1
        array_string = [''] 

        #leitura dos 2 bytes reservados para representação de {código: prefixo}
        qtd_bytes_codigo_bin = entrada.read(1)
        qtd_bytes_codigo = int.from_bytes(qtd_bytes_codigo_bin, 'little')
        qtd_bytes_char_bin = entrada.read(1)
        qtd_bytes_char = int.from_bytes(qtd_bytes_char_bin, 'little')

        while codigo_bin:

            codigo_bin = entrada.read(qtd_bytes_codigo)
            char_bin = entrada.read(qtd_bytes_char)
        
            codigo = int.from_bytes(codigo_bin, 'little')

            #transformação bin -> int -> char (Unicode)
            char = chr(int.from_bytes(char_bin, 'little'))

            #adiciona prefixo ao final do array e escreve na saída
            array_string.append(array_string[codigo] + char)
            saida.write(array_string[codigo] + char)


#Parâmetros
parametros = len(sys.argv)

if(sys.argv[1] == '-c'):
    if(parametros > 3):
        if(sys.argv[3] == '-o'):
            compactar(sys.argv[2], sys.argv[4])
    else:
        compactar(sys.argv[2], '')

elif(sys.argv[1] == '-x'):
    if(parametros > 3):
        if(sys.argv[3] == '-o'):
            descompactar(sys.argv[2], sys.argv[4])
    else:
        descompactar(sys.argv[2], '')

else:
    print("Parametros de entrada: -c <arquivo_entrada> / compressão")
    print("                     : -x <arquivo_entrada> / descompressão")
    print("                     : -o <arquivo_saida> / opcional")