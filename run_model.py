# Copyright © 2024 Advanced Micro Devices, Inc. All rights reserved.

import onnxruntime_genai as og

def model_load(model_dir : str):

    model = og.Model(model_dir)
    return model

def get_tokenizer(model):
    tokenizer = og.Tokenizer(model)
    tokenizer_stream = tokenizer.create_stream()

    return tokenizer, tokenizer_stream

def get_prompt():
    chat_template = '<|user|>\n{input} <|end|>\n<|assistant|>'

    text = input("Input: ")
    if not text:
        print("Error, input cannot be empty")
        exit

    prompt = f'{chat_template.format(input=text)}'
    return prompt

def setup(model, tokenizer, tokenizer_stream, prompt):
    
    # Set the max length to something sensible by default,
    # since otherwise it will be set to the entire context length
    search_options = {}
    search_options['max_length'] = 2048

    input_tokens = tokenizer.encode(prompt)

    params = og.GeneratorParams(model)
    params.set_search_options(**search_options)
    params.input_ids = input_tokens
    print("Creating generator with prompt")
    generator = og.Generator(model, params)

    print("Output: ", end='', flush=True)

    return generator

def run(generator, tokenizer_stream):

    num_tokens = 0

    tokens = []

    try:
        while not generator.is_done():
            generator.compute_logits()
            generator.generate_next_token()

            # this is getting token for first batch ?
            new_token = generator.get_next_tokens()[0]

            tokens.append(new_token)

            print(tokenizer_stream.decode(new_token), end='', flush=True)
            num_tokens += 1
    except KeyboardInterrupt:
        print("  --control+c pressed, aborting generation--")

    print()
    print(f"total tokens: {num_tokens}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--model_dir', type=str, default='model', help='Path to model directory with config json')
    args = parser.parse_args()
    print(f"model_dir: {args.model_dir}")

    model = model_load(args.model_dir)
    tokenizer, tokenizer_stream = get_tokenizer(model)
    prompt = get_prompt()
    generator = setup(model, tokenizer, tokenizer_stream, prompt)
    run(generator, tokenizer_stream)
    del generator
