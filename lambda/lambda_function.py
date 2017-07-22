
import json
import urllib.parse
import boto3

print('Loading function')

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
polly = boto3.client('polly')

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
    image_desc = image_description(rekog_labels)
    print(image_desc)

    ## Pollyでテキストから音声を合成する
    speech = text_to_speech(image_desc)
    print(speech)

    ## S3に音声をアップロードする
    response = upload_speech(key, speech, image_desc)
    return response

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

def text_to_speech(text):
    try:
        speech = polly.synthesize_speech(
            OutputFormat='mp3',
            SampleRate='22050',
            Text=text,
            TextType='text',
            VoiceId='Joanna'  # とりあえず英語想定
        )
        return speech
    except Exception as e:
        print(e)
        print('Error synthesizing to speech: "{}"'.format(text))
        raise e

def upload_speech(key, speech, description):
    try:
        upload_bucket = 'voiceoutnv.rshd'
        # TODO: バイト列ではなくStreamingBodyをもっとスマートに渡せるのではなかろうか？
        response = s3.put_object(Bucket=upload_bucket, Key=key+'.mp3',
                                 Body=speech['AudioStream'].read(),
                                 ContentType='audio/mpeg',
                                 Metadata={
                                     'Description': description
                                 })
        return response
    except Exception as e:
        print(e)
        print('Error uploading speech "{}".'.format(key))
        raise e
