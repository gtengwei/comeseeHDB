## To start the app
#from website import create_app
from website import *
from website.models import *
from website.test import *

#
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


