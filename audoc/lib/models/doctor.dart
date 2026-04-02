/// Doctor model
class Doctor {
  final int id;
  final String name;
  final String email;
  final String phone;
  final String specializedIn;
  final String specializedInDisplay;
  final List<String> availableDays;
  final String availableTime;
  final bool isAvailable;
  final String? photoUrl;

  Doctor({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.specializedIn,
    required this.specializedInDisplay,
    required this.availableDays,
    required this.availableTime,
    this.isAvailable = true,
    this.photoUrl,
  });

  factory Doctor.fromJson(Map<String, dynamic> json) {
    return Doctor(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      specializedIn: json['specialized_in'] ?? '',
      specializedInDisplay: json['specialized_in_display'] ?? json['specialized_in'] ?? '',
      availableDays: (json['available_days'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      availableTime: json['available_time'] ?? '',
      isAvailable: json['is_available'] ?? true,
      photoUrl: json['photo_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone': phone,
      'specialized_in': specializedIn,
      'available_days': availableDays,
      'available_time': availableTime,
      'is_available': isAvailable,
      'photo_url': photoUrl,
    };
  }
}

/// Medical specialties
class MedicalSpecialty {
  static const Map<String, String> specialties = {
    'GENERAL': 'General Physician',
    'DENTAL': 'Dental Care',
    'EYE': 'Eye Care',
    'MENTAL': 'Mental Health & Counseling',
    'ORTHO': 'Orthopedics',
    'DERM': 'Dermatology',
    'GYNAE': 'Gynecology',
    'PHYSIO': 'Physiotherapy',
  };

  static String getDisplay(String code) {
    return specialties[code] ?? code;
  }

  static List<MapEntry<String, String>> get all => specialties.entries.toList();
}
