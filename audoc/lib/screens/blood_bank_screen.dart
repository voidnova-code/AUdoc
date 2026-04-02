import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/blood_donation.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/custom_text_field.dart';

/// Blood Bank screen - donate and request blood
class BloodBankScreen extends StatefulWidget {
  const BloodBankScreen({super.key});

  @override
  State<BloodBankScreen> createState() => _BloodBankScreenState();
}

class _BloodBankScreenState extends State<BloodBankScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  BloodDonation? _existingDonation;
  bool _isLoadingStatus = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _checkDonationStatus();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _checkDonationStatus() async {
    final response = await ApiService.getBloodDonationStatus();
    setState(() {
      _isLoadingStatus = false;
      if (response.success) {
        _existingDonation = response.data;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Blood Bank'),
        backgroundColor: Colors.red.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(
              icon: Icon(Icons.volunteer_activism),
              text: 'Donate',
            ),
            Tab(
              icon: Icon(Icons.bloodtype),
              text: 'Request',
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _DonateTab(
            existingDonation: _existingDonation,
            isLoading: _isLoadingStatus,
            onRegistered: _checkDonationStatus,
          ),
          _RequestTab(onRequested: () {}),
        ],
      ),
    );
  }
}

/// Donate blood tab
class _DonateTab extends StatefulWidget {
  final BloodDonation? existingDonation;
  final bool isLoading;
  final VoidCallback onRegistered;

  const _DonateTab({
    this.existingDonation,
    required this.isLoading,
    required this.onRegistered,
  });

  @override
  State<_DonateTab> createState() => _DonateTabState();
}

class _DonateTabState extends State<_DonateTab> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _weightController = TextEditingController();
  final _healthConditionController = TextEditingController();
  final _messageController = TextEditingController();

  String? _selectedBloodGroup;
  DateTime? _dateOfBirth;
  bool _previousDonation = false;
  bool _isLoading = false;
  User? _user;

  @override
  void initState() {
    super.initState();
    _user = AuthService.getCurrentUser();
    _prefillForm();
  }

  void _prefillForm() {
    if (_user != null) {
      _nameController.text = _user!.fullName;
      _emailController.text = _user!.email;
      _phoneController.text = _user!.phone;
      _selectedBloodGroup = _user!.bloodGroup;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _weightController.dispose();
    _healthConditionController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  Future<void> _selectDateOfBirth() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(now.year - 20),
      firstDate: DateTime(now.year - 65),
      lastDate: DateTime(now.year - 18),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: Colors.red.shade700,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() => _dateOfBirth = picked);
    }
  }

  Future<void> _register() async {
    if (!_formKey.currentState!.validate()) return;

    if (_dateOfBirth == null) {
      _showSnackBar('Please select your date of birth', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    final donation = BloodDonation(
      studentId: _user?.studentId ?? '',
      donorName: _nameController.text.trim(),
      email: _emailController.text.trim(),
      phone: _phoneController.text.trim(),
      bloodGroup: _selectedBloodGroup!,
      dateOfBirth: DateFormat('yyyy-MM-dd').format(_dateOfBirth!),
      weight: int.parse(_weightController.text.trim()),
      previousDonation: _previousDonation,
      healthCondition: _healthConditionController.text.trim(),
      message: _messageController.text.trim(),
    );

    final response = await ApiService.registerBloodDonor(donation);

    setState(() => _isLoading = false);

    if (response.success) {
      _showSnackBar('Registered as blood donor! You will be notified when needed.');
      widget.onRegistered();
    } else {
      _showSnackBar(response.error ?? 'Registration failed', isError: true);
    }
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
    if (widget.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    // Show existing registration status
    if (widget.existingDonation != null) {
      return _ExistingDonorCard(donation: widget.existingDonation!);
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Hero section
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.red.shade400, Colors.red.shade700],
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  const Text(
                    '🩸',
                    style: TextStyle(fontSize: 48),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Become a Blood Donor',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Your donation can save up to 3 lives!',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.9),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Form fields
            CustomTextField(
              controller: _nameController,
              label: 'Full Name',
              prefixIcon: Icons.person,
              validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _emailController,
              label: 'Email',
              prefixIcon: Icons.email,
              keyboardType: TextInputType.emailAddress,
              validator: (v) {
                if (v?.isEmpty ?? true) return 'Required';
                if (!v!.contains('@')) return 'Invalid email';
                return null;
              },
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _phoneController,
              label: 'Phone Number',
              prefixIcon: Icons.phone,
              keyboardType: TextInputType.phone,
              validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
            ),
            const SizedBox(height: 16),

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

            // Date of birth
            InkWell(
              onTap: _selectDateOfBirth,
              borderRadius: BorderRadius.circular(12),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: 'Date of Birth',
                  prefixIcon: const Icon(Icons.cake),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  _dateOfBirth != null
                      ? DateFormat('MMM d, yyyy').format(_dateOfBirth!)
                      : 'Select date',
                  style: TextStyle(
                    color: _dateOfBirth != null ? Colors.black : Colors.grey,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _weightController,
              label: 'Weight (kg)',
              hint: 'Minimum 50 kg required',
              prefixIcon: Icons.monitor_weight,
              keyboardType: TextInputType.number,
              validator: (v) {
                if (v?.isEmpty ?? true) return 'Required';
                final weight = int.tryParse(v!);
                if (weight == null) return 'Enter a valid number';
                if (weight < 50) return 'Minimum 50 kg required';
                return null;
              },
            ),
            const SizedBox(height: 16),

            // Previous donation checkbox
            CheckboxListTile(
              value: _previousDonation,
              onChanged: (v) => setState(() => _previousDonation = v ?? false),
              title: const Text('I have donated blood before'),
              controlAffinity: ListTileControlAffinity.leading,
              contentPadding: EdgeInsets.zero,
              activeColor: Colors.red.shade700,
            ),

            CustomTextField(
              controller: _healthConditionController,
              label: 'Any Medical Conditions? (Optional)',
              hint: 'e.g., diabetes, heart disease...',
              prefixIcon: Icons.health_and_safety,
              maxLines: 2,
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _messageController,
              label: 'Additional Message (Optional)',
              prefixIcon: Icons.message,
              maxLines: 2,
            ),
            const SizedBox(height: 24),

            PrimaryButton(
              text: 'Register as Donor',
              icon: Icons.volunteer_activism,
              color: Colors.red.shade700,
              onPressed: _register,
              isLoading: _isLoading,
            ),
          ],
        ),
      ),
    );
  }
}

