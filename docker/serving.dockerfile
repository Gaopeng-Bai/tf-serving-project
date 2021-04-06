FROM tensorflow/serving:2.4.1

ADD src/train/models /models

CMD ["--model_config_file=/models/models.config"]