# -*- coding: utf-8 -*-
"""GAN using tensorflow.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ImL4RFQiIHLoLFc3k8hIvGkGnDYbA__z
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.datasets import mnist

LOG_DIR = "./logs/gan/"

(x_train,y_train), (x_test,y_test) = mnist.load_data()
x_train = x_train.astype(np.float32)/255.0
x_train = x_train.reshape(-1, 784)

def get_next_batch(batch_size, data_x):
  indices = np.random.choice(range(len(data_x)), batch_size)
  x = data_x[indices]
  return x

"""### *Graph Construction*"""

noise_dim = 100

gen_input = tf.placeholder(dtype=tf.float32, shape=[None, noise_dim])
disc_input = tf.placeholder(dtype=tf.float32, shape=[None, 784])

def generator(gen_input):
  with tf.variable_scope("generator"):
    dense1 = tf.layers.dense(gen_input, 256, activation=tf.nn.elu)
    dense2 = tf.layers.dense(dense1, 512, activation=tf.nn.elu)
    output = tf.layers.dense(dense2, 784, activation=tf.nn.sigmoid)
    return output  
  
def discriminator(disc_input):
  with tf.variable_scope("discriminator", reuse=tf.AUTO_REUSE):
    dense1 = tf.layers.dense(disc_input, 512, activation=tf.nn.elu)
    dense2 = tf.layers.dense(dense1, 256, activation=tf.nn.elu)
    output = tf.layers.dense(dense2, 1, activation=tf.nn.sigmoid)
    return output

g_z = generator(gen_input)
d_x = discriminator(disc_input)
d_g = discriminator(g_z)

train_vars = tf.trainable_variables()

gen_vars = [var for var in train_vars if "generator" in var.name]
disc_vars = [var for var in train_vars if "discriminator" in var.name]

disc_loss = tf.reduce_mean(tf.log(d_x) + tf.log(1 - d_g))
gen_loss = tf.reduce_mean(tf.log(d_g))

tf.summary.scalar("disc_loss", disc_loss)
tf.summary.scalar("gen_loss", gen_loss)

disc_step = tf.train.AdamOptimizer(1e-4).minimize(-disc_loss, var_list=disc_vars)
gen_step = tf.train.AdamOptimizer(1e-4).minimize(-gen_loss, var_list=gen_vars)

batch_size = 100
BATCH_NUM = (x_train.shape[0]//batch_size)
EPOCHS = 101

with tf.Session() as sess:
  train_writer = tf.summary.FileWriter(LOG_DIR, graph=tf.get_default_graph())
  sess.run(tf.global_variables_initializer())
  for i in range(EPOCHS):
    for j in range(BATCH_NUM):
      train_x = get_next_batch(batch_size, x_train)
      noise_x = np.random.normal(0.0, 1, size=(batch_size, noise_dim))
      
      sess.run(disc_step, feed_dict={disc_input:train_x, gen_input:noise_x}) 
      sess.run(gen_step, feed_dict={gen_input:noise_x})
      
    if i%10 == 0:
      train_x = get_next_batch(batch_size, x_train)
      noise_x = np.random.normal(0.0, 1, size=(batch_size, noise_dim))
      
      images = sess.run(g_z, feed_dict={gen_input:noise_x})
      images = images.reshape(-1, 28, 28)
      image = np.vstack([np.hstack([images[i] for i in np.random.choice(batch_size, 5)]) for j in range(5)])
      plt.figure(figsize=(10, 10))
      plt.imshow(image, cmap='gray')
      plt.title("Generate Image at step {}".format(i))
      plt.savefig("Image{}.png".format(i))

# %load_ext tensorboard

# %tensorboard --logdir "./logs/gan/"

