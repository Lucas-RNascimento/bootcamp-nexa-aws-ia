import json #permite manipular os dados no formato JSON
from pathlib import Path #usada para manipular caminhos de arquivos e diretórios

import boto3 #Importa o SDK boto3, usado para interagir com os serviços da AWS.
from botocore.exceptions import ClientError #mporta a classe ClientError, que é utilizada para lidar com erros durante chamadas aos serviços da AWS

from mypy_boto3_textract.type_defs import DetectDocumentTextResponseTypeDef


def detect_file_text() -> None:
    client = boto3.client("textract") #Cria um cliente para o serviço Textract da AWS.

    file_path = str(Path(__file__).parent / "images" / "lista-material-2.jpg") #Constrói o caminho completo para o arquivo de imagem
    with open(file_path, "rb") as f:
        document_bytes = f.read() #Abre o arquivo de imagem no modo binário ("rb") e lê seus bytes para serem enviados ao Textract.

    try:
        response = client.detect_document_text(Document={"Bytes": document_bytes}) #Faz uma chamada ao Textract para detectar texto no documento fornecido. Os bytes da imagem são enviados no campo Document
        with open("response.json", "w") as response_file:
            response_file.write(json.dumps(response)) #Salva a resposta JSON em um arquivo chamado response.json.
    except ClientError as e:
        print(f"Erro processando documento: {e}")


def get_lines() -> list[str]: #Responsável por obter as linhas de texto do arquivo de resposta response.json
    try:
        with open("response.json", "r") as f:
            data: DetectDocumentTextResponseTypeDef = json.loads(f.read())
            blocks = data["Blocks"]
        return [block["Text"] for block in blocks if block["BlockType"] == "LINE"]  # A resposta do Textract contém um conjunto de "blocos" de dados. Cada bloco pode ser do tipo "LINE" (linha de texto), "WORD" (palavra), etc. 
    #Apenas os blocos do tipo "LINE" são selecionados, e os textos correspondentes a esses blocos são retornados em uma lista.
    except IOError:
        detect_file_text()
    return []


if __name__ == "__main__":
    for line in get_lines(): #Itera pelas linhas de texto obtidas pela função
        print(line) #Imprime cada linha de texto no console.