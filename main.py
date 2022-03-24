## To start the app
#from website import create_app
from db import open_connection
from website import app


#app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
