from openaq import OpenAQ

client = OpenAQ(api_key='2ad5c805534fabe02ef4baa9f0a374d502e9607b02ec080b8323dced2866b25e')

location = client.locations.get(2178)

client.close()

print(location)