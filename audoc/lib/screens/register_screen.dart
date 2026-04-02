import 'package:flutter/material.dart';
import '../models/doctor.dart';
import '../models/blood_donation.dart';
import '../services/auth_service.dart';
import '../widgets/custom_text_field.dart';

/// Registration screen with OTP verification
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  int _currentStep = 0;

  // Controllers
  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _studentIdController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emergencyContactController = TextEditingController();
  final _homeAddressController = TextEditingController();
  final _presentAddressController = TextEditingController();
  final _otpController = TextEditingController();

  String? _selectedDepartment;
  String? _selectedBloodGroup;

  bool _isLoading = false;
  bool _otpSent = false;

  // Department choices
  static const List<Map<String, String>> departments = [
    {'code': 'CSE', 'name': 'Computer Science'},
    {'code': 'IT', 'name': 'Information Technology'},
    {'code': 'ECE', 'name': 'Electronics & Telecommunication'},
    {'code': 'MECH', 'name': 'Mechanical Engineering'},
    {'code': 'CIVIL', 'name': 'Civil Engineering'},
    {'code': 'PHY', 'name': 'Physics'},
    {'code': 'CHEM', 'name': 'Chemistry'},
    {'code': 'MATH', 'name': 'Mathematics'},
    {'code': 'BIO', 'name': 'Life Science & Bioinformatics'},
    {'code': 'ECON', 'name': 'Economics'},
    {'code': 'ENG', 'name': 'English'},
    {'code': 'OTHER', 'name': 'Other'},
  ];

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _emailController.dispose();
    _studentIdController.dispose();
    _phoneController.dispose();
    _emergencyContactController.dispose();
    _homeAddressController.dispose();
    _presentAddressController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    if (_emailController.text.trim().isEmpty) {
      _showSnackBar('Please enter your email', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    final response = await AuthService.sendRegisterOtp(
      _emailController.text.trim(),
    );

    setState(() => _isLoading = false);

    if (response.success) {
      setState(() => _otpSent = true);
      _showSnackBar('OTP sent to your email');
    } else {
      _showSnackBar(response.error ?? 'Failed to send OTP', isError: true);
    }
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;

    if (!_otpSent) {
      _showSnackBar('Please verify your email first', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    final data = {
      'first_name': _firstNameController.text.trim(),
      'last_name': _lastNameController.text.trim(),
      'email': _emailController.text.trim(),
      'student_id': _studentIdController.text.trim(),
      'phone': _phoneController.text.trim(),
      'emergency_contact': _emergencyContactController.text.trim(),
      'department': _selectedDepartment,
      'blood_group': _selectedBloodGroup,
      'home_address': _homeAddressController.text.trim(),
      'present_address': _presentAddressController.text.trim(),
    };

    final response = await AuthService.register(
      data,
      _otpController.text.trim(),
    );

    setState(() => _isLoading = false);

    if (response.success) {
      if (!mounted) return;
      _showSuccessDialog();
    } else {
      _showSnackBar(response.error ?? 'Registration failed', isError: true);
    }
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Colors.green.shade100,
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.check,
                size: 50,
                color: Colors.green.shade600,
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Registration Submitted!',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Your registration has been submitted for review. '
              'You will receive an email once approved.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context); // Close dialog
              Navigator.pop(context); // Go back to login
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showSnackBar(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Student Registration'),
        backgroundColor: const Color(0xFF1a5c96),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: Form(
        key: _formKey,
        child: Stepper(
          currentStep: _currentStep,
          onStepContinue: () {
            if (_currentStep < 2) {
              setState(() => _currentStep++);
            } else {
              _register();
            }
          },
          onStepCancel: () {
            if (_currentStep > 0) {
              setState(() => _currentStep--);
            }
          },
          controlsBuilder: (context, details) {
            return Padding(
              padding: const EdgeInsets.only(top: 20),
              child: Row(
                children: [
                  Expanded(
                    child: PrimaryButton(
                      text: _currentStep == 2 ? 'Submit' : 'Continue',
                      onPressed: _isLoading ? null : details.onStepContinue,
                      isLoading: _isLoading && _currentStep == 2,
                    ),
                  ),
                  if (_currentStep > 0) ...[
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton(
                        onPressed: details.onStepCancel,
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text('Back'),
                      ),
                    ),
                  ],
                ],
              ),
            );
          },
          steps: [
            // Step 1: Personal Info
            Step(
              title: const Text('Personal Information'),
              isActive: _currentStep >= 0,
              state: _currentStep > 0 ? StepState.complete : StepState.indexed,
              content: Column(
                children: [
                  CustomTextField(
                    controller: _firstNameController,
                    label: 'First Name',
                    prefixIcon: Icons.person,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _lastNameController,
                    label: 'Last Name',
                    prefixIcon: Icons.person_outline,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _studentIdController,
                    label: 'Student ID',
                    prefixIcon: Icons.badge,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomDropdown<String>(
                    value: _selectedDepartment,
                    label: 'Department',
                    prefixIcon: Icons.school,
                    items: departments
                        .map((d) => DropdownMenuItem(
                              value: d['code'],
                              child: Text(d['name']!),
                            ))
                        .toList(),
                    onChanged: (v) => setState(() => _selectedDepartment = v),
                    validator: (v) => v == null ? 'Required' : null,
                  ),
                ],
              ),
            ),

            // Step 2: Contact Info
            Step(
              title: const Text('Contact Information'),
              isActive: _currentStep >= 1,
              state: _currentStep > 1 ? StepState.complete : StepState.indexed,
              content: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: CustomTextField(
                          controller: _emailController,
                          label: 'Email',
                          prefixIcon: Icons.email,
                          keyboardType: TextInputType.emailAddress,
                          enabled: !_otpSent,
                          validator: (v) {
                            if (v?.isEmpty ?? true) return 'Required';
                            if (!v!.contains('@')) return 'Invalid email';
                            return null;
                          },
                        ),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: _isLoading || _otpSent ? null : _sendOtp,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _otpSent
                              ? Colors.green
                              : const Color(0xFF1a5c96),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 16,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : Icon(
                                _otpSent ? Icons.check : Icons.send,
                                color: Colors.white,
                              ),
                      ),
                    ],
                  ),
                  if (_otpSent) ...[
                    const SizedBox(height: 16),
                    CustomTextField(
                      controller: _otpController,
                      label: 'OTP Code',
                      prefixIcon: Icons.lock,
                      keyboardType: TextInputType.number,
                      validator: (v) {
                        if (v?.isEmpty ?? true) return 'Required';
                        if (v!.length != 6) return 'Must be 6 digits';
                        return null;
                      },
                    ),
                  ],
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _phoneController,
                    label: 'Phone Number',
                    prefixIcon: Icons.phone,
                    keyboardType: TextInputType.phone,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _emergencyContactController,
                    label: 'Emergency Contact',
                    prefixIcon: Icons.phone_in_talk,
                    keyboardType: TextInputType.phone,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                ],
              ),
            ),

            // Step 3: Additional Info
            Step(
              title: const Text('Additional Information'),
              isActive: _currentStep >= 2,
              state: _currentStep > 2 ? StepState.complete : StepState.indexed,
              content: Column(
                children: [
                  CustomDropdown<String>(
                    value: _selectedBloodGroup,
                    label: 'Blood Group',
                    prefixIcon: Icons.bloodtype,
                    items: BloodGroup.groups
                        .map((g) => DropdownMenuItem(value: g, child: Text(g)))
                        .toList(),
                    onChanged: (v) => setState(() => _selectedBloodGroup = v),
                    validator: (v) => v == null ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _homeAddressController,
                    label: 'Home Address',
                    prefixIcon: Icons.home,
                    maxLines: 2,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    controller: _presentAddressController,
                    label: 'Present Address',
                    prefixIcon: Icons.location_on,
                    maxLines: 2,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
