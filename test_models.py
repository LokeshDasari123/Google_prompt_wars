import vertexai
from vertexai.generative_models import GenerativeModel

project_id = "nexus-event-app-1904"
location = "asia-south1"

print(f"Scanning the Vertex AI ecosystem in {location}...")
vertexai.init(project=project_id, location=location)

# The Complete Arsenal (Ordered by Intelligence & Power)
models_to_test = [
    "gemini-3.1-pro-preview",  # The bleeding edge
    "gemini-2.5-pro",          # The modern heavyweight reasoning engine
    "gemini-2.5-flash",        # The modern speedster
    "gemini-2.0-flash",        # Reliable fallback
    "gemini-1.5-pro-002",      # Stable legacy pro
    "gemini-1.5-pro",          # Base legacy pro
    "gemini-1.5-flash"         # Base legacy flash
]

working_models = []

for model_name in models_to_test:
    try:
        model = GenerativeModel(model_name)
        response = model.generate_content("Ping")
        print(f"✅ SUCCESS: '{model_name}' is LIVE.")
        working_models.append(model_name)
    except Exception:
        print(f"❌ FAILED: '{model_name}' - Locked or unavailable.")

print("\n--- FINAL VERDICT ---")
if working_models:
    print(f"🏆 The most powerful model available to you is: {working_models[0]}")
else:
    print("⚠️ No models responded. Verify your Google Cloud credits.")
