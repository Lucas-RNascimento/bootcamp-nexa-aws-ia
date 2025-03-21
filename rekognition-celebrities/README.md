# AWS Rekognition: Detectando Celebridades em Imagens


Amazon Rekognition é um serviço avançado de análise de imagens e vídeos que utiliza aprendizado de máquina para identificar celebridades, objetos, cenas e até emoções em rostos de forma automatizada. Com esta tecnologia, é possível transformar imagens e vídeos em dados úteis, otimizando processos e integrando informações diretamente em sistemas de negócios


### Projeto Detectando Celebridades em Imagens

#### Steps:

1. Antes de inicar a codificação eu fiz a configuração do meu ambiente de projeto

   - comandos
    ```python

        Pip install uv

        uv init rekognition-celebrities

        uv add boto3

        uv add "boto3-stubs[rekognition]"

        uv venv

        .venv\Scripts\activate 

    ```
    


2. Codificacao
    - importando as bibliotecas
    ```python
        from pathlib import Path #Permite trabalhar com caminhos de arquivos de maneira flexível e compatível com diferentes sistemas operacionais.

        import boto3 #A biblioteca para interagir com serviços AWS, como o Rekognition.

        from mypy_boto3_rekognition.type_defs import CelebrityTypeDef, RecognizeCelebritiesResponseTypeDef #Fornece os tipos para o serviço Rekognition, como os retornos esperados para as funções.
        
        from PIL import Image, ImageDraw, ImageFont #(Python Imaging Library): Utilizado para abrir, desenhar e manipular imagens.
    ```

    - Configurando o Cliente AWS Rekognition
    ```python
        client = boto3.client("rekognition") #Inicializa o cliente para acessar os recursos do serviço Amazon Rekognition.


        def get_path(file_name: str) -> str:
            return str(Path(__file__).parent / "images" / file_name) #Uma função auxiliar que gera o caminho completo de um arquivo na pasta images relativa ao script atual. Isso facilita o uso de arquivos locais.
    ```

    - Funcao para reconhecimento das Celebridades em Imagens
    ```python
        def recognize_celebrities(photo: str) -> RecognizeCelebritiesResponseTypeDef:
        with open(photo, "rb") as image:
            return client.recognize_celebrities(Image={"Bytes": image.read()})
        
        #Usa a função client.recognize_celebrities para enviar uma imagem ao Rekognition e receber a análise de celebridades detectadas.

        #O arquivo da imagem é lido em modo binário (rb) e enviado na requisição em formato de bytes.
    ```

    - Desenhando Caixas nas Faces Reconhecidas
    ```python
        def draw_boxes(image_path: str, output_path: str, face_details: list[CelebrityTypeDef]):
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        width, height = image.size

        for face in face_details:
            box = face["Face"]["BoundingBox"]  # type: ignore
            left = int(box["Left"] * width)  # type: ignore
            top = int(box["Top"] * height)  # type: ignore
            right = int((box["Left"] + box["Width"]) * width)  # type: ignore
            bottom = int((box["Top"] + box["Height"]) * height)  # type: ignore

            confidence = face.get("MatchConfidence", 0)
            if confidence > 90:
                draw.rectangle([left, top, right, bottom], outline="red", width=3)

                text = face.get("Name", "")
                position = (left, top - 20)
                bbox = draw.textbbox(position, text, font=font)
                draw.rectangle(bbox, fill="red")
                draw.text(position, text, font=font, fill="white")

        image.save(output_path)
        print(f"Imagem salva com resultados em : {output_path}")

        # Desenha caixas ao redor das faces reconhecidas e adiciona o nome da celebridade, caso ela seja identificada com confiança acima de 90%

        #Caixas delimitadoras: As dimensões (esquerda, topo, direita, inferior) são calculadas com base na largura e altura da imagem.

        #Texto: O nome da celebridade é desenhado acima da caixa, com um retângulo de fundo vermelho.
    ```


    - Executando o Script Principal
    ```python
        if __name__ == "__main__":
        photo_paths = [
            get_path("bbc.jpg"),
            get_path("msn.jpg"),
            get_path("beckham-harden.jpg"),
        ]

        for photo_path in photo_paths:
            response = recognize_celebrities(photo_path)
            faces = response["CelebrityFaces"]
            if not faces:
                print(f"Não foram encontrados famosos para a imagem: {photo_path}")
                continue
            output_path = get_path(f"{Path(photo_path).stem}-resultado.jpg")
            draw_boxes(photo_path, output_path, faces)

        #Para cada imagem, a função recognize_celebrities() é chamada, retornando os detalhes das faces identificadas.

        #Caso nenhuma celebridade seja encontrada, uma mensagem é exibida e a iteração continua com a próxima imagem.
    ```


