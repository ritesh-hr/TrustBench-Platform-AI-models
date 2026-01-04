from google import genai

client = genai.Client(api_key="AIzaSyCZT2vOvBobxhZlU9tzAFe0T7ZGiWhRchY")

resp = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="You have 15 apples and give away 7. How many apples remain?"
)

print(resp)
print("TEXT:", resp.text)