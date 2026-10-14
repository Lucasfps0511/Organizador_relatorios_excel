import unicodedata
import pandas as pd
from pathlib import Path

PREPOSICOES = ["de", "da", "do", "das", "dos"]
CATEGORIAS = {"eletronicos": "Eletrônicos", "acessorios": "Acessórios"}

raiz_projeto = Path(__file__).resolve().parent.parent # diretório raiz do projeto; 
planilha = raiz_projeto / "data" / "vendas_baguncadas.xlsx" # caminho da planilha de vendas baguncadas;

def main():
    df = pd.read_excel(planilha) # lê a planilha de vendas baguncadas; #df = dataframe, que é uma estrutura de dados em pandas que representa uma planilha de dados;
    print("\nIniciando o organizador de relatórios Excel...")
    df = padronizar_textos(df)
    print(f"\n\nConferindo se os textos das colunas 'Produto' e 'Categoria' estão padronizados: \n\n {df['Produto'].value_counts()}\n\n{df['Categoria'].value_counts()}")
    df = limpar_precos(df)
    print(f"\n\nConferindo se os preços das colunas 'Preço' estão limpos: \n\n {df['Preço'].dtype}")
    print(f"\n\n Coluna 'preço' no geral: \n{df['Preço']}")
    df = padronizar_datas(df)
    print(f"\n\n Conferindo as datas da coluna 'Data': {df['Data']}")
    print(f"\n Qual o tipo? {df['Data'].dtype}. Quantos valores ausentes? {df['Data'].isna().sum()}")
    print(f"\n\n Quais são os valores únicos da coluna vendedor? {df["Vendedor"].unique()}")



def padronizar_textos(df):

    '''Padroniza os textos das colunas "Produto" e "Categoria";
    Em "Produto", remove espaços sobrando e coloca a inicial de cada palavra em maiúscula, mantendo preposições (de, da, do, das, dos) em minúsculas, com a função capitalizar;
    Em "Categoria", ignora acentos, maiúsculas e espaços para reconhecer o nome e o troca pelo nome oficial do dicionário CATEGORIAS, com a função padronizar_categoria; categorias desconhecidas são apenas capitalizadas;
    Valores ausentes (NaN) são mantidos como estão;
    Args:
        df (pandas.DataFrame): O dataframe contendo as colunas "Produto" e "Categoria";
    Returns:
        pandas.DataFrame: Uma cópia do dataframe com os textos padronizados;
    '''
    df = df.copy()
    df["Produto"] = df["Produto"].map(capitalizar) #Aplica a função capitalizar em cada valor da coluna;
    df["Categoria"] = df["Categoria"].map(padronizar_categoria) #Aplica a função padronizar_categoria em cada valor da coluna;
    return df


def capitalizar(texto):
    
    '''Converte para maiúscula a inicial de cada palavra do texto, mantendo as preposições (de, da, do, das, dos) em minúsculas, exceto quando forem a primeira palavra;
    Também remove espaços em branco sobrando no início, no fim e entre as palavras;
    Args:
        texto (str): O texto a ser capitalizado; valores que não são texto (como NaN) são devolvidos sem alteração;
    Returns:
        str: O texto capitalizado;
    '''
    if not isinstance(texto, str): # Verifica se o valor não é texto (ex: NaN, que é um float);
        return texto # Devolve o valor como veio, evitando erro ao tentar usar métodos de texto nele;
    palavras = texto.split() # Quebra o texto em uma lista de palavras; o split() sem argumento também descarta os espaços sobrando;
    resultado = [] # Cria uma lista vazia para guardar as palavras já formatadas;
    for i, palavra in enumerate(palavras): # Percorre as palavras; o enumerate entrega o índice (i) junto com a palavra;
        if palavra.lower() in PREPOSICOES and i > 0: # Se a palavra, em minúsculas, é uma preposição e não é a primeira do texto;
            resultado.append(palavra.lower()) # Guarda a palavra em minúsculas;
        else: # Caso contrário (palavra comum ou primeira palavra do texto);
            resultado.append(palavra.capitalize()) # Guarda a palavra com a inicial maiúscula e o resto em minúsculas;
    return " ".join(resultado) # Junta as palavras da lista em um único texto, separadas por um espaço;




