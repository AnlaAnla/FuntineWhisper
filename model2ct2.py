from ctranslate2.converters import Converter

model_path = "models/whisper-large-v3-finetune"
output_dir = "models/whisper-large-v3-finetune-ct2"

converter = Converter(model_name_or_path=model_path)
converter.convert(output_dir, copy_files=["tokenizer.json", "preprocessor_config.json"])