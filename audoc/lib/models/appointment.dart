/// Appointment model
class Appointment {
  final int? id;
  final String studentId;
  final String studentName;
  final String phone;
  final String email;
  final String studentDepartment;
  final String medicalDepartment;
  final String medicalDepartmentDisplay;
  final int? doctorId;
  final String? doctorName;
  final String? appointmentDate;
  final String? appointmentTime;
  final String problemDescription;
  final String status;
  final String? createdAt;
  final int? queuePosition;

  Appointment({
    this.id,
    required this.studentId,
    required this.studentName,
    required this.phone,
    required this.email,
    required this.studentDepartment,
    required this.medicalDepartment,
    this.medicalDepartmentDisplay = '',
    this.doctorId,
    this.doctorName,
    this.appointmentDate,
    this.appointmentTime,
    required this.problemDescription,
    this.status = 'PENDING',
    this.createdAt,
    this.queuePosition,
  });

  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      id: json['id'],
      studentId: json['student_id'] ?? '',
      studentName: json['student_name'] ?? '',
      phone: json['phone'] ?? '',
      email: json['email'] ?? '',
      studentDepartment: json['student_department'] ?? '',
      medicalDepartment: json['medical_department'] ?? '',
      medicalDepartmentDisplay: json['medical_department_display'] ?? '',
      doctorId: json['doctor_id'],
      doctorName: json['doctor_name'],
      appointmentDate: json['appointment_date'],
      appointmentTime: json['appointment_time'],
      problemDescription: json['problem_description'] ?? '',
      status: json['status'] ?? 'PENDING',
      createdAt: json['created_at'],
      queuePosition: json['queue_position'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'student_id': studentId,
      'student_name': studentName,
      'phone': phone,
      'email': email,
      'student_department': studentDepartment,
      'medical_department': medicalDepartment,
      'doctor_id': doctorId,
      'appointment_date': appointmentDate,
      'appointment_time': appointmentTime,
      'problem_description': problemDescription,
    };
  }

  String get statusDisplay {
    switch (status) {
      case 'PENDING':
        return 'Pending';
      case 'CONFIRMED':
        return 'Confirmed';
      case 'COMPLETED':
        return 'Completed';
      case 'REJECTED':
        return 'Rejected';
      case 'CANCELLED':
        return 'Cancelled';
      default:
        return status;
    }
  }

  bool get isUpcoming =>
      status == 'PENDING' || status == 'CONFIRMED';
}

/// Time slot choices
class TimeSlot {
  static const List<String> slots = [
    '09:00 AM', '09:30 AM',
    '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM',
    '12:00 PM', '12:30 PM',
    '02:00 PM', '02:30 PM',
    '03:00 PM', '03:30 PM',
    '04:00 PM', '04:30 PM',
  ];
}
