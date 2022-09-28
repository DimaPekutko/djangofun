from time import sleep
from celery import shared_task
from core.aws import s3, ses
from core.settings import AWS_CREDENTIALS as AWS


@shared_task
def notify_follower_about_new_post(page_name, post_content, email):
    ses.send_email(
        Destination={
        'ToAddresses': [email],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': post_content,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'New post on ' + page_name + ' page.',
            },
        },
        Source=AWS["AWS_VERIFIED_EMAIL"],
    )
    # print(f"{email} notifyed about new post")