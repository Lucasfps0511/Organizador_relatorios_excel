import pandas as pd

from main import (
    capitalizar,
    remover_acentos,
    padronizar_categoria,
    padronizar_textos,
    limpar_precos,
    padronizar_datas,
    padronizar_vendedores,
    tratar_valores_ausentes
)


# ---------- capitalizar ----------

def test_capitalizar_remove_espacos_e_mantem_preposicao():
    assert capitalizar("  soraya dos anjos ") == "Soraya dos Anjos"

def test_capitalizar_preposicao_no_meio():
    assert capitalizar("fone DE ouvido") == "Fone de Ouvido"

def test_capitalizar_preposicao_em_maiuscula():
    assert capitalizar("soraya DOS anjos") == "Soraya dos Anjos"

def test_capitalizar_preposicao_na_primeira_palavra_fica_maiuscula():
    assert capitalizar("de souza") == "De Souza"

def test_capitalizar_texto_todo_maiusculo():
    assert capitalizar("NOTEBOOK") == "Notebook"

def test_capitalizar_nan_devolve_nan():
    assert pd.isna(capitalizar(float("nan")))


# ---------- remover_acentos ----------

def test_remover_acentos_basico():
    assert remover_acentos("Eletrônicos") == "Eletronicos"

def test_remover_acentos_maiusculas_e_cedilha():
    assert remover_acentos("AÇÃO") == "ACAO"

def test_remover_acentos_texto_sem_acento_nao_muda():
    assert remover_acentos("Mouse") == "Mouse"

def test_remover_acentos_nan_devolve_nan():
    assert pd.isna(remover_acentos(float("nan")))


# ---------- padronizar_categoria ----------

def test_padronizar_categoria_sem_acento_e_com_espacos():
    assert padronizar_categoria("  ELETRONICOS ") == "Eletrônicos"

def test_padronizar_categoria_minuscula():
    assert padronizar_categoria("acessorios") == "Acessórios"

def test_padronizar_categoria_ja_correta():
    assert padronizar_categoria("Acessórios") == "Acessórios"

def test_padronizar_categoria_desconhecida_usa_valor_de_reserva():
    assert padronizar_categoria("periféricos") == "Periféricos"

def test_padronizar_categoria_nan_devolve_nan():
    assert pd.isna(padronizar_categoria(float("nan")))


# ---------- padronizar_textos ----------

def test_padronizar_textos_produto_e_categoria():
    df = pd.DataFrame({
        "Produto": ["  notebook ", "Fone DE ouvido"],
        "Categoria": ["eletronicos", "ACESSORIOS"],
    })
    resultado = padronizar_textos(df)
    assert resultado["Produto"].tolist() == ["Notebook", "Fone de Ouvido"]
    assert resultado["Categoria"].tolist() == ["Eletrônicos", "Acessórios"]

def test_padronizar_textos_mantem_categoria_ausente_como_nan():
    df = pd.DataFrame({"Produto": ["mouse"], "Categoria": [None]})
    resultado = padronizar_textos(df)
    assert pd.isna(resultado["Categoria"].iloc[0])

def test_padronizar_textos_nao_altera_o_dataframe_original():
    df = pd.DataFrame({"Produto": ["  notebook "], "Categoria": ["eletronicos"]})
    padronizar_textos(df)
    assert df["Produto"].iloc[0] == "  notebook "


# ---------- limpar_precos ----------

def test_limpar_precos_formatos_variados():
    df = pd.DataFrame({"Preço": ["R$ 1.234,50", "R$ 50", 3500, 3500.5]})
    resultado = limpar_precos(df)
    assert resultado["Preço"].tolist() == [1234.5, 50.0, 3500.0, 3500.5]

def test_limpar_precos_valor_invalido_vira_nan():
    df = pd.DataFrame({"Preço": ["abc", "R$ 10"]})
    resultado = limpar_precos(df)
    assert pd.isna(resultado["Preço"].iloc[0])
    assert resultado["Preço"].iloc[1] == 10.0

def test_limpar_precos_resultado_e_numerico():
    df = pd.DataFrame({"Preço": ["R$ 50", 80]})
    resultado = limpar_precos(df)
    assert pd.api.types.is_numeric_dtype(resultado["Preço"])

def test_limpar_precos_nao_altera_o_dataframe_original():
    df = pd.DataFrame({"Preço": ["R$ 50"]})
    limpar_precos(df)
    assert df["Preço"].iloc[0] == "R$ 50"


# ---------- padronizar_datas ----------

