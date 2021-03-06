from . import Env
env = Env()

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'ENABLE_CAPTCHA': (
        True,
        "Use Google ReCaptchav3; disable for legal or debug/hotfix reasons"
    ),
    'FEEDBACK_EMAIL': (
        "",
        "Where to send the feedback notifications to"
    ),
    'OA_NOTARY_CONTRACT': (
        '0xa57812DeC86336809Ea68987AbaA1669DeA31541',
        'Please configure this value so notarization works correctly'
    ),
    'OA_WRAP_API_URL': (
        'http://docker-host:9090',
        'Either local or remote setup which is able to wrap documents'
    ),
    # Variables needed for notarisastion step, which relies on buckets/queues
    # may be replaced by other mechanisms once they are defined
    # You could use AWS cloud, minio or AWS localstack to provide these values
    'OA_UNPROCESSED_QUEUE_URL': (
        '',
        'Do not send manual notifications if empty; must be available using the OA access keys'
    ),
    'OA_UNPROCESSED_BUCKET_NAME': (
        '',
        'Just a plain bucket name, do not send files to notarisation if empty',
    ),
    'OA_AWS_ACCESS_KEYS': (
        ':',
        'Values in format accesskey:secretkey, None if empty (policy defined)'
    ),

    # misc
    'USERS_NOTIFICATIONS_MAILBOX': (
        '',
        'The email where new notifications about registered users/etc will be sent'
    )

}
