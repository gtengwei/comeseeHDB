from conftest import *
import os

def test_diffPostalCode_review(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,"yeophuenyeo@gmail.com", "password123") # ==> user.postal_code = 190001

        #flat 0 postal_sector = 75
        rv = client.post('/flat-details/0', data={'review': "Love this neighbourhood! Near to MRT so I can sleep later before commuting to work :))"}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"You cannot review this flat! You can only review flats in your own postal district!" in rv.data

        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        print(context.keys())
        assert template.name == "home.html"
        template, context = captured_templates[1]
        print(context.keys())
        assert template.name == "flat_details.html"

def test_valid_review(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,"yeophuenyeo@gmail.com", "password123") # ==> user.postal_code = 534051

        #flat 3511 postal_code = 190001
        rv = client.post('/flat-details/3511', data={'review': "Love this neighbourhood! Near to MRT so I can sleep later before commuting to work :))"}, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Review added!" in rv.data
        assert b"Love this neighbourhood! Near to MRT so I can sleep later before commuting to work :))" in rv.data

        # COLLECTS templates from login() -> home.html and postreview -> flat_details.html
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        print(context.keys())
        assert template.name == "home.html"
        template, context = captured_templates[1]
        print(context.keys())
        assert template.name == "flat_details.html"

def test_more500word_review(client, captured_templates):
    """Tests a view that requires authentication"""
    from flask_login import current_user

    with client:
        login(client,"yeophuenyeo@gmail.com", "password123") # ==> user.postal_code = 534051
        
        cwd = Path(__file__).parent.absolute()
        os.chdir(cwd)
        #flat 3511 postal_code = 190001
        rv = client.post('/flat-details/3511', data={'review': open('532wordReview.txt', 'r').read().strip() }, follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200
        assert b"Review is too long! Maximum length for a review is 500 characters" in rv.data
        
        # COLLECTS templates from login() -> home.html and postreview -> flat_details.html
        assert len(captured_templates) == 2
        template, context = captured_templates[0]
        print(context.keys())
        assert template.name == "home.html"
        template, context = captured_templates[1]
        print(context.keys())
        assert template.name == "flat_details.html"
