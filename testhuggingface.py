from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

def translate_text(text, source_lang, target_lang):
    model_name = "facebook/nllb-200-distilled-600M"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    inputs = tokenizer(text, return_tensors="pt", src_lang=source_lang, tgt_lang=target_lang)
    outputs = model.generate(**inputs)
    translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return translation

# Usage
text_to_translate = "Hello, how are you?"
source_language = "en_XX"  # English
target_language = "es_XX"  # Spanish

result = translate_text(text_to_translate, source_language, target_language)
print(result)
