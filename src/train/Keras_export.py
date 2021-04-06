#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:**********************************************
# @Time    : 3/30/2021 4:31 PM
# @Author  : Gaopeng.Bai
# @File    : Keras_export.py
# @User    : gaope
# @Software: PyCharm
# @Description: 
# Reference:**********************************************
# saved model with signature
import os

import tensorflow.compat.v1 as tf
import tensorflow.compat.v1.keras.backend as K


def export_model(model,
                 export_model_dir,
                 model_version
                 ):
    """
    :param model:
    :param export_model_dir: type string, save dir for exported model
    :param model_version: type int best
    :return:no return
    """
    export_path_base = export_model_dir
    export_path = os.path.join(
        tf.compat.as_bytes(export_path_base),
        tf.compat.as_bytes(str(model_version)))
    builder = tf.saved_model.builder.SavedModelBuilder(export_path)
    with tf.get_default_graph().as_default():
        # prediction_signature
        tensor_info_input = tf.saved_model.utils.build_tensor_info(model.input)
        tensor_info_output = tf.saved_model.utils.build_tensor_info(model.output)
        prediction_signature = (
            tf.saved_model.signature_def_utils.build_signature_def(
                inputs={'input': tensor_info_input},  # Tensorflow.TensorInfo
                outputs={'result': tensor_info_output}))
        print('step1 => prediction_signature created successfully')

        # set-up a builder
        builder.add_meta_graph_and_variables(
            # tags:SERVING,TRAINING,EVAL,GPU,TPU
            sess=K.get_session(),
            tags=[tf.saved_model.tag_constants.SERVING],
            signature_def_map={'prediction_signature': prediction_signature,
                               tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                                   prediction_signature},
        )
        print('step2 => Export path(%s) ready to export trained model' % export_path, '\n starting to export model...')
        builder.save()
        print('Done exporting!')


if __name__ == '__main__':
    model = tf.keras.models.load_model('dnn_model/001')
    # model.compile(loss=categorical_crossentropy,
    #           optimizer=Adadelta(lr=0.1),
    #           metrics=['accuracy'])
    # model.load_weights('./model_data/weights.hdf5')
    model.summary()

    # with tf.Session() as sess:
    #     tf.saved_model.tag_constants.SERVING == "serve"，这里load时的tags需要和保存时的tags一致
        # meta_graph_def = tf.saved_model.loader.load(sess, tags=["serve"], export_dir="dnn_model/001")
        # graph = tf.get_default_graph()

    export_model(
        model,
        'models/export_model',
        2
    )
