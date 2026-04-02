import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/user.dart';
import '../models/doctor.dart';
import '../models/appointment.dart';
import '../models/blood_donation.dart';
import 'storage_service.dart';

/// API Service for all network calls
class ApiService {
  static final http.Client _client = http.Client();

  /// Get common headers
  static Map<String, String> get _headers {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    final sessionToken = StorageService.getSessionToken();
    if (sessionToken != null) {
      headers['Cookie'] = 'sessionid=$sessionToken';
    }

    final csrfToken = StorageService.getCsrfToken();
    if (csrfToken != null) {
      headers['X-CSRFToken'] = csrfToken;
    }

    return headers;
  }

  /// Extract and save session cookie from response
  static void _saveSession(http.Response response) {
    final cookies = response.headers['set-cookie'];
    if (cookies != null) {
      // Extract sessionid
      final sessionMatch = RegExp(r'sessionid=([^;]+)').firstMatch(cookies);
      if (sessionMatch != null) {
        StorageService.saveSessionToken(sessionMatch.group(1)!);
      }
      // Extract csrftoken
      final csrfMatch = RegExp(r'csrftoken=([^;]+)').firstMatch(cookies);
      if (csrfMatch != null) {
        StorageService.saveCsrfToken(csrfMatch.group(1)!);
      }
    }
  }

  // ─── Authentication ────────────────────────────────────────────────

