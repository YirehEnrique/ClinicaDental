Para instalar los requerimientos:
pip install -r requirements.txt

Para usar supabase: 

1. crear archivo .env
2. Recordar instalar -- pip install python-dotnev , para su uso correcto

3. importaciones: 

from dotenv import load_dotenv
import os

4. función para cargar el .env
load_dotenv()

5. Colocar en el .env
SECRET_KEY = 'django-insecure-yxc3-=w7^8pch)=w6&79fd2lr^yc35uekjzeu+4(n!+@wff0mx'
SUPABASE_HOST = aws-0-us-west-2.pooler.supabase.com #db.qodkeulvwevukezyrlwr.supabase.co
SUPABASE_PASSWORD =  dmZwfnNPNq41wGoK