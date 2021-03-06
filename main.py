#!/usr/bin/env python
# coding: utf-8

'''
A Convolutional Network implementation example using TensorFlow library.
This example is using the MNIST database of handwritten digits
(http://yann.lecun.com/exdb/mnist/)
Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/


Add a itchat controller with multi thread
'''

from __future__ import print_function

import tensorflow as tf

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data

# Import itchat & threading
import itchat
import threading
from multiprocessing import Process,Manager,Value,Lock,Queue
import os
# Create a running status flag


# Parameters


def nn_train(d,queue,lock,lock2,param):
    # Lock
    
    # mnist data reading
    mnist = input_data.read_data_sets("data/", one_hot=True)

    # Parameters
    # learning_rate = 0.001
    # training_iters = 200000
    # batch_size = 128
    # display_step = 10
    learning_rate, training_iters, batch_size, display_step = param

    # Network Parameters
    n_input = 784 # MNIST data input (img shape: 28*28)
    n_classes = 10 # MNIST total classes (0-9 digits)
    dropout = 0.75 # Dropout, probability to keep units

    # tf Graph input
    x = tf.placeholder(tf.float32, [None, n_input])
    y = tf.placeholder(tf.float32, [None, n_classes])
    keep_prob = tf.placeholder(tf.float32) #dropout (keep probability)
    # Create some wrappers dfor simplicity
    def conv2d(x, W, b, strides=1):
        # Conv2D wrapper, with bias and relu activation
        x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
        x = tf.nn.bias_add(x, b)
        return tf.nn.relu(x)


    def maxpool2d(x, k=2):
        # MaxPool2D wrapper
        return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                            padding='SAME')
    # Create model
    def conv_net(x, weights, biases, dropout):
        # Reshape input picture
        x = tf.reshape(x, shape=[-1, 28, 28, 1])

        # Convolution Layer
        conv1 = conv2d(x, weights['wc1'], biases['bc1'])
        # Max Pooling (down-sampling)
        conv1 = maxpool2d(conv1, k=2)

        # Convolution Layer
        conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
        # Max Pooling (down-sampling)
        conv2 = maxpool2d(conv2, k=2)

        # Fully connected layer
        # Reshape conv2 output to fit fully connected layer input
        fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
        fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
        fc1 = tf.nn.relu(fc1)
        # Apply Dropoutrun_state
        fc1 = tf.nn.dropout(fc1, dropout)

        # Output, class prediction
        out = tf.add(tf.matmul(fc1, weights['out']), biases['out'])
        return out

    # Store layers weight & bias
    weights = {
        # 5x5 conv, 1 input, 32 outputs
        'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
        # 5x5 conv, 32 inputs, 64 outputs
        'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
        # fully connected, 7*7*64 inputs, 1024 outputs
        'wd1': tf.Variable(tf.random_normal([7*7*64, 1024])),
        # 1024 inputs, 10 outputs (class prediction)
        'out': tf.Variable(tf.random_normal([1024, n_classes]))
    }

    biases = {
        'bc1': tf.Variable(tf.random_normal([32])),
        'bc2': tf.Variable(tf.random_normal([64])),
        'bd1': tf.Variable(tf.random_normal([1024])),
        'out': tf.Variable(tf.random_normal([n_classes]))
    }

    # Construct model
    pred = conv_net(x, weights, biases, keep_prob)

    # Define loss returlock2n 0and optimizer
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

    # Evaluate model
    correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))


    # Initializing the variables
    init = tf.global_variables_initializer()

    # Launch the graph
    print ('the tensorflow Process ID:{}'.format(os.getpid()))
    with tf.Session() as sess:
        sess.run(init)
        step = 1
        # Keep training until reach max iterations
        print('Wait for lock')
        lock.acquire()
        run_state = d.value
        lock.release()
        print('Start')
        while step * batch_size < training_iters and run_state:
            batch_x, batch_y = mnist.train.next_batch(batch_size)
            # Run optimization op (backprop)
            sess.run(optimizer, feed_dict={x: batch_x, y: batch_y,
                                        keep_prob: dropout})
            if step % display_step == 0:
                # Calculate batch loss and accuracy
                loss, acc = sess.run([cost, accuracy], feed_dict={x: batch_x,
                                                                y: batch_y,
                                                                keep_prob: 1.})
                lock.acquire()
                queue.put("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
                    "{:.6f}".format(loss) + ", Training Accuracy= " + \
                            "{:.5f}".format(acc))
                lock.release()
                '''itchat.send(, wechat_name)'''
            step += 1
            lock2.acquire()
            run_state = d.value
            lock2.release()
        print("Optimization Finished!")
        print(run_state)
        '''itchat.send("Optimization Finished!", wechat_name)'''
        lock.acquire()
        queue.put("Optimization Finished!")
        lock.release()
        # Calculate accuracy for 256 mnist test images
        acc = sess.run(accuracy, feed_dict={x: mnist.test.images[:256],
                                        y: mnist.test.labels[:256],keep_prob: 1.})

        lock.acquire()
        queue.put("Testing Accuracy:"+str(acc))
        lock.release()