def test_padronizar_datas_ano_com_quatro_digitos():
    df = pd.DataFrame({"Data": ["03/02/2026"]})
    resultado = padronizar_datas(df)
    assert resultado["Data"].iloc[0] == pd.Timestamp(2026, 2, 3)

def test_padronizar_datas_ano_com_dois_digitos():
    df = pd.DataFrame({"Data": ["05/11/26"]})
    resultado = padronizar_datas(df)
    assert resultado["Data"].iloc[0] == pd.Timestamp(2026, 11, 5)

def test_padronizar_datas_interpreta_como_dia_mes():
    df = pd.DataFrame({"Data": ["07/10/2026"]})
    resultado = padronizar_datas(df)
    assert resultado["Data"].iloc[0].month == 10
    assert resultado["Data"].iloc[0].day == 7

def test_padronizar_datas_invalida_vira_nat():
    df = pd.DataFrame({"Data": ["99/99/2026"]})
    resultado = padronizar_datas(df)
    assert pd.isna(resultado["Data"].iloc[0])

def test_padronizar_datas_resultado_e_datetime():
    df = pd.DataFrame({"Data": ["03/02/2026", "05/11/26"]})
    resultado = padronizar_datas(df)
    assert pd.api.types.is_datetime64_any_dtype(resultado["Data"])

# ---------- padronizar_vendedores ----------

def test_padronizar_vendedores_vendedor_capitaliza_segundo_nome():
    df = pd.DataFrame({
        "Vendedor": ["Francisco sousa (SP)"]
    })
    resultado = padronizar_vendedores(df)
    assert resultado["Vendedor"].iloc[0] == "Francisco Sousa"
    assert resultado["UF"].iloc[0] == "SP"

def test_padronizar_vendedores_capitaliza_nomes_e_uf():
    df = pd.DataFrame({
        "Vendedor": ["célia alves (go)"]
    })
    resultado = padronizar_vendedores(df)
    assert resultado["Vendedor"].iloc[0] == "Célia Alves"
    assert resultado["UF"].iloc[0] == "GO"

def test_padronizar_vendedores_nomes_capitalizados_e_uf_em_maiusculo_mantem_tudo():
    df = pd.DataFrame({
            "Vendedor": ["Soraya dos Anjos (AL)"]
    })
    resultado = padronizar_vendedores(df)
    assert resultado["Vendedor"].iloc[0] == "Soraya dos Anjos"
    assert resultado["UF"].iloc[0] == "AL"

def test_padronizar_vendedores_sem_uf_mantem_nome_e_uf_ausente():
    df = pd.DataFrame({
                "Vendedor": ["Rafael Diniz"]
    }) 
    resultado = padronizar_vendedores(df)
    assert resultado["Vendedor"].iloc[0] == "Rafael Diniz"
    assert pd.isna(resultado["UF"].iloc[0])

def test_padronizar_vendedores_vendedor_ausente_mantem_vendedor_e_uf_ausentes():
    df = pd.DataFrame({
        "Vendedor": ["Francisco sousa (SP)", None] # O texto na primeira linha é o que mantém a coluna como tipo texto. Com isso, o .str da função funciona e o None vira NaN.
        })
    resultado = padronizar_vendedores(df)
    assert pd.isna(resultado["Vendedor"].iloc[1]) # Conferindo Linha 2 (o 1 é o segundo número a partir do 0), Coluna Vendedor
    assert pd.isna(resultado["UF"].iloc[1]) # Conferindo Linha 2 Coluna UF
    assert resultado["Vendedor"].iloc[0] == "Francisco Sousa" # Assegura que a presença do NaN não atrapalhou o processamento da linha normal; sem ele, o teste passaria mesmo se a função falhasse em tudo, desde que retornasse NaN para tudo.

# ---------- tratar_valores_ausentes ----------

def test_tratar_valores_ausentes_produto_valido_sem_categoria_adiciona_categoria_respectiva():
    df = pd.DataFrame({
        "Produto": ["Fone de Ouvido"],
        "Categoria": [None],
        "Vendedor": ["Daniel Toriyama"], # placeholder 
        "UF": ["AC"], # placeholder
    })
    resultado = tratar_valores_ausentes(df)
    assert resultado["Categoria"].iloc[0] == "Acessórios"
    assert resultado["Produto"].iloc[0] == "Fone de Ouvido"
    assert resultado["Vendedor"].iloc[0] == "Daniel Toriyama"
    assert resultado["UF"].iloc[0] == "AC"