from conftest import *
import json

# NO restriction on adding favourites of the same (flat_id, user_id) via POST request
def test_favourite(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,"yeophuenyeo@gmail.com", "password123")
        flatID = 3 #===> insert flatID that has not been favourited
        rv = client.post('/favourite', data=json.dumps( {'flatID': flatID}) )

        # session is still accessible
        assert rv.status_code == 200
        assert Favourites.query.filter_by(flat_id=flatID, user_id=current_user.id).first() is not None

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "home.html"
        

def test_unfavourite(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,"yeophuenyeo@gmail.com", "password123")
        # Find a favourite belonging to user
        favourite = Favourites.query.filter_by(user_id=current_user.id).first()
        favouriteID = favourite.flat_id
        rv = client.post('/unfavourite', data=json.dumps( {'favouriteID': favouriteID}) )

        # session is still accessible
        assert rv.status_code == 200
        assert Favourites.query.filter_by(flat_id=favouriteID, user_id=current_user.id).first() is None

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "home.html"
        