/// Existing donor status card
class _ExistingDonorCard extends StatelessWidget {
  final BloodDonation donation;

  const _ExistingDonorCard({required this.donation});

  @override
  Widget build(BuildContext context) {
    Color statusColor;
    IconData statusIcon;
    String statusText;

    switch (donation.status) {
      case 'PENDING':
        statusColor = Colors.orange;
        statusIcon = Icons.hourglass_empty;
        statusText = 'Pending Review';
        break;
      case 'APPROVED':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        statusText = 'Approved';
        break;
      case 'COMPLETED':
        statusColor = Colors.blue;
        statusIcon = Icons.verified;
        statusText = 'Donated';
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.info;
        statusText = donation.status;
    }

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(statusIcon, size: 50, color: statusColor),
            ),
            const SizedBox(height: 24),
            Text(
              "You're a Registered Donor!",
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade800,
              ),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                statusText,
                style: TextStyle(
                  color: statusColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 24),
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    _InfoTile(
                      icon: Icons.person,
                      label: 'Name',
                      value: donation.donorName,
                    ),
                    const Divider(),
                    _InfoTile(
                      icon: Icons.bloodtype,
                      label: 'Blood Group',
                      value: donation.bloodGroup,
                    ),
                    const Divider(),
                    _InfoTile(
                      icon: Icons.phone,
                      label: 'Phone',
                      value: donation.phone,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              "You'll receive notifications when someone needs your blood type.",
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Request blood tab
class _RequestTab extends StatefulWidget {
  final VoidCallback onRequested;

  const _RequestTab({required this.onRequested});

  @override
  State<_RequestTab> createState() => _RequestTabState();
}

class _RequestTabState extends State<_RequestTab> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  final _reasonController = TextEditingController();
  final _hospitalNameController = TextEditingController();
  final _hospitalContactController = TextEditingController();
  final _notesController = TextEditingController();

  String? _selectedBloodGroup;
  String _selectedUrgency = 'MEDIUM';
  int _unitsRequired = 1;
  DateTime? _requiredDate;
  bool _isLoading = false;
  User? _user;

  @override
  void initState() {
    super.initState();
    _user = AuthService.getCurrentUser();
    _prefillForm();
  }

  void _prefillForm() {
    if (_user != null) {
      _nameController.text = _user!.fullName;
      _emailController.text = _user!.email;
      _phoneController.text = _user!.phone;
    }
    _requiredDate = DateTime.now();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _reasonController.dispose();
    _hospitalNameController.dispose();
    _hospitalContactController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: now,
      lastDate: now.add(const Duration(days: 30)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: Colors.red.shade700,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() => _requiredDate = picked);
    }
  }

