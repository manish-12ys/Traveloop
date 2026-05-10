import os
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.trip import Trip
from app.models.stop import Stop
from app.models.activity import Activity

app = create_app('development')

with app.app_context():
    # 1. Create a dummy user for community plans if it doesn't exist
    author = User.query.filter_by(username='travel_guru').first()
    if not author:
        author = User(username='travel_guru', email='guru@traveloop.com', is_admin=False)
        author.set_password('password123')
        db.session.add(author)
        db.session.commit()

    # Clean up previous dummy trips
    Trip.query.filter_by(user_id=author.id).delete()
    db.session.commit()

    # 2. Define trips
    plans = [
        {
            'title': 'Golden Triangle Tour',
            'destination': 'Delhi, Agra, Jaipur, India',
            'description': 'A 7-day cultural immersion experiencing the Taj Mahal, Amber Fort, and the bustling streets of Old Delhi.',
            'start_date': datetime.now().date() + timedelta(days=30),
            'end_date': datetime.now().date() + timedelta(days=37),
            'status': 'completed',
            'budget': 50000,
            'image_url': '/static/img/community/delhi.png',
            'is_public': True,
            'stops': [
                {'name': 'Delhi', 'location': 'New Delhi, DL, India', 'days_offset': 0, 'duration': 2},
                {'name': 'Agra', 'location': 'Agra, UP, India', 'days_offset': 2, 'duration': 2},
                {'name': 'Jaipur', 'location': 'Jaipur, RJ, India', 'days_offset': 4, 'duration': 3}
            ],
            'activities': [
                {'title': 'Red Fort Visit', 'stop_idx': 0, 'cost': 500, 'description': 'Explore the historic Red Fort.'},
                {'title': 'Taj Mahal Sunrise', 'stop_idx': 1, 'cost': 1300, 'description': 'Witness the sunrise at Taj Mahal.'},
                {'title': 'Amber Fort Tour', 'stop_idx': 2, 'cost': 1000, 'description': 'Elephant ride and tour of Amber Fort.'}
            ]
        },
        {
            'title': 'Goa Beach Retreat',
            'destination': 'Goa, India',
            'description': 'Relaxing on the pristine beaches of South Goa, enjoying seafood, and visiting historic Portuguese churches.',
            'start_date': datetime.now().date() + timedelta(days=45),
            'end_date': datetime.now().date() + timedelta(days=50),
            'status': 'planning',
            'budget': 25000,
            'image_url': '/static/img/community/goa.png',
            'is_public': True,
            'stops': [
                {'name': 'North Goa', 'location': 'Baga Beach, Goa, India', 'days_offset': 0, 'duration': 3},
                {'name': 'South Goa', 'location': 'Palolem Beach, Goa, India', 'days_offset': 3, 'duration': 2}
            ],
            'activities': [
                {'title': 'Baga Beach Water Sports', 'stop_idx': 0, 'cost': 2500, 'description': 'Parasailing and jet ski.'},
                {'title': 'Basilica of Bom Jesus', 'stop_idx': 0, 'cost': 0, 'description': 'Historic church visit in Old Goa.'},
                {'title': 'Palolem Sunset Cruise', 'stop_idx': 1, 'cost': 1500, 'description': 'Evening boat ride.'}
            ]
        },
        {
            'title': 'Classic Europe: Paris & Rome',
            'destination': 'Paris & Rome',
            'description': 'A romantic getaway featuring the Eiffel Tower, Louvre, Colosseum, and authentic Italian pasta.',
            'start_date': datetime.now().date() + timedelta(days=100),
            'end_date': datetime.now().date() + timedelta(days=110),
            'status': 'planning',
            'budget': 150000,
            'image_url': '/static/img/community/paris.png',
            'is_public': True,
            'stops': [
                {'name': 'Paris', 'location': 'Paris, France', 'days_offset': 0, 'duration': 5},
                {'name': 'Rome', 'location': 'Rome, Italy', 'days_offset': 5, 'duration': 5}
            ],
            'activities': [
                {'title': 'Eiffel Tower', 'stop_idx': 0, 'cost': 2500, 'description': 'Access to the top floor.'},
                {'title': 'Louvre Museum', 'stop_idx': 0, 'cost': 1800, 'description': 'Seeing the Mona Lisa.'},
                {'title': 'Colosseum Tour', 'stop_idx': 1, 'cost': 2000, 'description': 'Guided tour of the Colosseum and Roman Forum.'},
                {'title': 'Vatican City', 'stop_idx': 1, 'cost': 3000, 'description': 'Sistine Chapel and St. Peter Basilica.'}
            ]
        },
        {
            'title': 'Tokyo Neon & Tradition',
            'destination': 'Tokyo, Japan',
            'description': 'Exploring the contrast between neon-lit Akihabara and the historic temples of Asakusa. Sushi included!',
            'start_date': datetime.now().date() + timedelta(days=120),
            'end_date': datetime.now().date() + timedelta(days=127),
            'status': 'planning',
            'budget': 120000,
            'image_url': 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?q=80&w=2868&auto=format&fit=crop',
            'is_public': True,
            'stops': [
                {'name': 'Shibuya', 'location': 'Shibuya City, Tokyo, Japan', 'days_offset': 0, 'duration': 3},
                {'name': 'Asakusa', 'location': 'Asakusa, Tokyo, Japan', 'days_offset': 3, 'duration': 4}
            ],
            'activities': [
                {'title': 'Shibuya Crossing', 'stop_idx': 0, 'cost': 0, 'description': 'Walk the famous crossing.'},
                {'title': 'Meiji Shrine', 'stop_idx': 0, 'cost': 0, 'description': 'Peaceful shrine in the city.'},
                {'title': 'Senso-ji Temple', 'stop_idx': 1, 'cost': 500, 'description': 'Historic temple visit.'},
                {'title': 'Tsukiji Outer Market', 'stop_idx': 1, 'cost': 3000, 'description': 'Fresh sushi breakfast.'}
            ]
        },
        {
            'title': 'New York City Highlights',
            'destination': 'New York, USA',
            'description': 'Times Square, Central Park, Broadway shows, and pizza slices in the city that never sleeps.',
            'start_date': datetime.now().date() + timedelta(days=200),
            'end_date': datetime.now().date() + timedelta(days=207),
            'status': 'planning',
            'budget': 200000,
            'image_url': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?q=80&w=2940&auto=format&fit=crop',
            'is_public': True,
            'stops': [
                {'name': 'Manhattan', 'location': 'Manhattan, NY, USA', 'days_offset': 0, 'duration': 7}
            ],
            'activities': [
                {'title': 'Statue of Liberty', 'stop_idx': 0, 'cost': 2000, 'description': 'Ferry and access to pedestal.'},
                {'title': 'Central Park Walk', 'stop_idx': 0, 'cost': 0, 'description': 'Stroll through the park.'},
                {'title': 'Broadway Show', 'stop_idx': 0, 'cost': 10000, 'description': 'Watch a hit musical.'},
                {'title': 'Empire State Building', 'stop_idx': 0, 'cost': 3500, 'description': 'Observation deck view.'}
            ]
        }
    ]

    # Insert trips
    added_count = 0
    for plan in plans:
        new_trip = Trip(
            user_id=author.id,
            title=plan['title'],
            destination=plan['destination'],
            description=plan['description'],
            start_date=plan['start_date'],
            end_date=plan['end_date'],
            status=plan['status'],
            budget=plan['budget'],
            image_url=plan['image_url'],
            is_public=plan['is_public']
        )
        db.session.add(new_trip)
        db.session.flush() # To get new_trip.id
        
        # Add stops
        stops = []
        for i, stop_data in enumerate(plan['stops']):
            arrival = new_trip.start_date + timedelta(days=stop_data['days_offset'])
            departure = arrival + timedelta(days=stop_data['duration'])
            stop = Stop(
                trip_id=new_trip.id,
                name=stop_data['name'],
                location=stop_data['location'],
                arrival_date=arrival,
                departure_date=departure,
                order=i
            )
            db.session.add(stop)
            stops.append(stop)
            
        db.session.flush() # To get stop ids
        
        # Add activities
        for i, act_data in enumerate(plan['activities']):
            stop = stops[act_data['stop_idx']]
            activity = Activity(
                trip_id=new_trip.id,
                stop_id=stop.id,
                title=act_data['title'],
                description=act_data['description'],
                cost=act_data['cost'],
                order=i
            )
            db.session.add(activity)
            
        added_count += 1
    
    db.session.commit()
    print(f"Successfully added {added_count} detailed community trips with stops and activities!")