  /// Send login OTP
  static Future<ApiResponse> sendLoginOtp(String studentId) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.sendLoginOtp)),
        headers: _headers,
        body: jsonEncode({'student_id': studentId}),
      );
      _saveSession(response);

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return ApiResponse(success: true, data: data);
      }
      return ApiResponse(
        success: false,
        error: data['error'] ?? 'Failed to send OTP',
      );
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Login with OTP
  static Future<ApiResponse<User>> login(String studentId, String otp) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.studentLogin)),
        headers: _headers,
        body: jsonEncode({'student_id': studentId, 'otp': otp}),
      );
      _saveSession(response);

      final data = jsonDecode(response.body);
      if (response.statusCode == 200 && data['success'] == true) {
        final user = User.fromJson(data['user']);
        return ApiResponse(success: true, data: user);
      }
      return ApiResponse(
        success: false,
        error: data['error'] ?? 'Login failed',
      );
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Send registration OTP
  static Future<ApiResponse> sendRegisterOtp(String email) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.sendRegisterOtp)),
        headers: _headers,
        body: jsonEncode({'email': email}),
      );
      _saveSession(response);

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        return ApiResponse(success: true, data: data);
      }
      return ApiResponse(
        success: false,
        error: data['error'] ?? 'Failed to send OTP',
      );
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Register new student
  static Future<ApiResponse> register(
    Map<String, dynamic> data,
    String otp,
  ) async {
    try {
      data['otp'] = otp;
      final response = await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.register)),
        headers: _headers,
        body: jsonEncode(data),
      );
      _saveSession(response);

      final responseData = jsonDecode(response.body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(success: true, data: responseData);
      }
      return ApiResponse(
        success: false,
        error: responseData['error'] ?? 'Registration failed',
      );
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Logout
  static Future<ApiResponse> logout() async {
    try {
      await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.logout)),
        headers: _headers,
      );
      await StorageService.clearAll();
      return ApiResponse(success: true);
    } catch (e) {
      await StorageService.clearAll();
      return ApiResponse(success: true);
    }
  }

  // ─── Profile ───────────────────────────────────────────────────────

  /// Get user profile
  static Future<ApiResponse<User>> getProfile() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.url(ApiConfig.profile)),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        final data =
            decoded is Map<String, dynamic> &&
                decoded['profile'] is Map<String, dynamic>
            ? decoded['profile'] as Map<String, dynamic>
            : decoded as Map<String, dynamic>;
        return ApiResponse(success: true, data: User.fromJson(data));
      }
      return ApiResponse(success: false, error: 'Failed to load profile');
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  // ─── Doctors ───────────────────────────────────────────────────────

  /// Get all doctors
  static Future<ApiResponse<List<Doctor>>> getDoctors() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.url(ApiConfig.doctors)),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        final data = decoded is List
            ? decoded
            : (decoded is Map<String, dynamic> && decoded['doctors'] is List
                  ? decoded['doctors'] as List
                  : <dynamic>[]);
        final doctors = data.map((e) => Doctor.fromJson(e)).toList();
        return ApiResponse(success: true, data: doctors);
      }
      return ApiResponse(success: false, error: 'Failed to load doctors');
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  // ─── Appointments ──────────────────────────────────────────────────

  /// Get user appointments
  static Future<ApiResponse<List<Appointment>>> getAppointments() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.url(ApiConfig.appointments)),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        final data = decoded is List
            ? decoded
            : (decoded is Map<String, dynamic> &&
                      decoded['appointments'] is List
                  ? decoded['appointments'] as List
                  : <dynamic>[]);
        final appointments = data.map((e) => Appointment.fromJson(e)).toList();
        return ApiResponse(success: true, data: appointments);
      }
      return ApiResponse(success: false, error: 'Failed to load appointments');
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Book appointment
  static Future<ApiResponse> bookAppointment(Appointment appointment) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.appointments)),
        headers: _headers,
        body: jsonEncode(appointment.toJson()),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(success: true, data: data);
      }
      return ApiResponse(
        success: false,
        error: data['error'] ?? 'Failed to book appointment',
      );
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  // ─── Blood Bank ────────────────────────────────────────────────────

  /// Register as blood donor
  static Future<ApiResponse> registerBloodDonor(BloodDonation donation) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.bloodDonations)),
        headers: _headers,
        body: jsonEncode(donation.toJson()),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(success: true, data: data);
      }
      return ApiResponse(
        success: false,
        error: data['error'] ?? 'Failed to register',
      );
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Get blood donation status
  static Future<ApiResponse<BloodDonation?>> getBloodDonationStatus() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.url(ApiConfig.bloodDonations)),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        Map<String, dynamic>? data;
        if (decoded is Map<String, dynamic>) {
          if (decoded['id'] != null) {
            data = decoded;
          } else if (decoded['donation'] is Map<String, dynamic>) {
            data = decoded['donation'] as Map<String, dynamic>;
          } else if (decoded['donations'] is List &&
              (decoded['donations'] as List).isNotEmpty) {
            data = (decoded['donations'] as List).first as Map<String, dynamic>;
          }
        }
        if (data != null && data['id'] != null) {
          return ApiResponse(success: true, data: BloodDonation.fromJson(data));
        }
        return ApiResponse(success: true, data: null);
      }
      return ApiResponse(success: false, error: 'Failed to load status');
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Request blood
  static Future<ApiResponse> requestBlood(BloodRequest request) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.url(ApiConfig.bloodRequests)),
        headers: _headers,
        body: jsonEncode(request.toJson()),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(success: true, data: data);
      }
      return ApiResponse(
        success: false,
        error: data['error'] ?? 'Failed to submit request',
      );
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }

  /// Get blood requests
  static Future<ApiResponse<List<BloodRequest>>> getBloodRequests() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.url(ApiConfig.bloodRequests)),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        final data = decoded is List
            ? decoded
            : (decoded is Map<String, dynamic> && decoded['requests'] is List
                  ? decoded['requests'] as List
                  : <dynamic>[]);
        final requests = data.map((e) => BloodRequest.fromJson(e)).toList();
        return ApiResponse(success: true, data: requests);
      }
      return ApiResponse(success: false, error: 'Failed to load requests');
    } catch (e) {
      return ApiResponse(success: false, error: 'Network error: $e');
    }
  }
}

/// Generic API Response wrapper
class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? error;

  ApiResponse({required this.success, this.data, this.error});
}
