import 'package:flutter/material.dart';

class UserProvider with ChangeNotifier {
  String? _userId;
  String? _email;
  bool _isAuthenticated = false;

  String? get userId => _userId;
  String? get email => _email;
  bool get isAuthenticated => _isAuthenticated;

  void setUser(String id, String userEmail) {
    _userId = id;
    _email = userEmail;
    _isAuthenticated = true;
    notifyListeners();
  }

  void logout() {
    _userId = null;
    _email = null;
    _isAuthenticated = false;
    notifyListeners();
  }
}
