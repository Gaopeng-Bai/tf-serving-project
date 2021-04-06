'''
coding: utf-8
python: 3.7.6
Date: 2021-04-01 00:03:36
@Software: VsCode
@Author: Gaopeng Bai
@Email: gaopengbai0121@gmail.com
@Description: 
'''

import tensorflow as tf
import os


def export_model(model,
                 export_model_dir,
                 model_version
                 ):
    # form export_path
    export_path = os.path.join(
        tf.compat.as_bytes(export_model_dir),
        tf.compat.as_bytes(str(model_version)))

    # Defining your own signature is not necessary in TF2 using keras model, the framework will generate for you.
    @tf.function(input_signature=[tf.TensorSpec([], dtype=tf.float32)])
    def model_predict(input_batch):
        return {'input': input_batch, 'result': model(input_batch, training=False)}

    # Must contain 'serving_default' when using tensorflow-serving
    model.save(export_path,
               signatures={'result': model_predict,
                           tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY: model_predict})


if __name__ == '__main__':
    # load keras model using tf.keras.models.load_model()
    model = tf.keras.models.load_model('models/dnn_model/001')
    print(model.summary())
    # export model to models/export_model/2 with specified signature
    export_model(model, 'models/export_model', 2)