lock = Lock()
lock2 = Lock()
num = Value('d', 0)
queue = Queue(10)
flag = False
def wechatsend(wechat_name,queue,lock):
    i = 0
    while 1:
        if queue.empty() == False:
            lock.acquire()
            send_data = queue.get()
            itchat.send(str(send_data), toUserName=wechat_name)
            print("wechat send {}".format(i))
            lock.release()
            print ('the WeChatsend Process ID:{}'.format(os.getpid()))
            i+=1
            print("wechat send {}".format(i))
wechatsend_pro = Process(target=wechatsend,args=('filehelper',queue,lock))
@itchat.msg_register([itchat.content.TEXT])
def chat_trigger(msg):
    #global lock, running, learning_rate, training_iters, batch_size, display_step
    global lock,num,queue,wechatsend_pro,flag,lock2
    learning_rate = 0.001
    training_iters = 20000000
    batch_size = 128
    display_step = 100
    myUserName = itchat.get_friends(update=True)[0]["UserName"]
    if myUserName == msg.fromUserName:
        nn_train_thread = Process(target=nn_train,args=(num,queue,lock,lock2,(learning_rate, training_iters, batch_size, display_step)))
        if msg['Text'] == u'开始':
            print('Starting')
            lock2.acquire()
            num.value = 1
            lock2.release()
            print ('the WeChat Process ID:{}'.format(os.getpid()))
            itchat.send('Hello,the training is starting', toUserName='filehelper')
            try:
                #nn_train_thread = threading.Thread(target=loop, args=(10,))
                nn_train_thread.start()
                '''if flag == False:
                    wechatsend_pro.start()
                    flag = True'''
            except:
                msg.reply('Running')
        elif msg['Text'] == u'停止':
            print('Stopping')
            lock2.acquire()
            num.value = 0
            lock2.release()
            #nn_train_thread.join()
        elif msg['Text'] == u'参数':
            itchat.send('lr=%f, ti=%d, bs=%d, ds=%d'%(learning_rate, training_iters, batch_size, display_step),'filehelper')
        elif msg['Text'] == u'询问':
            lock.acquire()
            send_data = queue.get()
            itchat.send(str(send_data), toUserName='filehelper')
            lock.release()
        else:
            ''' try:
                param = msg['Text'].split()
                key, value = param
                print(key, value)
                if key == 'lr':
                    learning_rate = float(value)
                elif key == 'ti':
                    training_iters = int(value)
                elif key == 'bs':
                    batch_size = int(value)
                elif key == 'ds':
                    display_step = int(value)
            except:
                pass'''
            pass


if __name__ == '__main__':
    itchat.auto_login(hotReload=True)
    itchat.run()
    