# Copyright © 2024 Advanced Micro Devices, Inc. All rights reserved.

import onnxruntime_genai as og
from fastapi import FastAPI,Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import uvicorn
import json
import os


def model_load(model_dir : str):
    model = og.Model(model_dir)
    return model

def get_tokenizer(model):
    tokenizer = og.Tokenizer(model)
    tokenizer_stream = tokenizer.create_stream()
    return tokenizer, tokenizer_stream

def setup(model, tokenizer, tokenizer_stream, prompt):
    # Set the max length to something sensible by default,
    # since otherwise it will be set to the entire context length
    search_options = {}
    search_options['max_length'] = 2048

    input_tokens = tokenizer.encode(prompt)
    print(input_tokens)

    params = og.GeneratorParams(model)
    params.set_search_options(**search_options)
    params.input_ids = input_tokens
    print("Creating generator with prompt")
    generator = og.Generator(model, params)

    print("Output: ", end='', flush=True)
    return generator

def get_chat_user_prompt(input:str):
    user_input = input
    chat_template = f'<|user|>\n{{input}} <|end|>\n<|assistant|>\n'
    prompt = f'{chat_template.format(input=user_input)}'
    return prompt

def get_cot_user_prompt(input:str):
    user_input = input

    if model_running_name =="DeepSeek-R1-Distill-Qwen-7B" :
        chat_template = f'<|User|>\n{user_input}\n<|Assistant|>\n<think>\n'

    elif model_running_name == "DeepSeek-R1-Distill-Llama-8B" :
        chat_template = f'<|User|>\n{user_input}<|Assistant|>\n<think>\n'
    else:
        print('11')
        chat_template = f'<|User|>\n{user_input}<|end|>\n<|Assistant|>\n<think>\n'

    return chat_template

async def get_stream_chat_response(generator,tokenizer_stream,request:Request) :
    # yield "\n **思维链如下** : \n"
    yield "<think>\n"
    while not generator.is_done():
        generator.compute_logits()
        generator.generate_next_token()

        # this is getting token for first batch ?
        new_token = generator.get_next_tokens()[0]
        
        decode_text = tokenizer_stream.decode(new_token)

        if decode_text == '|User|':
            break

        if decode_text == '|Assistant|' : 
            break
        
        if await request.is_disconnected() :
            break

        yield decode_text

    del generator 

class Item(BaseModel):
    input:str

class model_config(BaseModel):
    model_name:str

app = FastAPI()

dir = os.path.dirname(os.path.abspath(__file__))

models_paths = {"DeepSeek-R1-Distill-Qwen-1.5B":f"{dir}\\models\\amd-qwen1.5B",
                "DeepSeek-R1-Distill-Llama-8B":f"{dir}\\models\\amd-llama8B",
                "DeepSeek-R1-Distill-Qwen-7B":f"{dir}\\models\\amd-qwen7B"
              }

model = None
model_running_name = None  #正在运行的模型的名称
tokenizer = None
tokenizer_stream = None
generator = None

llama_8b_think_token = 128014

@app.get("/healthy")
async def healthy():
    response = {
        "status" : "healthy",
    }
    response = json.dumps(response)
    return response

@app.post("/v1/chat/completions")
async def chat(request:Request) :
    if model == None :
        return {"error":"should specify a model, you can use change_model to specify a model for servering "}  
    
    data = await request.json()
    prompt = get_cot_user_prompt(data['input'])
    generator =  setup(model, tokenizer, tokenizer_stream, prompt)

    return StreamingResponse(get_stream_chat_response(generator,tokenizer_stream,request),media_type="text/plain")

@app.post("/change_model") 
async def change_model(model_config:model_config) :
    model_name = model_config.model_name
    if not (model_name  in models_paths ) : 

        response = {"response":f"model is not suuport ,only support {models_paths.keys()}"}
        return response
        
    model_path = models_paths[model_name]
    global model
    model  = None
    model =  model_load(model_path)

    global model_running_name
    model_running_name = model_name

    global tokenizer,tokenizer_stream
    tokenizer, tokenizer_stream = get_tokenizer(model)
    response = {"response":"change successfully!"}
    return response

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=9090)
