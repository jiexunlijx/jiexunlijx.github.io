import openai

#Set your API key here
openai.api_key = "Your API key"

while True:
    a = input("Enter a prompt or "quit" to exit: ")
    if a == "exit" or a == "quit":
        break
    response = openai.Image.create(
    prompt= a,
    n=1,
    #change image size for lower cost. 512x512, 256x256
    size="1024x1024"
    )
    image_url = response['data'][0]['url']
    print(image_url)