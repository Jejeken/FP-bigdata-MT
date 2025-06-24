from django.db import models

# Create your models here.
from openaq import OpenAQ
import os
from pandas import json_normalize

API_KEY = os.environ.get('2ad5c805534fabe02ef4baa9f0a374d502e9607b02ec080b8323dced2866b25e')

def air_quality(location_id):
    client = OpenAQ(api_key=API_KEY)
    location = client.locations.get(location_id)
    result = json_normalize(location.dict())
    client.close()
    return result
