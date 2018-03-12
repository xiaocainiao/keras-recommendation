


from __future__ import absolute_import
from __future__ import print_function
import numpy as np
#import random
np.random.seed(1337) # for reproducibility

import sys
sys.path.append('../')


from keras.datasets import reuters
from keras.models import Sequential
from keras.layers.recurrent import GRU,LSTM
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.core import TimeDistributedDense, Cosine, Merge, Reshape, ElementMul
from keras.layers.normalization import BatchNormalization
from keras.utils import np_utils
from keras.preprocessing.text import Tokenizer


batchsize=3681
staticFea=300
tempFea=600




def readbatch():
	global staticFile,tempFile,lblFile,batchsize
	static= np.zeros([batchsize,staticFea])
	temp= np.zeros([batchsize,14,tempFea])
	y_train=np.zeros([batchsize,300])
	i=0
	while True:
		s=staticFile.readline()
		t=tempFile.readline()
		l=lblFile.readline()
		s=unicode(s, errors='ignore')
		t=unicode(t, errors='ignore')
		l=unicode(l, errors='ignore')
		if not s:
			break
		st= s.split('\t')
		j=0
		for si in st:
			if not si or si=='\n':
				j=j-1
			else:
				static[i,	j]=float(si)
			j=j+1
		
		tf=t.split('\t')
		j=0
		tff=np.zeros(14*600)
		for ti in tf:
			if not ti or ti=='\n':
				j=j-1
			else:
				tff[	j]=float(ti)
			j=j+1
		tff=tff.reshape([14,600])
		temp[i]=tff
		lbls=l.split('\t')
		j=0
		for si in lbls:
			if not si or si=='\n':
				j=j-1
			else:
				y_train[i,	j]=float(si)
			j=j+1
		
		i=i+1
		if i==batchsize:
			break
	if i==batchsize:
		hasmore=1
	else:
		hasmore=0
		
	return static[0:i-1], temp[0:i-1],y_train[0:i-1],hasmore
		
		

staticmodel=Sequential()
staticmodel.add(Dense(300,300))
staticmodel.add(Activation('tanh'))
tempmodel=Sequential()
tempmodel.add(LSTM(tempFea,300))
model=Sequential()
model.add(Merge([staticmodel, tempmodel],mode='concat'))
model.add(Dense(300+300,300))
model.add(Activation('tanh'))




print('done model construction')
model.compile(loss='mean_squared_error', optimizer='Adadelta')
print('done complie')
for i in range(0,10):
	print("itr",i)
	staticFile=open(r"\\ZW5338456\F$\newTempOut1\fea.static")
	tempFile=open(r"\\ZW5338456\F$\newTempOut1\fea.Temp")
	lblFile=open(r"\\ZW5338456\F$\newTempOut1\fea.lbl")
	j=0
	while True:
		print("batch",j)
		j=j+1
		staticinput ,tempinput, y_train,hasmore = readbatch()
		history = model.train_on_batch([staticinput ,tempinput] ,y_train,accuracy=True)# nb_epoch=10, batch_size=1024, verbose=2, show_accuracy=True)
		if not hasmore :
			staticFile.close()
			tempFile.close()
			lblFile.close()
			break
	model.save_weights(r'\\ZW5338456\f$\temprepdiction.model.lstm.'+`i`)
	

model.save_weights(r'\\ZW5338456\f$\temprepdiction.model.lstm.')
