import pandas as pd
import xmltodict
import re


def tratar_xml(uploaded_file):
    """Processa um arquivo XML de NF-e e retorna DataFrame formatado."""

    def abrir_arquivo(file_bytes):
        return xmltodict.parse(file_bytes)
    
    def formatar_cpf_cnpj(valor):
        if not valor:
            return None
        
        # Remove caracteres não numéricos
        numeros = re.sub(r'\D', '', str(valor))
        
        if len(numeros) == 14:  # CNPJ
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
        elif len(numeros) == 11:  # CPF
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        

    def coletar_codigo_jbs(df):
        """Extrai códigos JBS da coluna 'infAdProd'."""
        resultados = []
        padroes = {
            'COD. JBS-': lambda x: x.split('COD. JBS-')[1].split(' ')[0],
            'Equivalente : JBS-': lambda x: x.split('Equivalente : JBS-')[1],
            'Mat:JBS-': lambda x: x.split('Mat:JBS-')[1].split(' ')[0],
            'PRODUTO JBS-': lambda x: x.split('PRODUTO JBS-')[1].split('; ')[0],
            'PROD.CLIENTE: JBS-': lambda x: x.split('PROD.CLIENTE: JBS-')[1].replace(')', ''),
            'Cod. Fabricante: ': lambda x: x.split('Cod. Fabricante: ')[1].split(' ')[0],
            ') Ped.Cliente': lambda x: x.replace('(', '').split(')')[0],
            ' MAT:': lambda x: x.split(' MAT:')[1],
            'Código do cliente: JBS-': lambda x: x.split('Código do cliente: JBS-')[1].split(' -')[0],
        }

        for info in df.get('infAdProd', []):
            encontrado = False
            for padrao, extracao in padroes.items():
                if padrao in str(info):
                    try:
                        resultados.append(extracao(info))
                    except Exception:
                        resultados.append(0)
                    encontrado = True
                    break
            if not encontrado:
                resultados.append(0)  # mantém tamanho consistente

        # Garantir que o tamanho da lista seja igual ao tamanho do DF
        while len(resultados) < len(df):
            resultados.append(0)

        return resultados

    # Lê o XML
    data = abrir_arquivo(uploaded_file)

    # Coleta campos fixos
    ide = data['nfeProc']['NFe']['infNFe']['ide']
    emit = data['nfeProc']['NFe']['infNFe']['emit']
    dest = data['nfeProc']['NFe']['infNFe']['dest']
    infocompl = data['nfeProc']['NFe']['infNFe'].get('infAdic', {}).get('infCpl', None)
    det = data['nfeProc']['NFe']['infNFe']['det']
    df = pd.json_normalize(det, sep='.')

    # Adiciona colunas fixas
    novas_colunas = {
        'Série': ide['serie'],
        'NF': ide['nNF'],
        'Operação': ide['natOp'],
        'Emitente CNPJ': emit.get('CNPJ'),
        'Emitente Nome': emit.get('xNome'),
        'Destinatário CNPJ': dest.get('CNPJ'),
        'Destinatário Nome': dest.get('xNome'),
        'Informações Complementares': infocompl,
    }

    for coluna, valor in novas_colunas.items():
        df[coluna] = valor

    # Reorganiza colunas
    colunas_ordenadas = list(novas_colunas.keys()) + [col for col in df.columns if col not in novas_colunas]
    df = df[colunas_ordenadas]

    # Adiciona Código JBS
    df['Código JBS'] = coletar_codigo_jbs(df) or 0

    # Seleção e renomeação final
    df = df[['Série', 'NF', 'Operação', 'Emitente Nome', 'Emitente CNPJ',
             'Destinatário Nome', 'Destinatário CNPJ', 'Informações Complementares',
             'Código JBS', 'prod.xProd', 'prod.uCom', 'prod.qCom', 'prod.vUnCom', 'prod.vProd']]

    df.columns = ['Série', 'NF', 'Operação', 'Emitente Nome', 'Emitente CNPJ',
                  'Destinatário Nome', 'Destinatário CNPJ', 'Informações Complementares',
                  'Código JBS', 'Produto', 'Unidade de Medida', 'Qtde', 'Valor Unitário', 'Valor Total']
    
    # Conversões de tipos
    df['Emitente CNPJ'] = df['Emitente CNPJ'].apply(formatar_cpf_cnpj)
    df['Destinatário CNPJ'] = df['Destinatário CNPJ'].apply(formatar_cpf_cnpj)
    
    df['Série'] = df['Série'].astype('int', errors='ignore')
    df['NF'] = df['NF'].astype('int', errors='ignore')
    df['Código JBS'] = df['Código JBS'].astype('int', errors='ignore')
    df['Qtde'] = df['Qtde'].astype('float', errors='ignore')
    df['Valor Unitário'] = df['Valor Unitário'].astype('float', errors='ignore')
    

    return df


def concatenar_df(uploaded_files):
    """Concatena múltiplos XMLs processados em um único DataFrame."""
    todos_df = [tratar_xml(uploaded_file.read()) for uploaded_file in uploaded_files]
    df_tratado = pd.concat(todos_df, ignore_index=True)

    return df_tratado