  Future<void> _submitRequest() async {
    if (!_formKey.currentState!.validate()) return;

    if (_requiredDate == null) {
      _showSnackBar('Please select the required date', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    final request = BloodRequest(
      studentId: _user?.studentId ?? '',
      requesterName: _nameController.text.trim(),
      email: _emailController.text.trim(),
      phone: _phoneController.text.trim(),
      bloodGroup: _selectedBloodGroup!,
      unitsRequired: _unitsRequired,
      reason: _reasonController.text.trim(),
      urgency: _selectedUrgency,
      requiredDate: DateFormat('yyyy-MM-dd').format(_requiredDate!),
      hospitalName: _hospitalNameController.text.trim(),
      hospitalContact: _hospitalContactController.text.trim(),
      notes: _notesController.text.trim(),
    );

    final response = await ApiService.requestBlood(request);

    setState(() => _isLoading = false);

    if (response.success) {
      _showSnackBar('Request submitted! Matching donors have been notified.');
      _resetForm();
      widget.onRequested();
    } else {
      _showSnackBar(response.error ?? 'Failed to submit request', isError: true);
    }
  }

  void _resetForm() {
    _formKey.currentState?.reset();
    _reasonController.clear();
    _hospitalNameController.clear();
    _hospitalContactController.clear();
    _notesController.clear();
    setState(() {
      _selectedBloodGroup = null;
      _selectedUrgency = 'MEDIUM';
      _unitsRequired = 1;
      _requiredDate = DateTime.now();
    });
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
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Urgency warning
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.orange.shade200),
              ),
              child: Row(
                children: [
                  Icon(Icons.info, color: Colors.orange.shade700),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'All registered donors with matching blood type will be notified.',
                      style: TextStyle(color: Colors.orange.shade800),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            CustomTextField(
              controller: _nameController,
              label: 'Your Name',
              prefixIcon: Icons.person,
              validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  child: CustomTextField(
                    controller: _emailController,
                    label: 'Email',
                    prefixIcon: Icons.email,
                    keyboardType: TextInputType.emailAddress,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: CustomTextField(
                    controller: _phoneController,
                    label: 'Phone',
                    prefixIcon: Icons.phone,
                    keyboardType: TextInputType.phone,
                    validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                Expanded(
                  flex: 2,
                  child: CustomDropdown<String>(
                    value: _selectedBloodGroup,
                    label: 'Blood Group Needed',
                    prefixIcon: Icons.bloodtype,
                    items: BloodGroup.groups
                        .map((g) => DropdownMenuItem(value: g, child: Text(g)))
                        .toList(),
                    onChanged: (v) => setState(() => _selectedBloodGroup = v),
                    validator: (v) => v == null ? 'Required' : null,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Units',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      Row(
                        children: [
                          IconButton(
                            icon: const Icon(Icons.remove_circle_outline),
                            onPressed: _unitsRequired > 1
                                ? () => setState(() => _unitsRequired--)
                                : null,
                          ),
                          Text(
                            '$_unitsRequired',
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.add_circle_outline),
                            onPressed: () => setState(() => _unitsRequired++),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Urgency selector
            const Text(
              'Urgency Level',
              style: TextStyle(fontSize: 14, color: Colors.grey),
            ),
            const SizedBox(height: 8),
            Row(
              children: UrgencyLevel.all.map((entry) {
                final isSelected = _selectedUrgency == entry.key;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(entry.value),
                      selected: isSelected,
                      onSelected: (selected) {
                        if (selected) {
                          setState(() => _selectedUrgency = entry.key);
                        }
                      },
                      selectedColor: _getUrgencyColor(entry.key),
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.white : Colors.black,
                        fontSize: 12,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _reasonController,
              label: 'Reason for Request',
              hint: 'e.g., Surgery, Accident, Transfusion',
              prefixIcon: Icons.medical_information,
              validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
            ),
            const SizedBox(height: 16),

            // Required date
            InkWell(
              onTap: _selectDate,
              borderRadius: BorderRadius.circular(12),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: 'Date Needed By',
                  prefixIcon: const Icon(Icons.calendar_today),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  _requiredDate != null
                      ? DateFormat('MMM d, yyyy').format(_requiredDate!)
                      : 'Select date',
                ),
              ),
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _hospitalNameController,
              label: 'Hospital / Clinic Name',
              prefixIcon: Icons.local_hospital,
              validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _hospitalContactController,
              label: 'Hospital Contact / Address',
              prefixIcon: Icons.location_on,
              maxLines: 2,
              validator: (v) => v?.isEmpty ?? true ? 'Required' : null,
            ),
            const SizedBox(height: 16),

            CustomTextField(
              controller: _notesController,
              label: 'Additional Notes (Optional)',
              prefixIcon: Icons.notes,
              maxLines: 2,
            ),
            const SizedBox(height: 24),

            PrimaryButton(
              text: 'Submit Request',
              icon: Icons.send,
              color: Colors.red.shade700,
              onPressed: _submitRequest,
              isLoading: _isLoading,
            ),
          ],
        ),
      ),
    );
  }

  Color _getUrgencyColor(String urgency) {
    switch (urgency) {
      case 'LOW':
        return Colors.green;
      case 'MEDIUM':
        return Colors.orange;
      case 'HIGH':
        return Colors.deepOrange;
      case 'URGENT':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

class _InfoTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoTile({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
              ),
              Text(
                value,
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
