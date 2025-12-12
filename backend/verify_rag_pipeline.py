from chatbot_brain import brain

def verify():
    # Mock Models (just dummy objects)
    brain.register_models(price_model="MockPrice", crop_model="MockCrop", pest_model="MockPest")
    
    # Test 1: Knowledge Base Query
    print("\n--- TEST 1: RAG Query (Potato Blight) ---")
    response1 = brain.generate_response("How to treat potato early blight?")
    print(f"Response:\n{response1}")
    
    # Test 2: Market Query (intent check)
    print("\n--- TEST 2: Market Query (Wheat Price) ---")
    response2 = brain.generate_response("What is the price of wheat?")
    print(f"Response:\n{response2}")
    
    # Test 3: General Chit-chat
    print("\n--- TEST 3: General (Hello) ---")
    response3 = brain.generate_response("Hello, are you there?")
    print(f"Response:\n{response3}")

if __name__ == "__main__":
    verify()
