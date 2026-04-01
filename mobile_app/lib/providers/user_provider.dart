import 'package:flutter/material.dart';

class UserProvider with ChangeNotifier {
  String? _userId;
  String? _email;
  String? _role;
  String? _name;
  String? _sex;
  bool _isAuthenticated = false;

  String? get userId => _userId;
  String? get email => _email;
  String? get role => _role;
  String? get name => _name;
  String? get sex => _sex;
  bool get isAuthenticated => _isAuthenticated;
  bool get isDoctor => _role == 'doctor';

  void setUser(String id, String userEmail, String userRole, {String? userName, String? userSex}) {
    _userId = id;
    _email = userEmail;
    _role = userRole;
    _name = userName;
    _sex = userSex;
    _isAuthenticated = true;
    notifyListeners();
  }

  void logout() {
    _userId = null;
    _email = null;
    _role = null;
    _name = null;
    _sex = null;
    _isAuthenticated = false;
    notifyListeners();
  }
}
