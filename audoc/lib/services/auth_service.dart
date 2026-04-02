import '../models/user.dart';
import 'api_service.dart';
import 'storage_service.dart';

/// Authentication service
class AuthService {
  /// Check if user is logged in
  static bool isLoggedIn() {
    return StorageService.isLoggedIn() && StorageService.getUser() != null;
  }

  /// Get current user
  static User? getCurrentUser() {
    return StorageService.getUser();
  }

  /// Send login OTP
  static Future<ApiResponse> sendLoginOtp(String studentId) async {
    return ApiService.sendLoginOtp(studentId);
  }

  /// Login with OTP
  static Future<ApiResponse<User>> login(String studentId, String otp) async {
    final response = await ApiService.login(studentId, otp);
    
    if (response.success && response.data != null) {
      await StorageService.saveUser(response.data!);
      await StorageService.setLoggedIn(true);
    }
    
    return response;
  }

  /// Send registration OTP
  static Future<ApiResponse> sendRegisterOtp(String email) async {
    return ApiService.sendRegisterOtp(email);
  }

  /// Register new student
  static Future<ApiResponse> register(Map<String, dynamic> data, String otp) async {
    return ApiService.register(data, otp);
  }

  /// Logout
  static Future<void> logout() async {
    await ApiService.logout();
    await StorageService.clearAll();
  }

  /// Refresh user profile from server
  static Future<ApiResponse<User>> refreshProfile() async {
    final response = await ApiService.getProfile();
    
    if (response.success && response.data != null) {
      await StorageService.saveUser(response.data!);
    }
    
    return response;
  }
}
