import torch
import albumentations as A
import numpy as np

from PIL import Image
from model import create_mobilenet_model
from albumentations.pytorch import ToTensorV2

model = create_mobilenet_model()
device = "cuda" if torch.cuda.is_available() else "cpu"

checkpoint = torch.load("weights-1.pth")
model.load_state_dict(checkpoint)

transform = A.Compose([
    A.Resize(232, 232),
    A.CenterCrop(224, 224),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])

model.eval()

def predict(image_path):
    img = Image.open(image_path).convert("RGB")

    img = np.array(img)
    img = transform(image=img)
    img = img['image'].to(device)
    img = img.unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)

    outputs = torch.nn.Softmax()(outputs)
    #print(outputs[0])
    return outputs[0].tolist()
    # real_probability, fake_probability = outputs

    # return real_probability, fake_probability
