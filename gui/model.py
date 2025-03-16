import torch
import timm
from torch import nn

def create_mobilenet_model(num_classes=2, freeze_at_start=True):
    model = timm.create_model('mobilenetv3_small_100', pretrained='imagenet')

    if freeze_at_start:
        for param in model.parameters():
            param.requires_grad = False

    in_features = model.classifier.in_features

    model.classifier = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.BatchNorm1d(512),
        nn.ReLU(),
        nn.Dropout(0.4),

        nn.Linear(512, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Dropout(0.3),

        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Dropout(0.2),

        nn.Linear(128, num_classes)
    )

    return model
