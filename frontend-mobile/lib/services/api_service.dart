import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiService {
  // Dynamic base URL to handle both Emulator and Flutter Web
  static String get baseUrl =>
      kIsWeb ? 'http://127.0.0.1:8000/api/v1' : 'http://10.0.2.2:8000/api/v1';

  // Singleton pattern for uniform use
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  String? _accessToken;

  Map<String, String> get _headers {
    final headers = {'Content-Type': 'application/json'};
    if (_accessToken != null) {
      headers['Authorization'] = 'Bearer $_accessToken';
    }
    return headers;
  }

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

  // Login with role
  Future<Map<String, dynamic>> login({
    required String identifier,
    required String password,
    required String role,
  }) async {
    try {
      var uri = Uri.parse('$baseUrl/auth/login');
      var response = await http.post(
        uri,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': identifier,
          'password': password,
        },
      );

      var data = _handleResponse(response);
      _accessToken = data['access_token'];

      return {
        'status': 'success',
        'user_id': data['user_id'].toString(),
        'email': data['email'],
        'name': data['username'],
        'role': data['role'] ?? role,
        'sex': data['sex']
      };
    } catch (e) {
      debugPrint('Login failed: $e');
      throw Exception('Login failed. Please ensure the backend server is running and credentials are correct.');
    }
  }

  // Register Patient
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
    try {
      var uri = Uri.parse('$baseUrl/auth/register');
      var response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': email.isNotEmpty ? email : contactNumber,
          'email': email,
          'password': password,
          'role': 'patient'
        }),
      );

      var data = _handleResponse(response);
      _accessToken = data['access_token'];

      return {
        'status': 'success',
        'user_id': data['user_id'].toString(),
        'email': data['email'],
        'name': data['username'],
        'role': 'patient'
      };
    } catch (e) {
      debugPrint('Registration failed: $e');
      throw Exception('Registration failed. Please ensure the backend server is running.');
    }
  }

  void logout() {
    _accessToken = null;
  }

  // Generate Report
  Future<Map<String, dynamic>> generateReport(String query,
      {List<Map<String, dynamic>>? files}) async {
    var uri = Uri.parse('$baseUrl/rag/generate-report');
    var request = http.MultipartRequest('POST', uri);

    if (_accessToken != null) {
      request.headers['Authorization'] = 'Bearer $_accessToken';
    }

    request.fields['query'] = query;
    request.fields['patient_id'] = "1";

    if (files != null && files.isNotEmpty) {
      for (var f in files) {
        var multipartFile = http.MultipartFile.fromBytes(
          'files',
          f['bytes'] as List<int>,
          filename: f['name'] as String,
        );
        request.files.add(multipartFile);
      }
    }

    try {
      // RAG pipeline can take several minutes – use a 10 minute timeout
      var streamedResponse = await request.send()
          .timeout(const Duration(minutes: 10));
      var response = await http.Response.fromStream(streamedResponse)
          .timeout(const Duration(minutes: 10));

      // _handleResponse will throw on non-2xx. Propagate that directly.
      return _handleResponse(response);
    } catch (e) {
      debugPrint('Report generation failed: $e');
      throw Exception('Backend unavailable. Please ensure the server is running for AI-powered diagnostics.');
    }
  }

  // Chat with AI
  Future<Map<String, dynamic>> chat(String message, String patientId) async {
    var uri = Uri.parse('$baseUrl/chat/');
    try {
      var response = await http.post(uri,
          headers: _headers,
          body: json.encode({
            'message': message,
            'patient_id':
                patientId != 'unknown' ? int.tryParse(patientId) : null
          }));
      return _handleResponse(response);
    } catch (e) {
      debugPrint('Chat failed: $e');
      throw Exception("I'm having trouble connecting to the backend. Please ensure the server is running.");
    }
  }

  // Get Reports / Patient History
  Future<Map<String, dynamic>> getReports(String patientId) async {
    var uri = Uri.parse('$baseUrl/patient/$patientId/history');
    try {
      var response = await http.get(uri, headers: _headers);
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Get Reports Failed: $e');
    }
  }

  // Generic file upload
  Future<Map<String, dynamic>> uploadFile(
      List<int> bytes, String filename) async {
    var uri = Uri.parse('$baseUrl/upload/record');
    var request = http.MultipartRequest('POST', uri);

    if (_accessToken != null) {
      request.headers['Authorization'] = 'Bearer $_accessToken';
    }

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

  // Appointments
  Future<Map<String, dynamic>> getPatientAppointments(String patientId) async {
    var uri = Uri.parse('$baseUrl/appointments/patient/$patientId');
    try {
      var response = await http.get(uri, headers: _headers);
      var data = _handleResponse(response);
      return {'status': 'success', 'data': data};
    } catch (e) {
      return {'status': 'success', 'data': []};
    }
  }

  Future<Map<String, dynamic>> getDoctorsBySpecialty(String specialty) async {
    var uri = Uri.parse('$baseUrl/doctors/specialty/$specialty');
    try {
      var response = await http.get(uri, headers: _headers);
      var data = _handleResponse(response);
      return {'status': 'success', 'data': data};
    } catch (e) {
      return {'status': 'success', 'data': []};
    }
  }

  Future<Map<String, dynamic>> bookAppointment(
      Map<String, dynamic> payload) async {
    var uri = Uri.parse('$baseUrl/appointments/book');
    try {
      var response =
          await http.post(uri, headers: _headers, body: json.encode(payload));
      return _handleResponse(response);
    } catch (e) {
      throw Exception('Booking failed: $e');
    }
  }
}
