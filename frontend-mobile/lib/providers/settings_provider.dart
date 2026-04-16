import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsProvider with ChangeNotifier {
  late SharedPreferences _prefs;

  ThemeMode _themeMode = ThemeMode.dark;
  bool _notificationsEnabled = true;
  double _llmTemp = 0.2;
  String _agentStrictness = 'high';

  ThemeMode get themeMode => _themeMode;
  bool get notificationsEnabled => _notificationsEnabled;
  double get llmTemp => _llmTemp;
  String get agentStrictness => _agentStrictness;

  SettingsProvider() {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    _prefs = await SharedPreferences.getInstance();
    
    final themeStr = _prefs.getString('theme') ?? 'dark';
    _themeMode = themeStr == 'dark' ? ThemeMode.dark : ThemeMode.light;
    
    _notificationsEnabled = _prefs.getBool('notifications') ?? true;
    _llmTemp = _prefs.getDouble('llmTemp') ?? 0.2;
    _agentStrictness = _prefs.getString('agentStrictness') ?? 'high';
    
    notifyListeners();
  }

  Future<void> toggleTheme(bool isDark) async {
    _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
    await _prefs.setString('theme', isDark ? 'dark' : 'light');
    notifyListeners();
  }

  Future<void> toggleNotifications(bool isEnabled) async {
    _notificationsEnabled = isEnabled;
    await _prefs.setBool('notifications', isEnabled);
    notifyListeners();
  }

  Future<void> setLlmTemp(double temp) async {
    _llmTemp = temp;
    await _prefs.setDouble('llmTemp', temp);
    notifyListeners();
  }

  Future<void> setAgentStrictness(String strictness) async {
    _agentStrictness = strictness;
    await _prefs.setString('agentStrictness', strictness);
    notifyListeners();
  }
}
