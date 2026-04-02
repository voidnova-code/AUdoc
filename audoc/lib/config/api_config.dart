/// API Configuration for AUdoc Flutter App
/// Change baseUrl to your Django server address

class ApiConfig {
  // For Android emulator use 10.0.2.2
  // For iOS simulator use localhost
  // For real device use your computer's IP address
  static const String baseUrl = 'http://10.0.2.2:8000';
  
  // API Endpoints
  static const String sendLoginOtp = '/api/send-login-otp/';
  static const String studentLogin = '/api/student-login/';
  static const String sendRegisterOtp = '/api/send-register-otp/';
  static const String register = '/api/register/';
  static const String doctors = '/api/doctors/';
  static const String appointments = '/api/appointments/';
  static const String bloodDonations = '/api/blood-donations/';
  static const String bloodRequests = '/api/blood-requests/';
  static const String profile = '/api/profile/';
  static const String logout = '/api/logout/';
  
  // Build full URL
  static String url(String endpoint) => baseUrl + endpoint;
}
