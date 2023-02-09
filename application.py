from io import BytesIO
from tkinter import Image
import tensorflow as tf
tf.compat.v1.disable_v2_behavior()
#rom tensorflow.keras.applications.imagenet_utils import decode_predictions
import numpy as np
from PIL import Image ##from here added for XAI, remove if error 4 libs
from keras.utils import load_img
from keras.utils import img_to_array
from lime import lime_image
import matplotlib.pyplot as plt
########################Serialization####################
from json import JSONEncoder
import json
import shap
from keras.preprocessing.image import ImageDataGenerator
## IMPORT FOR OCCLUSION
# from tf_explain.callbacks.occlusion_sensitivity import OcclusionSensitivityCallback
# from tf_explain.callbacks.occlusion_sensitivity import OcclusionSensitivity
# import cv2

dir_path = 'dataset-resized/'
test=ImageDataGenerator(rescale=1/255,
                        validation_split=0.2)
test_generator=test.flow_from_directory(dir_path,
                                        target_size=(300,300),
                                        batch_size=32,
                                        class_mode='categorical',
                                        subset='validation',
                                        shuffle=True)

labels = (test_generator.class_indices)
labels = dict((v,k) for k,v in labels.items())

def get_ClassName(var):
    result1 = None
    if var == 'cardboard':
        result1 = 0
    elif var == 'glass':
        result1 = 1
    elif var == 'metal':
        result1 = 2
    elif var == 'paper':
        result1 = 3
    elif var == 'plastic':
        result1= 4
    elif var == 'trash':
        result1 = 5
    return result1
def load_image_by_name(imageName: str):
    basePath = "dataset-resized/"
    img_path = basePath + imageName
    img = load_img(img_path, target_size=(300, 300))
    img = img_to_array(img, dtype=np.uint8)
    img=np.array(img)/255.0
    return img
class ModelExplainerInterface():
    def load_image_by_image_name(self, image_name: str):
        img = load_image_by_name(image_name)
        print(img)
        label_name, label_class = self.get_class_from_name(image_name)
        return img, label_name, label_class

    def load_image_by_test_data_index(self, generator, test_data_index: int):
        imgs = []
        img_path = "data-resized/"
        names = []
        for name in test_generator.filenames:
            img = load_img(img_path + name, target_size=(300, 300, 3))
            img = img_to_array(img, dtype=np.uint8)

            img = np.array(img) / 255.0

            names.append(name)
        imgs.append(img[np.newaxis, ...])

        return imgs, names

    def get_class_from_name(self, image_name: str):
        label_name = image_name.split('/')[0]
        label_class = list(labels.keys())[list(labels.values()).index(label_name)]
        return label_name, label_class

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)
#########################################################
class_names = ['Cardboard', 'Glass', 'Metal', 'Paper', 'Plastic','Trash']
#def upload_model(model: h5py.File):
    # model = tf.keras.applications.MobileNetV2(weights="imagenet")
#    mymodel = tf.keras.models.load_model(model)
#    print("Model loaded")
#    return model
#mymodel = upload_model()
def load_model():
    #model = tf.keras.applications.MobileNetV2(weights="imagenet")
    model= tf.keras.models.load_model('trained_model.h5')
    print("Model loaded")
    model.summary()
    return model
model = load_model()
def predict(image: Image.Image):
    #image = np.asarray(image.resize((224, 224)))[..., :3]####RGB Image -> 224*224
    #image = np.expand_dims(image, 0)
    #image = image / 127.5 - 1.0
    print("predicting...")
    image = np.asarray(image.resize((300, 300)))[..., :3]
    image = np.expand_dims(image, 0)
    image = image/255.0
    p = model.predict(image)
    cName = class_names[(np.argmax(p[0],axis=-1))]
    response = []
    #resp = {}
    prob = str(np.max(p[0], axis=-1))
    response.append(cName)
    response.append(prob)
    return response
    #return response
    #response.append(prob)
    #return a
    #response.append(resp)
    #return resp
    #res = {}
    #return resp

#    result = decode_predictions(model.predict(image), 2)[0]
#    response = []
#    for i, res in enumerate(result):
#        resp = {}
#        resp["class"] = res[1]
#        resp["confidence"] = f"{res[2]*100:0.2f} %"
#        response.append(resp)
 #   return response
