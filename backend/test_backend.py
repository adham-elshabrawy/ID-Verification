#!/usr/bin/env python3
"""
Simple test script for the backend API
Run: python test_backend.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Testing Kiosk Backend API\n")
    print("=" * 50)
    
    # 1. Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("   ERROR: Cannot connect to backend. Is it running?")
        print("   Start with: uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    # 2. Register device
    print("\n2. Registering test device...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices/register",
            json={
                "device_id": "test-device-laptop-001",
                "location_name": "Test Office",
                "name": "Test Tablet"
            }
        )
        if response.status_code == 201:
            data = response.json()
            api_key = data["api_key"]
            print(f"   Status: {response.status_code}")
            print(f"   Device ID: {data['device_id']}")
            print(f"   Location: {data['location_name']}")
            print(f"   API Key: {api_key[:20]}...")
            
            # Save API key for subsequent requests
            headers = {"X-Device-API-Key": api_key}
            
            # 3. Get device info
            print("\n3. Getting device info...")
            response = requests.get(f"{BASE_URL}/api/devices/me", headers=headers)
            if response.status_code == 200:
                print(f"   Status: {response.status_code}")
                print(f"   Device Info: {json.dumps(response.json(), indent=2)}")
            
            # 4. Create test employee
            print("\n4. Creating test employee...")
            response = requests.post(
                f"{BASE_URL}/api/employees",
                headers=headers,
                json={
                    "location_id": data["location_id"],
                    "employee_id": "EMP001",
                    "name": "Test Employee",
                    "pin": "1234"
                }
            )
            if response.status_code == 201:
                emp_data = response.json()
                print(f"   Status: {response.status_code}")
                print(f"   Employee ID: {emp_data['employee_id']}")
                print(f"   Name: {emp_data['name']}")
                employee_id = emp_data["id"]
                
                # 5. Get employee state
                print("\n5. Getting employee state...")
                response = requests.get(
                    f"{BASE_URL}/api/employees/{employee_id}/state",
                    headers=headers
                )
                if response.status_code == 200:
                    state_data = response.json()
                    print(f"   Status: {response.status_code}")
                    print(f"   State: {state_data['state']}")
                
                # 6. Create time event (clock in)
                print("\n6. Creating clock-in event...")
                response = requests.post(
                    f"{BASE_URL}/api/time-events",
                    headers=headers,
                    json={
                        "employee_id": employee_id,
                        "event_type": "IN",
                        "method": "PIN"
                    }
                )
                if response.status_code == 201:
                    event_data = response.json()
                    print(f"   Status: {response.status_code}")
                    print(f"   Event Type: {event_data['event_type']}")
                    print(f"   Method: {event_data['method']}")
                
                # 7. Get clocked-in employees
                print("\n7. Getting clocked-in employees...")
                response = requests.get(
                    f"{BASE_URL}/api/time-events/clocked-in",
                    headers=headers
                )
                if response.status_code == 200:
                    clocked_in = response.json()
                    print(f"   Status: {response.status_code}")
                    print(f"   Clocked In Count: {len(clocked_in)}")
                    if clocked_in:
                        print(f"   Employees: {[e['name'] for e in clocked_in]}")
                
                # 8. Get admin stats
                print("\n8. Getting admin stats...")
                response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
                if response.status_code == 200:
                    stats = response.json()
                    print(f"   Status: {response.status_code}")
                    print(f"   Stats: {json.dumps(stats, indent=2)}")
                
            else:
                print(f"   ERROR: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"   ERROR: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("\nTest completed!")
    print("\nNext steps:")
    print("1. Open http://localhost:8000/docs for interactive API testing")
    print("2. Set up Android emulator or connect physical device")
    print("3. Update ApiClient.kt with: http://YOUR_IP:8000/api/")

if __name__ == "__main__":
    test_backend()

