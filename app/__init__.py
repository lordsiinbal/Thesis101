from flask import Flask
from flask_cors import CORS

# print(sys.path)

from app.Controllers.InsertController import post
from app.Controllers.FetchController import get
from app.Controllers.UpdateController import put
from app.Controllers.DeleteController import delete


from .database import db
 
def create_app(config_file = 'settings.py'):
    print("hellow ")
    app =Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config["MONGODB_HOST"]= 'mongodb+srv://topetope:topetope1024_@cluster0.hicig.mongodb.net/db_detectCore?retryWrites=true&w=majority'
    # app.config["MONGODB_HOST"]='localhost:27017/db_detectCore'
    app.config.from_pyfile(config_file)
    db.init_app(app)
    app.register_blueprint(post)
    app.register_blueprint(get)
    app.register_blueprint(put)
    app.register_blueprint(delete)
    
    return app