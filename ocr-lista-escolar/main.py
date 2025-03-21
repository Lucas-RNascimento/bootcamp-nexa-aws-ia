import json
import boto3
from botocore.exceptions import ClientError

def detect_file_text_from_s3(bucket_name: str, file_name: str) -> list[str]:
    client = boto3.client("textract")

    # Recupera o documento do S3
    try:
        s3_object = {"S3Object": {"Bucket": bucket_name, "Name": file_name}}
        response = client.detect_document_text(Document=s3_object)

        # Processa os blocos retornados e extrai as linhas de texto
        blocks = response.get("Blocks", [])
        lines = [block["Text"] for block in blocks if block["BlockType"] == "LINE"]
        return lines
    except ClientError as e:
        print(f"Erro ao processar documento do S3: {e}")
        return []


if __name__ == "__main__":
    bucket_name = "bkt-textract-lista-material"
    file_name = "lista-material-2.jpg"

    # Busca e imprime as linhas de texto extraídas
    lines = detect_file_text_from_s3(bucket_name, file_name)
    if lines:
        print("Linhas extraídas do documento:")
        for line in lines:
            print(line)
        
        # Criando um dictionary para formatar a response response
        formatted_data = {"lines": lines}
        
        # Escreva a resposata formatada em um JSON file
        with open("formatted_response.json", "w") as json_file:
            json.dump(formatted_data, json_file, indent=4, ensure_ascii=False)  # preservando a formanatcao
        print("\nResposta formatada salva em 'formatted_response.json'.")
    else:
        print("Nenhuma linha foi extraída ou houve um erro.")