import os
from email_hunter import EmailHunterClient
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

email_hunter_client = EmailHunterClient(os.getenv('EMAILHUNTERS_KEY'))

def check_if_email_exists(email):
   try: # In case of emailhunter is down, don't validate if email exists in their db.
     return email_hunter_client.exist(email)[0]
   except:
      return True


def get_existing_email(domain):
   return get_existing_emails(domain)[0]['value']


def get_existing_emails(domain):
   return email_hunter_client.search(domain)

