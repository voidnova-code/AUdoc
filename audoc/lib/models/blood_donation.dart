/// Blood Donation model
class BloodDonation {
  final int? id;
  final String studentId;
  final String donorName;
  final String email;
  final String phone;
  final String bloodGroup;
  final String dateOfBirth;
  final int weight;
  final bool previousDonation;
  final String healthCondition;
  final String message;
  final String status;
  final String? createdAt;

  BloodDonation({
    this.id,
    required this.studentId,
    required this.donorName,
    required this.email,
    required this.phone,
    required this.bloodGroup,
    required this.dateOfBirth,
    required this.weight,
    this.previousDonation = false,
    this.healthCondition = '',
    this.message = '',
    this.status = 'PENDING',
    this.createdAt,
  });

  factory BloodDonation.fromJson(Map<String, dynamic> json) {
    return BloodDonation(
      id: json['id'],
      studentId: json['student_id'] ?? '',
      donorName: json['donor_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      bloodGroup: json['blood_group'] ?? '',
      dateOfBirth: json['date_of_birth'] ?? '',
      weight: json['weight'] ?? 0,
      previousDonation: json['previous_donation'] ?? false,
      healthCondition: json['health_condition'] ?? '',
      message: json['message'] ?? '',
      status: json['status'] ?? 'PENDING',
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'student_id': studentId,
      'donor_name': donorName,
      'email': email,
      'phone': phone,
      'blood_group': bloodGroup,
      'date_of_birth': dateOfBirth,
      'weight': weight,
      'previous_donation': previousDonation,
      'health_condition': healthCondition,
      'message': message,
    };
  }
}

/// Blood Request model
class BloodRequest {
  final int? id;
  final String studentId;
  final String requesterName;
  final String email;
  final String phone;
  final String bloodGroup;
  final int unitsRequired;
  final String reason;
  final String urgency;
  final String requiredDate;
  final String hospitalName;
  final String hospitalContact;
  final String notes;
  final String status;
  final String? createdAt;

  BloodRequest({
    this.id,
    required this.studentId,
    required this.requesterName,
    required this.email,
    required this.phone,
    required this.bloodGroup,
    this.unitsRequired = 1,
    required this.reason,
    this.urgency = 'MEDIUM',
    required this.requiredDate,
    required this.hospitalName,
    required this.hospitalContact,
    this.notes = '',
    this.status = 'PENDING',
    this.createdAt,
  });

  factory BloodRequest.fromJson(Map<String, dynamic> json) {
    return BloodRequest(
      id: json['id'],
      studentId: json['student_id'] ?? '',
      requesterName: json['requester_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      bloodGroup: json['blood_group'] ?? '',
      unitsRequired: json['units_required'] ?? 1,
      reason: json['reason'] ?? '',
      urgency: json['urgency'] ?? 'MEDIUM',
      requiredDate: json['required_date'] ?? '',
      hospitalName: json['hospital_name'] ?? '',
      hospitalContact: json['hospital_contact'] ?? '',
      notes: json['notes'] ?? '',
      status: json['status'] ?? 'PENDING',
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'student_id': studentId,
      'requester_name': requesterName,
      'email': email,
      'phone': phone,
      'blood_group': bloodGroup,
      'units_required': unitsRequired,
      'reason': reason,
      'urgency': urgency,
      'required_date': requiredDate,
      'hospital_name': hospitalName,
      'hospital_contact': hospitalContact,
      'notes': notes,
    };
  }

  String get urgencyDisplay {
    switch (urgency) {
      case 'LOW':
        return 'Low';
      case 'MEDIUM':
        return 'Medium';
      case 'HIGH':
        return 'High';
      case 'URGENT':
        return 'Urgent';
      default:
        return urgency;
    }
  }
}

/// Blood group choices
class BloodGroup {
  static const List<String> groups = [
    'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-',
  ];
}

/// Urgency levels
class UrgencyLevel {
  static const Map<String, String> levels = {
    'LOW': 'Low',
    'MEDIUM': 'Medium',
    'HIGH': 'High',
    'URGENT': 'Urgent',
  };

  static List<MapEntry<String, String>> get all => levels.entries.toList();
}