def remover_acentos(texto):
      if not isinstance(texto, str): # Verifica se o valor não é texto (ex: NaN, que é um float);
            return texto # Devolve o valor como veio, evitando erro ao tentar usar métodos de texto nele;
      texto_sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii") #Primeiro separa letras dos acentos ("ô" vira "o^"), depois descarta o que não é ASCII (os acentos) e por fim transforma ASCII em texto de novo
      return texto_sem_acentos


def padronizar_vendedores(df):
    df = df.copy()


def padronizar_categoria(texto):
    if not isinstance(texto, str): # Verifica se o valor não é texto (ex: NaN, que é um float);
        return texto # Devolve o valor como veio, evitando erro ao tentar usar métodos de texto nele;
    chave = remover_acentos(texto).strip().lower() # A palavra sem acento, sem espaços e em minúsculo;
    return CATEGORIAS.get(chave, capitalizar(texto)) # Retorna o valor da chave no dicionário; o segundo argumento é um "valor de reserva", usado quando a chave não existe no dicionário, então uma categoria não casdastrada sai formatada




def limpar_precos(df):

    '''Limpa os preços das colunas 'Preço' removendo os símbolos de moeda e convertendo para o tipo numérico;
    Args:
        df (pandas.DataFrame): O dataframe contendo a coluna 'Preço';
    Returns:
        pandas.DataFrame: O dataframe com os preços limpos;
    '''
    df = df.copy()
    df["Preço"] = df["Preço"].astype(str) #transforma a coluna 'Preço' em uma string;
    df["Preço"] = df["Preço"].str.replace("R$", "", regex=False).str.strip()
    tem_virgula = df["Preço"].str.contains(",", regex=False) #devolve uma Series (coluna) de True se contém vírgula e False se não 
    df.loc[tem_virgula, "Preço"] = df.loc[tem_virgula, "Preço"].str.replace(".", "", regex=False) #Nas linhas que tem vírgula, na coluna preço, coloque os valore atuais sem pontos
    df["Preço"] = df["Preço"].str.replace(",", ".", regex=False)
    df["Preço"] = pd.to_numeric(df["Preço"], errors="coerce") #Converte a coluna 'Preço' para o tipo numérico, tratando valores inválidos como NaN;
    return df


def padronizar_datas(df):
    
    '''Converte a coluna 'Data' de texto para o tipo datetime, aceitando formatos mistos (ex: 03/02/2026 e 05/11/26);
    As datas são interpretadas como dia/mês/ano e valores inválidos são convertidos para NaT;
    Args:
        df (pandas.DataFrame): O dataframe contendo a coluna 'Data';
    Returns:
        pandas.DataFrame: O dataframe com a coluna 'Data' convertida para datetime;
    '''

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"], format="mixed", dayfirst=True, errors="coerce")
    return df

if __name__ == "__main__":
    main()


#TODO:
#Implementar separação de Vendedor e UF (nome capitalizado + UF em maiúsculas);
#Tratar valores ausentes (Categoria via dicionário Produto → Categoria; Vendedor como "Não informado");
#Remover duplicatas exatas (drop_duplicates, sem remover linhas que só têm vendedor diferente);
#Criar coluna Total (Quantidade * Preço);
#Validar dados (quantidade e preço maiores que zero) e avisar no console;
#Salvar a planilha limpa em data/saida/ com to_excel;
#Escrever testes para cada função nova em tests/test_main.py;
#(opcional) Formatar o arquivo final com openpyxl: largura das colunas, moeda e data;


