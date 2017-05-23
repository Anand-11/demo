


DEBUG = True#False
PRODUCTION=True






#----------------------------------------------------------------------------
COUPON_MAIL_CC=['elmer@yoolotto.com','ali@yoolotto.com'] if PRODUCTION else ['kanika.chugh@sp-assurance.com']
COUPON_REDEEM_DURATION=24*60 if PRODUCTION else 5 # duration must be in minutes
NOTIFICATIONS_SANDBOX=not PRODUCTION #set sandbox based on production 

ALLOWED_HOSTS = ["*"]
# POSTMARK_API_KEY = ""
# POSTMARK_SENDER = ""

ADMINS = (
    ('Yoolotto', 'kanika.chugh@sp-assurance.com'),
)


MANAGERS = ADMINS

'''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'prowithcoupon',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '3306',                      # Set to empty string for default.
    }
}'''

'''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'yoo_db1',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'spa_user',
        'PASSWORD': 'yoolotto',
        'HOST': '184.72.191.192',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '3306',                      # Set to empty string for default.
    }
}'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'yoo_lat',                # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER':'root',#'yoolotto_reward_spauser',
        'PASSWORD':'root', #'Spayoorewards@789',
        'HOST': '127.0.0.1',#'yoospa_qa',#'107.22.13.68',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '3306',                      # Set to empty string for default.
    }
}




BASE_URL = "http://localhost:8000"

#DEFAULT_FROM_EMAIL = "prizes@yoolotto.com"
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_HOST_USER = 'yoolottocoupons@gmail.com'
#EMAIL_HOST_PASSWORD = 'Yoolotto@123'

DEFAULT_FROM_EMAIL = "postmaster@yoolotto.com"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@yoolotto.com'
EMAIL_HOST_PASSWORD = '392d835b47387003458deed44c86f042'

