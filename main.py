#-------------------------------------------------------------------------------
import uvicorn
from fastapi.openapi.utils import get_openapi
import json
from aiofile import async_open
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, File, UploadFile,Depends, Form
from application import predict, read_imagefile, explain_lime#,read_model
from application import ShapModelExplainer
# from application import OcclusionSensitityModelExplainer
from application import get_ClassName
ShapExplainer = ShapModelExplainer()
# OcclusionExplainer = OcclusionSensitityModelExplainer()
####################FOR REQUEST BODY####################
from pydantic import BaseModel
description = """
xAI Microservices APIs helps you to understand the internal model structure and provide you explanation.
## Image Class Prediction Service

You can just pass an image to the Predict API and get prediction back as JSON

## LIME and SHAP Explainability Services

Just pass your image to the LIME Microservice and this service provide you the results in JSON

## Occlusion Sensitivity Explainability Service
* *Send Image True Label** (_cardboard,glass,metal,paper,plastic,trash_).
"""

# def create_application() -> FastAPI:
#     application = FastAPI(openapi_url="/building/openapi.json", docs_url="/building/docs")

#    application.include_router(create_building.router, prefix="/building", tags=["building"])
#    application.include_router(modify_building.router, prefix="/building", tags=["building"]
#    application.include_router(get_building.router, prefix="/building", tags=["building"])
#    application.include_router(get_buildings.router, prefix="/building", tags=["building"])
#     application.include_router(remove_building.router, prefix="/building", tags=["building"])
#     application.include_router(assign_users_to_building.router, prefix="/building", tags=["building"])
#     return application


# app = create_application()


app = FastAPI(
 openapi_url="/building/openapi.json",
 docs_url="/building/docs",
     title="XAI Microservices",
     description=description,
     version="0.0.1",
     terms_of_service="https://dps.cs.ut.ee/index.html",
     contact={
         "name": "Mehrdad Asadi, Ph.D.",
         "url": "https://dps.cs.ut.ee/people.html",
         "email": "mehrdad.asadi@ut.ee",
     },
     license_info={
         "name": "Apache 2.0",
         "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
     },
     servers=[{"url":"http://192.168.42.93"}], 
   # routes=app.routes,
)



#app = FastAPI()

#def my_schema():
#    if app.openapi_schema:
#        return app.openapi_schema
#    openapi_schema = get_openapi(
#        description="""testing""",
#        title="XAI Microservices",
#        terms_of_service="https://dps.cs.ut.ee/index.html",
#        version="0.0.1",
#        servers=[{"url": "http://192.168.42.93"}],
#        routes=app.routes,
#    )
#    app.openapi_schema = openapi_schema
#    return app.openapi_schema

#app.openapi = my_schema

#with open('openai.json', 'w') as f:
#  json.dump(app.openapi(), f)
@app.get("/test")
def read_root():
    print("GET api is running")
    return {"Hello": "World"}


@app.post("/predict/image")
async def predict_api(file: UploadFile = File(...)):
    print("POST api is running after asyncdef")
    extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_imagefile(await file.read())
    prediction = predict(image)
    return prediction

@app.post("/explain_lime/image") 
async def explain_api(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_imagefile(await file.read())
    explaination = explain_lime(image)
    return explaination

@app.post("/explain_shap/image")
async def explain_api(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_imagefile(await file.read())
    explaination = ShapExplainer.explain_shap(image)
    return explaination

# class ClassLabel(BaseModel):
#     imagetype: str
# @app.post("/explain_occlusion/image")
# async def explain_api(file: UploadFile = File(...), base:ClassLabel = Depends()):
#     extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
#     input = base.dict()
#     var = input['imagetype']
#     classNum = get_ClassName(var)
#     ####################### FIND CLASS ########################
#     if not extension:
#         return "Image must be jpg or png format!"
#     #label_number = get_ClassName(var)
#     var1 = 4
#     image = read_imagefile(await file.read())
#     explaination = OcclusionExplainer.explain_occlusion(image,classNum)
#     return explaination
#print(app.openapi())
#schema = app.openapi()

with open('openapi.json', 'w') as f:
  json.dump(app.openapi(), f)

if __name__ == "__main__":
    uvicorn.run(app, port=8080)
