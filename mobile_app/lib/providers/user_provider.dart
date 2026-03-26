import 'package:flutter/material.dart';

class UserProvider with ChangeNotifier {
  String? _userId;
  String? _email;
  String? _role;
  bool _isAuthenticated = false;

  String? get userId => _userId;
  String? get email => _email;
  String? get role => _role;
  bool get isAuthenticated => _isAuthenticated;
  bool get isDoctor => _role == 'doctor';

  void setUser(String id, String userEmail, String userRole) {
    _userId = id;
    _email = userEmail;
    _role = userRole;
    _isAuthenticated = true;
    notifyListeners();
  }

  void logout() {
    _userId = null;
    _email = null;
    _role = null;
    _isAuthenticated = false;
    notifyListeners();
  }
}
