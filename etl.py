import pandas as pd
import xmltodict
import os

def tratar_xml(uploaded_files):

    def abrir_arquivo(uploaded_file):
        return xmltodict.parse(uploaded_file)

    def coletar_codigo_jbs(df):
        list = []
        for i,info in enumerate(df['infAdProd']):
            list.append(info.split('Cod. Fabricante: ',)[1].split(' ')[0])
        return list
    
    data = abrir_arquivo(uploaded_files)
    
    det = data['nfeProc']['NFe']['infNFe']['det']
    serie = data['nfeProc']['NFe']['infNFe']['ide']['serie']
    nnf = data['nfeProc']['NFe']['infNFe']['ide']['nNF']
    nfref = data['nfeProc']['NFe']['infNFe']['ide']['NFref']
    emit_cnpj = data['nfeProc']['NFe']['infNFe']['emit']['CNPJ']
    emit_nome = data['nfeProc']['NFe']['infNFe']['emit']['xNome']
    dest_cnpj =  data['nfeProc']['NFe']['infNFe']['dest']['CNPJ']
    dest_nome = data['nfeProc']['NFe']['infNFe']['dest']['xNome']
    infocompl = data['nfeProc']['NFe']['infNFe']['infAdic']['infCpl']

    df = pd.json_normalize(det, sep='.')
    novas_colunas = ['Série', 'NF', 'Emitente CNPJ', 'Emitente Nome', 'Destinatátio CNPJ', 'Destinatário Nome', 'Informações Complementares']
    dados_novas_colunas= [serie, nnf, emit_cnpj, emit_nome, dest_cnpj, dest_nome, infocompl]

    for i,coluna in enumerate(novas_colunas):
        df[coluna] = dados_novas_colunas[i]

    colunas = novas_colunas + [col for col in df.columns if col not in novas_colunas]
    df = df[colunas]
    df.dropna(axis='columns', how='all')

    df['Código JBS'] = coletar_codigo_jbs(df)    

    df = df[['Série', 'NF', 'Emitente Nome', 'Emitente CNPJ',
       'Destinatário Nome', 'Destinatátio CNPJ', 'Informações Complementares','Código JBS', 'prod.xProd','prod.uCom', 'prod.qCom', 'prod.vUnCom', 'prod.vProd']]

    return df

def concatenar_df(uploaded_files):

    todos_df = []

    for uploaded_file in uploaded_files:
        df = tratar_xml(uploaded_file.read())
        todos_df.append(df)

    list_str = ['Emitente Nome', 'Emitente CNPJ', 'Destinatário Nome', 'Destinatátio CNPJ', 'Informações Complementares', 'prod.xProd', 'prod.uCom']
    list_int = ['Série', 'NF', 'Código JBS', ]
    list_float = ['prod.qCom', 'prod.vUnCom', 'prod.vProd']

    df_tratado = pd.concat(todos_df, ignore_index=True)

    for coluna in list_str:
        df_tratado[coluna] = df_tratado[coluna].astype('str')
    for coluna in list_float:
        df_tratado[coluna] = df_tratado[coluna].astype('float64')
    for coluna in list_int:
        df_tratado[coluna] = df_tratado[coluna].astype('int64')
    
    return df_tratado
    