import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

/// Service for persistent storage (session management)
class StorageService {
  static const String _keyUser = 'user_data';
  static const String _keySessionToken = 'session_token';
  static const String _keyIsLoggedIn = 'is_logged_in';
  static const String _keyCsrfToken = 'csrf_token';

  static SharedPreferences? _prefs;

  /// Initialize shared preferences
  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// Get SharedPreferences instance
  static SharedPreferences get prefs {
    if (_prefs == null) {
      throw Exception('StorageService not initialized. Call init() first.');
    }
    return _prefs!;
  }

  // ─── User Management ───────────────────────────────────────────────

  /// Save user data
  static Future<bool> saveUser(User user) async {
    final jsonString = jsonEncode(user.toJson());
    return prefs.setString(_keyUser, jsonString);
  }

  /// Get saved user
  static User? getUser() {
    final jsonString = prefs.getString(_keyUser);
    if (jsonString == null) return null;
    try {
      final json = jsonDecode(jsonString);
      return User.fromJson(json);
    } catch (e) {
      return null;
    }
  }

  /// Clear user data
  static Future<bool> clearUser() async {
    return prefs.remove(_keyUser);
  }

  // ─── Session Management ────────────────────────────────────────────

  /// Save session token
  static Future<bool> saveSessionToken(String token) async {
    return prefs.setString(_keySessionToken, token);
  }

  /// Get session token
  static String? getSessionToken() {
    return prefs.getString(_keySessionToken);
  }

  /// Save CSRF token
  static Future<bool> saveCsrfToken(String token) async {
    return prefs.setString(_keyCsrfToken, token);
  }

  /// Get CSRF token
  static String? getCsrfToken() {
    return prefs.getString(_keyCsrfToken);
  }

  /// Set logged in status
  static Future<bool> setLoggedIn(bool value) async {
    return prefs.setBool(_keyIsLoggedIn, value);
  }

  /// Check if user is logged in
  static bool isLoggedIn() {
    return prefs.getBool(_keyIsLoggedIn) ?? false;
  }

  // ─── Clear All ─────────────────────────────────────────────────────

  /// Clear all stored data (logout)
  static Future<void> clearAll() async {
    await prefs.remove(_keyUser);
    await prefs.remove(_keySessionToken);
    await prefs.remove(_keyIsLoggedIn);
    await prefs.remove(_keyCsrfToken);
  }
}
