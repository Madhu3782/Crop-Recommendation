from chatbot_brain import brain

def verify():
    # Mock Models
    brain.register_models(price_model="MockPrice", crop_model="MockCrop", pest_model="MockPest")
    
    # Test: Kannada Translation
    query = "How to treat potato early blight?"
    target_lang = "Kannada"
    
    print(f"\n--- TEST: Query '{query}' in '{target_lang}' ---")
    response = brain.generate_response(query, language=target_lang)
    
    print(f"Original (En): {response['answer_en'][:100]}...")
    try:
        translated_text = response['answer_translated'].encode('utf-8', 'ignore').decode('utf-8')
        print(f"Translated ({target_lang}):\n{translated_text}")
    except Exception as e:
        print(f"Print Error: {e}")
    
    # Check if translation looks different from English
    if response['answer_translated'] != response['answer_en']:
        print("\nSUCCESS: Translation generated.")
    else:
        print("\nWARNING: Translation is identical to English (Validation Failed or English requested).")

if __name__ == "__main__":
    verify()
