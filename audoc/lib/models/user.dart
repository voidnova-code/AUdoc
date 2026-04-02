/// User model for authenticated student
class User {
  final String studentId;
  final String firstName;
  final String lastName;
  final String email;
  final String phone;
  final String department;
  final String bloodGroup;
  final String homeAddress;
  final String presentAddress;
  final String emergencyContact;
  final bool isVerified;

  User({
    required this.studentId,
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.phone,
    required this.department,
    required this.bloodGroup,
    required this.homeAddress,
    required this.presentAddress,
    required this.emergencyContact,
    this.isVerified = true,
  });

  String get fullName => '$firstName $lastName';

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      studentId: json['student_id'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      department: json['department'] ?? '',
      bloodGroup: json['blood_group'] ?? '',
      homeAddress: json['home_address'] ?? '',
      presentAddress: json['present_address'] ?? '',
      emergencyContact: json['emergency_contact'] ?? '',
      isVerified: json['is_verified'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'student_id': studentId,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone': phone,
      'department': department,
      'blood_group': bloodGroup,
      'home_address': homeAddress,
      'present_address': presentAddress,
      'emergency_contact': emergencyContact,
      'is_verified': isVerified,
    };
  }
}
