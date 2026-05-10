"""
Location Service for Phase 4
Handles interactions with GeoDB Cities, OpenTripMap, and Unsplash APIs.
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

class LocationService:
    _cache = {}

    @staticmethod
    def _get_api_keys():
        return {
            'geodb': os.getenv('GEODB_API_KEY'),
            'opentripmap': os.getenv('OPENTRIPMAP_API_KEY'),
            'unsplash': os.getenv('UNSPLASH_API_KEY')
        }

    @staticmethod
    def search_cities(query):
        """Search for cities using GeoDB Cities API"""
        query = query.strip().lower()
        if query in LocationService._cache:
            return LocationService._cache[query]

        keys = LocationService._get_api_keys()
        api_key = keys['geodb']
        
        if not api_key or api_key == 'your-geodb-api-key':
            logger.warning("GeoDB API Key missing, using mock data")
            return LocationService._mock_city_search(query)

        url = "https://geodb-cities-api.p.rapidapi.com/v1/geo/cities"
        querystring = {"namePrefix": query, "limit": "5", "sort": "-population"}
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "geodb-cities-api.p.rapidapi.com"
        }

        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            data = response.json()
            results = [
                {
                    'id': city['id'],
                    'name': city['city'],
                    'region': city['region'],
                    'country': city['country'],
                    'latitude': city['latitude'],
                    'longitude': city['longitude']
                } for city in data.get('data', [])
            ]
            LocationService._cache[query] = results
            return results
        except Exception as e:
            logger.error(f"GeoDB Search Error: {e}")
            return LocationService._mock_city_search(query)

    @staticmethod
    def get_attractions(lat, lon, radius=5000):
        """Get tourist attractions using OpenTripMap API"""
        keys = LocationService._get_api_keys()
        api_key = keys['opentripmap']

        if not api_key or api_key == 'your-opentripmap-api-key':
            logger.warning("OpenTripMap API Key missing, using mock data")
            return LocationService._mock_attractions(lat, lon)

        url = f"https://api.opentripmap.com/0.1/en/places/radius"
        params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "format": "json",
            "apikey": api_key,
            "kinds": "interesting_places,tourist_facilities"
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            # Filter and limit to 10 attractions
            return [
                {
                    'xid': place['xid'],
                    'name': place.get('name', 'Unnamed Place'),
                    'kinds': place.get('kinds', ''),
                    'latitude': place['point']['lat'],
                    'longitude': place['point']['lon'],
                    'dist': place.get('dist', 0)
                } for place in data if place.get('name')
            ][:10]
        except Exception as e:
            logger.error(f"OpenTripMap Error: {e}")
            return LocationService._mock_attractions(lat, lon)

    @staticmethod
    def get_city_image(city_name):
        """Fetch a city image from Unsplash"""
        keys = LocationService._get_api_keys()
        api_key = keys['unsplash']

        if not api_key or api_key == 'your-unsplash-api-key':
            return "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": f"{city_name} skyline",
            "per_page": 1,
            "client_id": api_key
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
        except Exception as e:
            logger.error(f"Unsplash Error: {e}")
        
        return "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

    # --- Mock Helpers ---
    @staticmethod
    def _mock_city_search(query):
        india_city_rows = [
            ('Agartala', 'Tripura', 23.8315, 91.2868),
            ('Agra', 'Uttar Pradesh', 27.1767, 78.0081),
            ('Ahmedabad', 'Gujarat', 23.0225, 72.5714),
            ('Aizawl', 'Mizoram', 23.7271, 92.7176),
            ('Ajmer', 'Rajasthan', 26.4499, 74.6399),
            ('Alappuzha', 'Kerala', 9.4981, 76.3388),
            ('Aligarh', 'Uttar Pradesh', 27.8974, 78.0880),
            ('Allahabad', 'Uttar Pradesh', 25.4358, 81.8463),
            ('Alwar', 'Rajasthan', 27.5530, 76.6346),
            ('Amaravati', 'Andhra Pradesh', 16.5417, 80.5150),
            ('Ambala', 'Haryana', 30.3782, 76.7767),
            ('Amravati', 'Maharashtra', 20.9374, 77.7796),
            ('Amritsar', 'Punjab', 31.6340, 74.8723),
            ('Anand', 'Gujarat', 22.5645, 72.9289),
            ('Anantapur', 'Andhra Pradesh', 14.6819, 77.6006),
            ('Asansol', 'West Bengal', 23.6739, 86.9524),
            ('Aurangabad', 'Maharashtra', 19.8762, 75.3433),
            ('Ayodhya', 'Uttar Pradesh', 26.7996, 82.2042),
            ('Bareilly', 'Uttar Pradesh', 28.3670, 79.4304),
            ('Belagavi', 'Karnataka', 15.8497, 74.4977),
            ('Bengaluru', 'Karnataka', 12.9716, 77.5946),
            ('Berhampore', 'West Bengal', 24.0983, 88.2679),
            ('Bhagalpur', 'Bihar', 25.2425, 86.9842),
            ('Bharatpur', 'Rajasthan', 27.2152, 77.5020),
            ('Bharuch', 'Gujarat', 21.7051, 72.9959),
            ('Bhatinda', 'Punjab', 30.2110, 74.9455),
            ('Bhavnagar', 'Gujarat', 21.7645, 72.1519),
            ('Bhilai', 'Chhattisgarh', 21.1938, 81.3509),
            ('Bhilwara', 'Rajasthan', 25.3463, 74.6364),
            ('Bhiwandi', 'Maharashtra', 19.3002, 73.0588),
            ('Bhopal', 'Madhya Pradesh', 23.2599, 77.4126),
            ('Bhubaneswar', 'Odisha', 20.2961, 85.8245),
            ('Bhuj', 'Gujarat', 23.2419, 69.6669),
            ('Bikaner', 'Rajasthan', 28.0229, 73.3119),
            ('Bilaspur', 'Chhattisgarh', 22.0796, 82.1391),
            ('Bokaro', 'Jharkhand', 23.6693, 86.1511),
            ('Brahmapur', 'Odisha', 19.3149, 84.7941),
            ('Chandigarh', 'Chandigarh', 30.7333, 76.7794),
            ('Chennai', 'Tamil Nadu', 13.0827, 80.2707),
            ('Coimbatore', 'Tamil Nadu', 11.0168, 76.9558),
            ('Cuttack', 'Odisha', 20.4625, 85.8828),
            ('Darbhanga', 'Bihar', 26.1522, 85.8971),
            ('Darjeeling', 'West Bengal', 27.0410, 88.2663),
            ('Davangere', 'Karnataka', 14.4644, 75.9218),
            ('Dehradun', 'Uttarakhand', 30.3165, 78.0322),
            ('Delhi', 'Delhi', 28.6139, 77.2090),
            ('Dhanbad', 'Jharkhand', 23.7957, 86.4304),
            ('Dharamshala', 'Himachal Pradesh', 32.2190, 76.3234),
            ('Dibrugarh', 'Assam', 27.4728, 94.9120),
            ('Dimapur', 'Nagaland', 25.9091, 93.7276),
            ('Durg', 'Chhattisgarh', 21.1904, 81.2849),
            ('Durgapur', 'West Bengal', 23.5204, 87.3119),
            ('Dwarka', 'Gujarat', 22.2442, 68.9685),
            ('Ernakulam', 'Kerala', 9.9816, 76.2999),
            ('Erode', 'Tamil Nadu', 11.3410, 77.7172),
            ('Faridabad', 'Haryana', 28.4089, 77.3178),
            ('Gandhinagar', 'Gujarat', 23.2156, 72.6369),
            ('Gangtok', 'Sikkim', 27.3389, 88.6065),
            ('Gaya', 'Bihar', 24.7955, 84.9994),
            ('Ghaziabad', 'Uttar Pradesh', 28.6692, 77.4538),
            ('Gorakhpur', 'Uttar Pradesh', 26.7606, 83.3732),
            ('Greater Noida', 'Uttar Pradesh', 28.4744, 77.5040),
            ('Gulbarga', 'Karnataka', 17.3297, 76.8343),
            ('Guntur', 'Andhra Pradesh', 16.3067, 80.4365),
            ('Gurugram', 'Haryana', 28.4595, 77.0266),
            ('Guwahati', 'Assam', 26.1445, 91.7362),
            ('Gwalior', 'Madhya Pradesh', 26.2183, 78.1828),
            ('Haridwar', 'Uttarakhand', 29.9457, 78.1642),
            ('Hisar', 'Haryana', 29.1492, 75.7217),
            ('Hubballi', 'Karnataka', 15.3647, 75.1240),
            ('Hyderabad', 'Telangana', 17.3850, 78.4867),
            ('Imphal', 'Manipur', 24.8170, 93.9368),
            ('Indore', 'Madhya Pradesh', 22.7196, 75.8577),
            ('Itanagar', 'Arunachal Pradesh', 27.0844, 93.6053),
            ('Jabalpur', 'Madhya Pradesh', 23.1815, 79.9864),
            ('Jaipur', 'Rajasthan', 26.9124, 75.7873),
            ('Jaisalmer', 'Rajasthan', 26.9157, 70.9083),
            ('Jalandhar', 'Punjab', 31.3260, 75.5762),
            ('Jalgaon', 'Maharashtra', 21.0077, 75.5626),
            ('Jammu', 'Jammu and Kashmir', 32.7266, 74.8570),
            ('Jamnagar', 'Gujarat', 22.4707, 70.0577),
            ('Jamshedpur', 'Jharkhand', 22.8046, 86.2029),
            ('Jhansi', 'Uttar Pradesh', 25.4484, 78.5685),
            ('Jodhpur', 'Rajasthan', 26.2389, 73.0243),
            ('Jorhat', 'Assam', 26.7509, 94.2037),
            ('Junagadh', 'Gujarat', 21.5222, 70.4579),
            ('Kakinada', 'Andhra Pradesh', 16.9891, 82.2475),
            ('Kalaburagi', 'Karnataka', 17.3297, 76.8343),
            ('Kalyan', 'Maharashtra', 19.2403, 73.1305),
            ('Kannur', 'Kerala', 11.8745, 75.3704),
            ('Kanpur', 'Uttar Pradesh', 26.4499, 80.3319),
            ('Kargil', 'Ladakh', 34.5539, 76.1349),
            ('Karimnagar', 'Telangana', 18.4386, 79.1288),
            ('Karnal', 'Haryana', 29.6857, 76.9905),
            ('Kasaragod', 'Kerala', 12.4996, 74.9869),
            ('Kathua', 'Jammu and Kashmir', 32.3693, 75.5254),
            ('Katni', 'Madhya Pradesh', 23.8343, 80.3894),
            ('Kavaratti', 'Lakshadweep', 10.5669, 72.6417),
            ('Khammam', 'Telangana', 17.2473, 80.1514),
            ('Kochi', 'Kerala', 9.9312, 76.2673),
            ('Kohima', 'Nagaland', 25.6751, 94.1086),
            ('Kolkata', 'West Bengal', 22.5726, 88.3639),
            ('Kollam', 'Kerala', 8.8932, 76.6141),
            ('Kota', 'Rajasthan', 25.2138, 75.8648),
            ('Kottayam', 'Kerala', 9.5916, 76.5222),
            ('Kozhikode', 'Kerala', 11.2588, 75.7804),
            ('Kurnool', 'Andhra Pradesh', 15.8281, 78.0373),
            ('Leh', 'Ladakh', 34.1526, 77.5771),
            ('Lucknow', 'Uttar Pradesh', 26.8467, 80.9462),
            ('Ludhiana', 'Punjab', 30.9010, 75.8573),
            ('Madurai', 'Tamil Nadu', 9.9252, 78.1198),
            ('Mangaluru', 'Karnataka', 12.9141, 74.8560),
            ('Mathura', 'Uttar Pradesh', 27.4924, 77.6737),
            ('Meerut', 'Uttar Pradesh', 28.9845, 77.7064),
            ('Moradabad', 'Uttar Pradesh', 28.8386, 78.7733),
            ('Motihari', 'Bihar', 26.6475, 84.9163),
            ('Mumbai', 'Maharashtra', 19.0760, 72.8777),
            ('Munnar', 'Kerala', 10.0889, 77.0595),
            ('Muzaffarpur', 'Bihar', 26.1209, 85.3647),
            ('Mysuru', 'Karnataka', 12.2958, 76.6394),
            ('Nadiad', 'Gujarat', 22.6916, 72.8634),
            ('Nagaon', 'Assam', 26.3480, 92.6840),
            ('Nagpur', 'Maharashtra', 21.1458, 79.0882),
            ('Nainital', 'Uttarakhand', 29.3803, 79.4636),
            ('Nanded', 'Maharashtra', 19.1383, 77.3210),
            ('Nashik', 'Maharashtra', 19.9975, 73.7898),
            ('Navi Mumbai', 'Maharashtra', 19.0330, 73.0297),
            ('Noida', 'Uttar Pradesh', 28.5355, 77.3910),
            ('Panaji', 'Goa', 15.4909, 73.8278),
            ('Patiala', 'Punjab', 30.3398, 76.3869),
            ('Patna', 'Bihar', 25.5941, 85.1376),
            ('Pimpri-Chinchwad', 'Maharashtra', 18.6298, 73.7997),
            ('Pondicherry', 'Puducherry', 11.9416, 79.8083),
            ('Port Blair', 'Andaman and Nicobar Islands', 11.6234, 92.7265),
            ('Prayagraj', 'Uttar Pradesh', 25.4358, 81.8463),
            ('Pudukkottai', 'Tamil Nadu', 10.3797, 78.8208),
            ('Pune', 'Maharashtra', 18.5204, 73.8567),
            ('Puri', 'Odisha', 19.8135, 85.8312),
            ('Raipur', 'Chhattisgarh', 21.2514, 81.6296),
            ('Rajahmundry', 'Andhra Pradesh', 17.0005, 81.8040),
            ('Rajkot', 'Gujarat', 22.3039, 70.8022),
            ('Ranchi', 'Jharkhand', 23.3441, 85.3096),
            ('Rourkela', 'Odisha', 22.2604, 84.8536),
            ('Rudrapur', 'Uttarakhand', 28.9875, 79.4141),
            ('Salem', 'Tamil Nadu', 11.6643, 78.1460),
            ('Sambalpur', 'Odisha', 21.4669, 83.9812),
            ('Sangli', 'Maharashtra', 16.8524, 74.5815),
            ('Satna', 'Madhya Pradesh', 24.6005, 80.8322),
            ('Shillong', 'Meghalaya', 25.5788, 91.8933),
            ('Shimla', 'Himachal Pradesh', 31.1048, 77.1734),
            ('Shivamogga', 'Karnataka', 13.9299, 75.5681),
            ('Siliguri', 'West Bengal', 26.7271, 88.3953),
            ('Silvassa', 'Dadra and Nagar Haveli and Daman and Diu', 20.2739, 73.0087),
            ('Srinagar', 'Jammu and Kashmir', 34.0837, 74.7973),
            ('Surat', 'Gujarat', 21.1702, 72.8311),
            ('Tezpur', 'Assam', 26.6528, 92.7926),
            ('Thane', 'Maharashtra', 19.2183, 72.9781),
            ('Thanjavur', 'Tamil Nadu', 10.7867, 79.1378),
            ('Thiruvananthapuram', 'Kerala', 8.5241, 76.9366),
            ('Thoothukudi', 'Tamil Nadu', 8.7642, 78.1348),
            ('Thrissur', 'Kerala', 10.5276, 76.2144),
            ('Tinsukia', 'Assam', 27.4898, 95.3599),
            ('Tiruchirappalli', 'Tamil Nadu', 10.7905, 78.7047),
            ('Tirunelveli', 'Tamil Nadu', 8.7139, 77.7567),
            ('Tirupati', 'Andhra Pradesh', 13.6288, 79.4192),
            ('Tiruppur', 'Tamil Nadu', 11.1085, 77.3411),
            ('Udaipur', 'Rajasthan', 24.5854, 73.7125),
            ('Ujjain', 'Madhya Pradesh', 23.1765, 75.7885),
            ('Vadodara', 'Gujarat', 22.3072, 73.1812),
            ('Varanasi', 'Uttar Pradesh', 25.3176, 82.9739),
            ('Vasai-Virar', 'Maharashtra', 19.3919, 72.8397),
            ('Vellore', 'Tamil Nadu', 12.9165, 79.1325),
            ('Vijayawada', 'Andhra Pradesh', 16.5062, 80.6480),
            ('Visakhapatnam', 'Andhra Pradesh', 17.6868, 83.2185),
            ('Warangal', 'Telangana', 17.9689, 79.5941),
            ('Yamunanagar', 'Haryana', 30.1290, 77.2800),
        ]

        mocks = [
            {
                'id': index + 1,
                'name': name,
                'region': region,
                'country': 'India',
                'latitude': lat,
                'longitude': lon
            }
            for index, (name, region, lat, lon) in enumerate(india_city_rows)
        ]
        normalized_query = query.lower()
        matches = [c for c in mocks if normalized_query in c['name'].lower() or normalized_query in c['region'].lower()]
        return sorted(matches, key=lambda city: (city['country'] != 'India', city['name']))[:12]

    @staticmethod
    def _mock_attractions(lat, lon):
        # Hyderabad specific mocks
        if 17.3 <= lat <= 17.5 and 78.4 <= lon <= 78.6:
            return [
                {'xid': 'h1', 'name': 'Charminar', 'kinds': 'historic', 'latitude': 17.3616, 'longitude': 78.4747},
                {'xid': 'h2', 'name': 'Golconda Fort', 'kinds': 'forts', 'latitude': 17.3833, 'longitude': 78.4011},
                {'xid': 'h3', 'name': 'Salar Jung Museum', 'kinds': 'museums', 'latitude': 17.3713, 'longitude': 78.4804},
                {'xid': 'h4', 'name': 'Hussain Sagar', 'kinds': 'lakes', 'latitude': 17.4239, 'longitude': 78.4738},
            ]
        
        # Delhi specific mocks
        if 28.5 <= lat <= 28.7 and 77.1 <= lon <= 77.3:
            return [
                {'xid': 'd1', 'name': 'Red Fort', 'kinds': 'historic', 'latitude': 28.6562, 'longitude': 77.2410},
                {'xid': 'd2', 'name': 'India Gate', 'kinds': 'monuments', 'latitude': 28.6129, 'longitude': 77.2295},
                {'xid': 'd3', 'name': 'Qutub Minar', 'kinds': 'historic', 'latitude': 28.5244, 'longitude': 77.1855},
            ]

        # Chennai specific mocks
        if 13.0 <= lat <= 13.1 and 80.2 <= lon <= 80.3:
            return [
                {'xid': 'c1', 'name': 'Marina Beach', 'kinds': 'beaches', 'latitude': 13.0445, 'longitude': 80.2824},
                {'xid': 'c2', 'name': 'Kapaleeshwarar Temple', 'kinds': 'temples', 'latitude': 13.0333, 'longitude': 80.2707},
            ]
        
        return [
            {'xid': 'm1', 'name': 'Famous Museum', 'kinds': 'museums', 'latitude': lat + 0.001, 'longitude': lon + 0.001},
            {'xid': 'm2', 'name': 'Grand Park', 'kinds': 'parks', 'latitude': lat - 0.001, 'longitude': lon - 0.001},
            {'xid': 'm3', 'name': 'Historic Tower', 'kinds': 'historic', 'latitude': lat + 0.002, 'longitude': lon - 0.002},
        ]