3. Ideias de Melhorias

- Fazer a busca da imagem em um bucket S3

    ```python

        from pathlib import Path
        import boto3
        from mypy_boto3_rekognition.type_defs import CelebrityTypeDef, RecognizeCelebritiesResponseTypeDef
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO

        # Initialize Rekognition and S3 clients
        client = boto3.client("rekognition")
        s3_client = boto3.client("s3")

        def recognize_celebrities_s3(bucket_name: str, file_name: str) -> RecognizeCelebritiesResponseTypeDef:
            return client.recognize_celebrities(Image={"S3Object": {"Bucket": bucket_name, "Name": file_name}})

        def draw_boxes_s3_and_save(bucket_name: str, file_name: str, output_bucket: str, output_key: str, face_details: list[CelebrityTypeDef]):
            
            # Download the image from the S3 bucket to memory
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=file_name)
            image = Image.open(BytesIO(s3_object["Body"].read()))
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()

            width, height = image.size

            for face in face_details:
                box = face["Face"]["BoundingBox"]  # type: ignore
                left = int(box["Left"] * width)  # type: ignore
                top = int(box["Top"] * height)  # type: ignore
                right = int((box["Left"] + box["Width"]) * width)  # type: ignore
                bottom = int((box["Top"] + box["Height"]) * height)  # type: ignore

                confidence = face.get("MatchConfidence", 0)
                if confidence > 90:
                    draw.rectangle([left, top, right, bottom], outline="red", width=3)

                    text = face.get("Name", "")
                    position = (left, top - 20)
                    bbox = draw.textbbox(position, text, font=font)
                    draw.rectangle(bbox, fill="red")
                    draw.text(position, text, font=font, fill="white")

            # Save the modified image to memory as bytes
            image_buffer = BytesIO()
            image.save(image_buffer, format="JPEG")
            image_buffer.seek(0)

            # Upload the image back to the output S3 bucket
            s3_client.put_object(Bucket=output_bucket, Key=output_key, Body=image_buffer, ContentType="image/jpeg")
            print(f"Imagem salva com resultados no bucket S3: {output_bucket}/{output_key}")

        if __name__ == "__main__":
            input_bucket_name = "bkt-rekognition-celebrities"  # Bucket containing input images
            output_bucket_name = "bkt-rekognition-celebrities"  # Bucket to store processed images
            photo_paths = [
                "input/contora.jpg"  # Use "input" as a folder (prefix) within the bucket  
            ]

            for photo_path in photo_paths:
                print(f"Processando a imagem: {photo_path}")
                response = recognize_celebrities_s3(input_bucket_name, photo_path)
                faces = response["CelebrityFaces"]
                if not faces:
                    print(f"Não foram encontrados famosos para a imagem: {photo_path}")
                    continue
                
                # Define the output path in S3 for the processed image
                output_key = f"results/{Path(photo_path).stem}-resultado.jpg"
                draw_boxes_s3_and_save(input_bucket_name, photo_path, output_bucket_name, output_key, faces)
    ```