## To start the app
#from website import create_app
from website import *
from website.models import *
from website.__init__ import app 
app = app
#
if __name__ == '__main__':
    #app = create_app()
    app.run(debug=True)