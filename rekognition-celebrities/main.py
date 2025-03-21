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
    input_bucket_name = "" #incluir nome do bucket
    output_bucket_name = "" #incluir nome do bucket
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
        
        
        output_key = f"results/{Path(photo_path).stem}-resultado.jpg"  # Use "results" as a folder (prefix) within the bucket 
        draw_boxes_s3_and_save(input_bucket_name, photo_path, output_bucket_name, output_key, faces)
