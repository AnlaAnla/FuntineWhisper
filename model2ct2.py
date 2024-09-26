# ct2-transformers-converter --model models/whisper-tiny-finetune --output_dir models/whisper-tiny-finetune-ct2 --copy_files tokenizer.json preprocessor_config.json --quantization float16


# from ctranslate2.converters import Converter
#
# model_path = "models/whisper-large-v3-finetune"
# output_dir = "models/whisper-large-v3-finetune-ct2"
#
# converter = Converter(model_name_or_path=model_path)
# converter.convert(output_dir, copy_files=["tokenizer.json", "preprocessor_config.json"])
#
# print("Done")


import subprocess

a = subprocess.call(["dir"])  # shell参数为false，则，命令以及参数以列表的形式给出
print(a)
'''
0  此时只返回0表示执行成功
'''