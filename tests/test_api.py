"""
Test suite for Interview Platform Backend API
"""

import requests
import json
import time
from threading import Thread

BASE_URL = 'http://localhost:5000'


class TestAPI:
    """Test backend API endpoints"""
    
    def __init__(self):
        self.session_id = None
        self.document_id = None
        self.session_code = None
    
    def test_health(self):
        """Test health endpoint"""
        print("\n=== Testing Health Endpoint ===")
        response = requests.get(f'{BASE_URL}/api/health')
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Health check passed: {data}")
        return True
    
    def test_create_session(self):
        """Test session creation"""
        print("\n=== Testing Session Creation ===")
        response = requests.post(
            f'{BASE_URL}/api/sessions',
            json={'support_person_id': 'sp-001'}
        )
        assert response.status_code == 201
        data = response.json()
        
        self.session_id = data['session_id']
        self.document_id = data['document_id']
        self.session_code = data['code']
        
        print(f"✓ Session created")
        print(f"  Session ID: {self.session_id}")
        print(f"  Document ID: {self.document_id}")
        print(f"  Session Code: {self.session_code}")
        return True
    
    def test_verify_session(self):
        """Test session verification"""
        print("\n=== Testing Session Verification ===")
        response = requests.get(f'{BASE_URL}/api/sessions/{self.session_code}')
        assert response.status_code == 200
        data = response.json()
        
        assert data['session_id'] == self.session_id
        assert data['document_id'] == self.document_id
        
        print(f"✓ Session verified successfully")
        print(f"  Returned data: {json.dumps(data, indent=2)}")
        return True
    
    def test_invalid_code(self):
        """Test invalid session code"""
        print("\n=== Testing Invalid Session Code ===")
        response = requests.get(f'{BASE_URL}/api/sessions/INVALID')
        assert response.status_code == 404
        
        print(f"✓ Invalid code rejected correctly")
        return True
    
    def test_get_connections(self):
        """Test getting connections"""
        print("\n=== Testing Get Connections ===")
        response = requests.get(f'{BASE_URL}/api/sessions/{self.session_id}/connections')
        assert response.status_code == 200
        data = response.json()
        
        print(f"✓ Connections retrieved")
        print(f"  Active connections: {data['active_count']}")
        print(f"  Total connections: {len(data['all_connections'])}")
        return True
    
    def test_get_history(self):
        """Test getting document history"""
        print("\n=== Testing Document History ===")
        response = requests.get(f'{BASE_URL}/api/documents/{self.document_id}/history')
        assert response.status_code == 200
        data = response.json()
        
        print(f"✓ Document history retrieved")
        print(f"  Changes: {len(data['changes'])}")
        return True
    
    def test_get_admin_sessions(self):
        """Test admin sessions endpoint"""
        print("\n=== Testing Admin Sessions Endpoint ===")
        response = requests.get(f'{BASE_URL}/api/admin/sessions')
        assert response.status_code == 200
        data = response.json()
        
        print(f"✓ Admin sessions retrieved")
        print(f"  Total sessions: {len(data['sessions'])}")
        return True
    
    def test_get_admin_document(self):
        """Test admin document endpoint"""
        print("\n=== Testing Admin Document Endpoint ===")
        response = requests.get(f'{BASE_URL}/api/admin/documents/{self.document_id}')
        assert response.status_code == 200
        data = response.json()
        
        print(f"✓ Admin document retrieved")
        print(f"  Document ID: {data['id']}")
        print(f"  Created: {data['created_at']}")
        print(f"  Changes: {len(data['change_history'])}")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*50)
        print("INTERVIEW PLATFORM - API TEST SUITE")
        print("="*50)
        
        tests = [
            self.test_health,
            self.test_create_session,
            self.test_verify_session,
            self.test_invalid_code,
            self.test_get_connections,
            self.test_get_history,
            self.test_get_admin_sessions,
            self.test_get_admin_document,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test()
                passed += 1
            except Exception as e:
                print(f"✗ Test failed: {str(e)}")
                failed += 1
        
        print("\n" + "="*50)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("="*50 + "\n")
        
        return failed == 0


if __name__ == '__main__':
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(10):
        try:
            requests.get(f'{BASE_URL}/api/health', timeout=1)
            print("Server is ready!")
            break
        except:
            print(f"Attempt {i+1}/10...")
            time.sleep(1)
    
    # Run tests
    tester = TestAPI()
    success = tester.run_all_tests()
    
    exit(0 if success else 1)
