import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiService {
  // Dynamic base URL to handle both Emulator and Flutter Web
  static String get baseUrl => kIsWeb ? 'http://127.0.0.1:8000/api/v1' : 'http://10.0.2.2:8000/api/v1';

  // Singleton pattern for uniform use
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  // Helper method for error handling
  dynamic _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isNotEmpty) {
        return json.decode(response.body);
      }
      return null;
    } else {
      throw Exception('API Error: ${response.statusCode} - ${response.body}');
    }
  }

  // Hardcoded Mock Database
  static final List<Map<String, String>> _mockDoctors = [
    {'identifier': 'dr.smith@medrag.com', 'password': 'password123', 'name': 'Dr. Smith', 'id': 'd1'},
    {'identifier': 'dr.jones@medrag.com', 'password': 'password123', 'name': 'Dr. Jones', 'id': 'd2'},
    {'identifier': '1234567890', 'password': 'password123', 'name': 'Dr. Patel', 'id': 'd3'},
  ];

  static final List<Map<String, String>> _mockPatients = [
    {'identifier': 'john.doe@email.com', 'password': 'password123', 'name': 'John Doe', 'id': 'JD123456', 'role': 'patient'},
    {'identifier': 'jane.smith@email.com', 'password': 'password123', 'name': 'Jane Smith', 'id': 'JS654321', 'role': 'patient'},
    {'identifier': '0987654321', 'password': 'password123', 'name': 'Bob User', 'id': 'BU112233', 'role': 'patient'},
    {'identifier': 'alice.w@email.com', 'password': 'password123', 'name': 'Alice Wong', 'id': 'AW998877', 'role': 'patient'},
    {'identifier': 'mike.j@email.com', 'password': 'password123', 'name': 'Mike Johnson', 'id': 'MJ554433', 'role': 'patient'},
    {'identifier': 'sarah.c@email.com', 'password': 'password123', 'name': 'Sarah Connor', 'id': 'SC223344', 'role': 'patient'},
    {'identifier': 'david.b@email.com', 'password': 'password123', 'name': 'David Banner', 'id': 'DB776655', 'role': 'patient'},
    {'identifier': 'emily.r@email.com', 'password': 'password123', 'name': 'Emily Rose', 'id': 'ER009988', 'role': 'patient'},
  ];

  // Login with role
  Future<Map<String, dynamic>> login({
    required String identifier, // Email or Contact Number
    required String password,
    required String role, // 'patient' or 'doctor'
  }) async {
    await Future.delayed(const Duration(milliseconds: 800));
    
    // Strict Mock DB Validation
    if (role == 'doctor') {
      final doc = _mockDoctors.where((u) => u['identifier'] == identifier).firstOrNull;
      if (doc == null) {
        throw Exception('Doctor profile not found in database.');
      } else if (doc['password'] != password) {
        throw Exception('Wrong login credentials for Doctor.');
      }
      return {'status': 'success', 'user_id': doc['id'], 'email': doc['identifier'], 'name': doc['name'], 'role': role};
    } else {
      final pat = _mockPatients.where((u) => u['identifier'] == identifier).firstOrNull;
      if (pat == null) {
        throw Exception('Patient not found in database.');
      } else if (pat['password'] != password) {
        throw Exception('Wrong login credentials for Patient.');
      }
      return {'status': 'success', 'user_id': pat['id'], 'email': pat['identifier'], 'name': pat['name'], 'role': role};
    }
  }

  // Register Patient (Mock)
  Future<Map<String, dynamic>> register({
    required String patientId,
    required String firstName,
    required String lastName,
    required String email,
    required String contactNumber,
    required String password,
    required String dob,
    required String age,
    required String gender,
    required String height,
    required String weight,
    required String smokingStatus,
    required String drinkingStatus,
    required String lifestyleOther,
    required String pastConditions,
    required String surgeries,
    required String familyHistory,
    required String allergies,
    required String medications,
    required String physicianName,
  }) async {
    await Future.delayed(const Duration(milliseconds: 1500));
    
    // Add to mock patient database
    _mockPatients.add({
      'identifier': email.isNotEmpty ? email : contactNumber,
      'password': password,
      'name': '$firstName $lastName',
      'id': patientId,
      'role': 'patient'
    });

    return {
      'status': 'success',
      'user_id': patientId,
      'email': email,
      'role': 'patient'
    };
  }

  // Generate Report (Multimodal implementation)
  Future<Map<String, dynamic>> generateReport(String query, {List<int>? imageBytes, String? filename}) async {
    var uri = Uri.parse('$baseUrl/rag/generate-report');
    var request = http.MultipartRequest('POST', uri);

    request.fields['query'] = query;
    request.fields['patient_id'] = "1";

    if (imageBytes != null && filename != null) {
      var multipartFile = http.MultipartFile.fromBytes(
        'image',
        imageBytes,
        filename: filename,
        contentType: MediaType('image', 'jpeg'), // Simplified content type for prototype
      );
      request.files.add(multipartFile);
    }

    try {
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      return _handleResponse(response);
    } catch (e) {
      // Prototype Fallback: If backend is unreachable, gracefully return a mock report.
      await Future.delayed(const Duration(seconds: 2));
      return {
        "status": "success",
        "diagnosis": "Mock Fallback Diagnosis: Potential localized inflammation or muscular strain based on observed patient metrics. Recommended rest, hydration, and NSAIDs as needed.",
        "evidences": [
          "Clinical Trial 1032 indicates 85% efficacy for standard NSAID protocol in similar strain patterns.",
          "Image analysis (simulated): No apparent fractures. Soft tissue slightly elevated."
        ]
      };
    }
  }

  // Chat with AI
  Future<Map<String, dynamic>> chat(String message, String patientId) async {
    var uri = Uri.parse('$baseUrl/chat/?message=${Uri.encodeComponent(message)}&patient_id=$patientId');
    try {
      var response = await http.post(uri);
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Chat Failed: $e');
    }
  }

  // Get Reports / Patient History
  Future<Map<String, dynamic>> getReports(String patientId) async {
    var uri = Uri.parse('$baseUrl/patient/$patientId/history');
    try {
      var response = await http.get(uri);
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Get Reports Failed: $e');
    }
  }

  // Generic file upload wrapper
  Future<Map<String, dynamic>> uploadFile(List<int> bytes, String filename) async {
    var uri = Uri.parse('$baseUrl/upload/record');
    var request = http.MultipartRequest('POST', uri);
    
    var multipartFile = http.MultipartFile.fromBytes(
      'file',
      bytes,
      filename: filename,
    );
    request.files.add(multipartFile);

    try {
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Upload File Failed: $e');
    }
  }
}
