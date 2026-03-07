import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ReportProvider with ChangeNotifier {
  Map<String, dynamic>? _patientHistory;
  Map<String, dynamic>? _latestReport;
  bool _isLoading = false;

  Map<String, dynamic>? get patientHistory => _patientHistory;
  Map<String, dynamic>? get latestReport => _latestReport;
  bool get isLoading => _isLoading;

  Future<void> loadPatientHistory(String patientId) async {
    _isLoading = true;
    notifyListeners();

    try {
      _patientHistory = await ApiService().getReports(patientId);
    } catch (e) {
      print("Error loading history: $e");
      // Load fallback stub on error
      _patientHistory = {
        'first_name': 'Jane',
        'last_name': 'Doe',
        'reports': [],
        'mood_logs': [],
        'activity_logs': [],
        'cycle_logs': []
      };
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void setLatestReport(Map<String, dynamic> report) {
    _latestReport = report;
    notifyListeners();
  }
}
