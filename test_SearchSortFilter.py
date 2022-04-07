from conftest import *

def test_Search(client, captured_templates):

    with client:
        search = "%{}%".format("beach rd") #===> insert search input
        #can POST request to views.home too
        rv = client.post(url_for('views.search',address=search), data={'search': search , 'amenity': [], 'flat_type': [], 'town': [], 'price': []},follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "search.html"
        expected = Flat.query.filter(Flat.address.like(search))
        assert expected.count() == context['data_length'] # ===> expected no.of results = actual
        
        # create list of first 10 flats shown in response
        actual = []
        i = 0
        while i < 10:
            actual.append(context['flats'][i].id)
            i+=1

        #check first 10 flats shown in response is expected
        assert set(actual).issubset( set([id[0] for id in expected.with_entities(Flat.id).all()]) )

def test_get_Sort(client, captured_templates):
    ''' CRITERIA (only 1 at anytime):

            price_high              price_low
            remaining_lease_high    remaining_lease_low
            storey_high             storey_low
            price_per_sqm_high      price_per_sqm_low
            favourites_high         favourites_low
    '''
    with client:
        criteria = "price_high" #===> insert sort criteria
        rv = client.get(url_for('views.sort',criteria=criteria))

        # session is still accessible
        assert rv.status_code == 200

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "home.html"
        flats = Flat.query.order_by(Flat.resale_price.desc()) #===> order by sort criteria
        
        print(context['session'])
        
        # create list of first 10 flats shown in response
        actual = []
        i = 0
        while i < 10:
            actual.append(context['flats'][i].id)
            i+=1

        #check first 10 flats shown in response is expected
        assert set(actual).issubset( set([id[0] for id in flats.with_entities(Flat.id).all()]) )

def test_Home_Filter(client, captured_templates):
    '''
        price_range
        town
        flat_type
        amenity
    '''
    with client:
        address = "%{}%".format("")
        flat_types = ['5 ROOM']
        amenities = []
        towns = ['SENGKANG']
        price_range = ['700000-800000']
        rv = client.post(url_for('views.home'), data={'search': address,'amenity': amenities, 'flat_type': flat_types, 'town': towns, 'price': price_range},follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "search.html"
        
        # filter by conditions
        expected = Flat.query.filter(Flat.address.like(address), Flat.flat_type.in_(flat_types), Flat.town.in_(towns), Flat.resale_price.between(700000, 800000)) 
        assert expected.count() == context['data_length'] # ===> expected no.of results = actual
        print(context['session'])
        
        # create list of first 10 flats shown in response
        actual = []
        i = 0
        while i < 10:
            actual.append(context['flats'][i].id)
            i+=1

        #check first 10 flats shown in response is expected
        assert set(actual).issubset( set([id[0] for id in expected.with_entities(Flat.id).all()]) )

# FAILED ====> filter.html is not updated ======> suggest to remove it completely
def test_Filter(client, captured_templates):
    '''
        price_range
        town
        flat_type
        amenity
    '''
    with client:
        address = "%{}%".format("")
        flat_types = ['5 ROOM']
        amenities = []
        towns = ['SENGKANG']
        price_range = ['700000-800000']
        rv = client.post(url_for('views.filter'), data={'amenity': amenities, 'flat_type': flat_types, 'town': towns, 'price': price_range},follow_redirects=True)

        # session is still accessible
        assert rv.status_code == 200

        assert len(captured_templates) == 1
        template, context = captured_templates[0]
        assert template.name == "filter.html"
        
        # filter by conditions
        expected = Flat.query.filter(Flat.flat_type.in_(flat_types), Flat.town.in_(towns),Flat.resale_price.between(700000, 800000)) 
        
        print(context.keys())
        
        # create list of first 10 flats shown in response
        actual = []
        i = 0
        while i < 10:
            actual.append(context['flats'][i].id)
            i+=1
        print(actual)
        print([id[0] for id in expected.with_entities(Flat.id).all()])
        #check first 10 flats shown in response is expected
        assert set(actual).issubset( set([id[0] for id in expected.with_entities(Flat.id).all()]) )