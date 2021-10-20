# -*- coding: utf-8 -*-
"""en2tr_sample_usage.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14saiYYF6t3-AnNAfBl2zWxamiFtSCgvy
"""

import os

import tensorflow as tf
tf.logging.set_verbosity(tf.logging.ERROR)
tfe = tf.contrib.eager
tfe.enable_eager_execution() 

import numpy as np
from tensor2tensor import problems
from tensor2tensor import models
from tensor2tensor import problems
from tensor2tensor.utils import trainer_lib
from tensor2tensor.data_generators import text_encoder

from tensor2tensor.utils import t2t_model
from tensor2tensor.utils import registry

import textwrap

import sys
sys.path.append("nmt-en-tr")
import nmt_en_tr

model_path = 'en2tr'

data_dir = os.path.join(model_path, 'data')
ckpt_dir = os.path.join(model_path, 'model')

en2tr_problem = problems.problem("translate_en_tr")
encoders = en2tr_problem.feature_encoders(data_dir)

ckpt_path = tf.train.latest_checkpoint(ckpt_dir)

def encode(input_str, output_str=None):
  """Input str to features dict, ready for inference"""
  inputs = encoders["inputs"].encode(input_str) + [1]  # add EOS id 
  batch_inputs = tf.reshape(inputs, [1, -1, 1])  # Make it 3D.
  return {"inputs": batch_inputs}

def decode(integers):
  """List of ints to str"""
  integers = list(np.squeeze(integers))
  #print("-----------------------\n",integers,"\n------------------------\n")
  if 1 in integers:
    integers = integers[:integers.index(1)]
    #print("-----------------------\n",integers,"\n------------------------\n")
  if len(integers) == 1:
    return encoders["inputs"].decode(integers)
  return encoders["inputs"].decode(np.squeeze(integers))

model_name = "transformer"
hparams_set = "transformer_tpu"

Modes = tf.estimator.ModeKeys

hparams = trainer_lib.create_hparams(hparams_set, data_dir=data_dir, problem_name="translate_en_tr")

translate_model = registry.model(model_name)(hparams, Modes.EVAL)

# Restore and translate!
def translate(inputs, beam_size = 5, alpha = 0.6, **kwargs):
  encoded_inputs = encode(inputs)
  with tfe.restore_variables_on_create(ckpt_path):
    model_output = translate_model.infer(encoded_inputs, **kwargs)["outputs"]
  if len(model_output.shape) == 2:
    return decode(model_output)
  else:
    return [decode(x) for x in model_output[0]]
  
def translate_and_display(input):
  output = translate(input)
  print('\n  '.join(textwrap.wrap("Input: {}".format(input), 80)))
  print()
  print('\n  '.join(textwrap.wrap("Output: {}".format(output), 80)))

inputs = "First Name"

translate_and_display(inputs)

#translate_and_display("be sure that the information you give is accurate and complete")

#translate_and_display("people you have contacted during this period")

#translate_and_display("have you been in contact with anyone in the last 14 days who is experiencing these symptoms?")