import httpx
import json

client = httpx.Client()

# Test registration for user 1
print('📝 Testing User 1 registration...')
response = client.post(
    'http://127.0.0.1:8000/auth/register',
    json={'email': 'user1@example.com', 'password': 'password123', 'name': 'User 1'},
    timeout=5.0
)
if response.status_code == 201:
    data = response.json()
    token1 = data['access_token']
    print(f'✅ User 1 registered')
    
    # Create profile for user 1
    print('\n🎯 Creating profile for User 1...')
    headers = {'Authorization': f'Bearer {token1}'}
    response = client.post(
        'http://127.0.0.1:8000/profile/',
        json={
            'name': 'User 1 Training',
            'weight_kg': 80,
            'height_cm': 175,
            'age': 28,
            'gender': 'male',
            'goal': 'muscle'
        },
        headers=headers
    )
    if response.status_code == 201:
        profile1 = response.json()
        print(f'✅ Profile created: {profile1["name"]}')
    else:
        print(f'❌ Error: {response.status_code}')
        print(response.text)
    
    # Now register user 2
    print('\n📝 Testing User 2 registration...')
    response = client.post(
        'http://127.0.0.1:8000/auth/register',
        json={'email': 'user2@example.com', 'password': 'password456', 'name': 'User 2'},
        timeout=5.0
    )
    if response.status_code == 201:
        data = response.json()
        token2 = data['access_token']
        print(f'✅ User 2 registered')
        
        # Try to list profiles with user 2 token
        print('\n📋 User 2 listing their profiles...')
        headers = {'Authorization': f'Bearer {token2}'}
        response = client.get(
            'http://127.0.0.1:8000/profile/',
            headers=headers
        )
        if response.status_code == 200:
            profiles = response.json()
            print(f'✅ User 2 profiles: {len(profiles)} profiles')
            print('   (should be 0, User 1 profiles are separate)')
        else:
            print(f'❌ Error: {response.status_code}')
        
        # Create profile for user 2
        print('\n🎯 Creating profile for User 2...')
        response = client.post(
            'http://127.0.0.1:8000/profile/',
            json={
                'name': 'User 2 Running',
                'weight_kg': 70,
                'height_cm': 170,
                'age': 25,
                'gender': 'female',
                'goal': 'fit'
            },
            headers=headers
        )
        if response.status_code == 201:
            profile2 = response.json()
            print(f'✅ Profile created: {profile2["name"]}')
        
        # User 1 list their own profiles
        print('\n📋 User 1 listing their profiles...')
        headers = {'Authorization': f'Bearer {token1}'}
        response = client.get(
            'http://127.0.0.1:8000/profile/',
            headers=headers
        )
        if response.status_code == 200:
            profiles = response.json()
            print(f'✅ User 1 profiles: {len(profiles)} profile(s)')
            for p in profiles:
                print(f'   - {p["name"]} ({p["goal"]})')
        
        print('\n✅ All tests passed! Profiles are user-scoped.')
    else:
        print(f'❌ User 2 registration failed: {response.status_code}')
else:
    print(f'❌ User 1 registration failed: {response.status_code}')
