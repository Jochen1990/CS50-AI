In this project, we use a convolutional neural network to learn from a data set of German traffic signs to accurately predict the traffic sign categories.
The model used is based on the Tensor Flow Keras Sequential Model.

I started the model by applaying one convultional layer with 32 filters with a 3 by 3 kernel, 1 max-pooling layer with a two by two pool size and one hidden layer with 128 units and a 0.5 dropout. The results showd that this model was obviously not
adequate enough to learn from the data set. This was probably due to the fact that only one convolutional layer and one pooling layer were not enough to generalize the image enough.
Additionally, only one hidden layer was probably not enough for the model to learn efficiently.

I then experimented around by adding and subtracting convolutional layers and pooling layers. The results showed, that in the end, having two convolutional and two pooling layers, three hidden layers with one drop out of 0.5 gave the best accuracy and best results.


