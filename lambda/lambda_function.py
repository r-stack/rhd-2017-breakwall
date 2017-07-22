
import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    ## S3オブジェクトを取得する
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    s3obj = get_s3_object(bucket, key)
    #print(s3obj)

    ## Rekognitionでラベルを検出する
    # TODO s3オブジェクトが画像じゃなかったらエラーにする
    rekog_labels = recognize_image_labels(bucket, key)
    return image_description(rekog_labels)

def get_s3_object(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def recognize_image_labels(bucket, key):
    try:
        labels = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )
        return labels
    except Exception as e:
        print(e)
        print('Error detecting labels {} from bucket {}.'.format(key, bucket))
        raise e

### 画像に対するラベルから画像の説明文を生成する。
def image_description(labels):
    top3_labels = [label['Name'] for label in labels['Labels'][:3]]
    return 'This image shows {}.'.format(', '.join(top3_labels))
