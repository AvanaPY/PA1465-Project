

def create_ai_model():

    lstm_model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(1, return_sequences=True),
        tf.keras.layers.Dense(units=1)
    ])

    model.compile(loss=tf.losses.MeanSquaredError(),
                    optimizer=tf.optimizers.Adam(),
                    metrics=[tf.metrics.MeanAbsoluteError()])
    """
        Creates an AI model

        Args::
            --

        Returns::
            Tensorflow AI model

        Raises::
            --
    """
    return lstm_model

def load_ai_model(model, load_weights_path):
    model.load_weights(load_weights_path)
    """
        Loads the AI model's weights from a file

    Args::
        model: A tensorflow AI model
        load_weights_path: str object representing the file path to load the weights from

    Returns::
        Tensorflow AI model

    Raises::
        Any errors tensorflow might've raised when loading weights
    """
    return model

def save_ai_model(model, save_weights_path):
    model.save_weights(save_weights_path)
    """
        Saves the AI model's weights into a file

    Args::
        model: A tensorflow AI model
        save_weights_path: str object representing the file path to save the weights to

    Returns::
        Tensorflow AI model

    Raises::
        Any errors tensorflow might've raised when loading weights
    """
    return model

def train_ai(model, data): #need to fix data into train and validation
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                    patience=2,
                                                    mode='min')

    history = model.fit(window.train, epochs=MAX_EPOCHS, #
                      validation_data=window.val,
                      callbacks=[early_stopping])
    return history
    """
        Trains an AI model

        Args::
            model:: A tensorflow AI model
            data:: Some data you can train the AI on, I don't know

        Returns::
            --

        Raises::
           --
    """
    pass