def read_imagefile(file) -> Image.Image:
    image = Image.open(BytesIO(file))
    return image

########################### READ MODEL #################################
#def read_model(file) -> h5py.File:
#    mymodel = h5py.File(BytesIO(file))
#    print(type(mymodel))
#    return mymodel
#########################################################################
##from here added for LIME
def explain_lime(image: Image.Image):
    explainer = lime_image.LimeImageExplainer()
    image = np.asarray(image.resize((300, 300)))[..., :3]
    #image = np.expand_dims(image, 0)
    image = image / 127.5 - 1.0
    explanation = explainer.explain_instance(image, model.predict,
                                             top_labels=5, hide_color=0, num_samples=1000)
    print("Top labels " + str(explanation.top_labels))
    temp_2, mask_2 = explanation.get_image_and_mask(explanation.top_labels[0], positive_only=False, num_features=10,
                                                    hide_rest=False)
    print(temp_2.shape)
    print(mask_2.shape)
    #ax1 = plt.subplot(1,1,1)
    #print(type(fig))
    #print(type(ax1))
    encodedNumpyData = json.dumps(temp_2, cls=NumpyArrayEncoder)
    plt.figure()
    plt.title(label='Lime explanation')
    #ax1.imshow(mark_boundaries(temp_2, mask_2))
    plt.imshow(temp_2)
    plt.show()
    #print(temp_2)
    #print(temp_2*255)
    #ax1.axis('off')
    return encodedNumpyData

class ShapModelExplainer(ModelExplainerInterface):
    def explain_image_by_image_name(self, image_name: str):
        img, label_name, label_class = super(ShapModelExplainer, self).load_image_by_image_name(image_name)
        img = img[np.newaxis, ...]
        shap_values = self.explain_shap(img)
        print(type(label_class))
        self.plot_explanations(shap_values, img)

    def explain_image_by_test_data_index(self, generator, index: int):
        img = self.load_image_by_test_data_index(test_generator, index)

        temp, mask = self.explain_shap(img)
        self.plot_explanations(temp, mask)

    def build_background_for_computing(self, generator):
        background_imgs = []
        for name in generator.filenames:
            img, label_name, label_class = super(ShapModelExplainer, self).load_image_by_image_name(name)
            background_imgs.append(img[np.newaxis, ...])

        return background_imgs

    def explain_shap(self, image: Image.Image):
        #print("Explaining with SHAP")
        image = np.asarray(image.resize((300, 300)))[..., :3]
        image = np.expand_dims(image, 0)
        image = image / 255.0
        p = model.predict(image)
        print(p)
        # DeepExplainer to explain predictions of the model
        background_imgs = self.build_background_for_computing(test_generator)
        explainer = shap.DeepExplainer(model,background_imgs)  # compute shap values
        shap_values = explainer.shap_values(image, check_additivity=False)
        encodedNumpyData = json.dumps(shap_values, cls=NumpyArrayEncoder)
        self.plot_explanations(shap_values, image)
        return encodedNumpyData
    def plot_explanations(self,shap_values, img):
        shap.image_plot(shap_values, img, labels=list(labels.values()), show=False)
        #plt.title('Shap Explanation')
        plt.show()

# class OcclusionSensitityModelExplainer(ModelExplainerInterface):
#
#     def explain_occlusion(self,image: Image.Image,label):
#         image = np.asarray(image.resize((300, 300)))[..., :3]
#         image = np.expand_dims(image, 0)
#         image = image / 255.0
#         print("Explaining with Occlusion Sensitivity")
#         explained_img_name = 'TESTNAME.png'
#         explainer = OcclusionSensitivity()
#         data = (image, label)
#         grid = explainer.explain(data, model, label, patch_size=15, colormap=cv2.COLORMAP_TURBO)  #
#         print(grid.shape)
#         explainer.save(grid, ".", explained_img_name)
#         self.plot_explanations(explained_img_name)
#         #return grid, explained_img_name
#         encodedNumpyData = json.dumps(grid, cls=NumpyArrayEncoder)
#         return encodedNumpyData
#
#     def plot_explanations(self, img_name):
#         img = plt.imread(img_name)
#         plt.figure(figsize=(6, 6))
#         plt.imshow(img)
#         plt.axis('off')
#         plt.title('Occlusion Sensitivity')
#         plt.show()

