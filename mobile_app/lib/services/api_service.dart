import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class ApiService {
  // Use 10.0.2.2 for Android emulator to hit localhost of the host machine.
  // If running on physical device, use the actual IPv4 address of the host.
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';

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

  // Login (Stub for now matching backend behavior)
  Future<Map<String, dynamic>> login(String email, String password) async {
    // In a real app we would POST /token, for prototype we bypass
    await Future.delayed(const Duration(milliseconds: 800));
    return {'status': 'success', 'user_id': 1, 'email': email};
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
      throw Exception('Generate Report Failed: $e');
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
