## To start the app
#from website import create_app
from website import *
from website.models import *

#
if __name__ == '__main__':
    app = create_app()
    #create_Flat_table()
    #db.create_all(app=app)
    app.run(debug=True)


