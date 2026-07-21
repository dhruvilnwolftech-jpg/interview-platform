"""
Simple Backend Test - No WebSocket Required
Tests only REST API endpoints
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    response = requests.get(f'{BASE_URL}/api/health')
    assert response.status_code == 200
    print("✓ Health check passed")
    return True

def test_create_session():
    """Test session creation"""
    print("\n" + "="*60)
    print("TEST 2: Create Session")
    print("="*60)
    response = requests.post(
        f'{BASE_URL}/api/sessions',
        json={'support_person_id': 'sp-test-001'}
    )
    assert response.status_code == 201
    data = response.json()
    
    session_id = data['session_id']
    document_id = data['document_id']
    code = data['code']
    
    print(f"✓ Session created")
    print(f"  Code: {code}")
    print(f"  Session ID: {session_id}")
    print(f"  Document ID: {document_id}")
    
    return session_id, document_id, code

def test_verify_code(code):
    """Test code verification"""
    print("\n" + "="*60)
    print("TEST 3: Verify Session Code")
    print("="*60)
    response = requests.get(f'{BASE_URL}/api/sessions/{code}')
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Session verified")
    print(f"  Code matches: {code}")
    return True

def test_get_connections(session_id):
    """Test connection tracking"""
    print("\n" + "="*60)
    print("TEST 4: Get Connections")
    print("="*60)
    response = requests.get(
        f'{BASE_URL}/api/sessions/{session_id}/connections'
    )
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Connections retrieved")
    print(f"  Active count: {data['active_count']}")
    print(f"  Total connections: {len(data['all_connections'])}")
    return True

def test_get_history(document_id):
    """Test document history"""
    print("\n" + "="*60)
    print("TEST 5: Get Document History")
    print("="*60)
    response = requests.get(
        f'{BASE_URL}/api/documents/{document_id}/history'
    )
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Document history retrieved")
    print(f"  Changes: {len(data['changes'])}")
    return True

def test_admin_sessions():
    """Test admin sessions endpoint"""
    print("\n" + "="*60)
    print("TEST 6: Admin - Get All Sessions")
    print("="*60)
    response = requests.get(f'{BASE_URL}/api/admin/sessions')
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Admin sessions retrieved")
    print(f"  Total sessions: {len(data['sessions'])}")
    return True

def test_admin_document(document_id):
    """Test admin document endpoint"""
    print("\n" + "="*60)
    print("TEST 7: Admin - Get Document Details")
    print("="*60)
    response = requests.get(
        f'{BASE_URL}/api/admin/documents/{document_id}'
    )
    assert response.status_code == 200
    data = response.json()
    
    print(f"✓ Admin document retrieved")
    print(f"  Document ID: {data['id']}")
    print(f"  Change history: {len(data['change_history'])}")
    return True

def main():
    print("\n" + "="*80)
    print(" INTERVIEW PLATFORM - SIMPLE TEST SUITE (REST API ONLY) ".center(80))
    print("="*80)
    
    passed = 0
    failed = 0
    
    try:
        # Test 1
        if test_health():
            passed += 1
        
        # Test 2
        session_id, document_id, code = test_create_session()
        passed += 1
        
        # Test 3
        if test_verify_code(code):
            passed += 1
        
        # Test 4
        if test_get_connections(session_id):
            passed += 1
        
        # Test 5
        if test_get_history(document_id):
            passed += 1
        
        # Test 6
        if test_admin_sessions():
            passed += 1
        
        # Test 7
        if test_admin_document(document_id):
            passed += 1
        
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        failed += 1
    except Exception as e:
        print(f"✗ Test error: {e}")
        failed += 1
    
    print("\n" + "="*80)
    print(f" RESULTS: {passed} passed, {failed} failed ".center(80, "="))
    print("="*80 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
