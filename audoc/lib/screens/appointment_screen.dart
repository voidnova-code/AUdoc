import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/appointment.dart';
import '../models/doctor.dart';
import '../models/user.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../widgets/appointment_card.dart';
import '../widgets/custom_text_field.dart';

/// Appointment screen - book and view appointments
class AppointmentScreen extends StatefulWidget {
  const AppointmentScreen({super.key});

  @override
  State<AppointmentScreen> createState() => _AppointmentScreenState();
}

class _AppointmentScreenState extends State<AppointmentScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<Appointment> _appointments = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadAppointments();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadAppointments() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    final response = await ApiService.getAppointments();

    setState(() {
      _isLoading = false;
      if (response.success && response.data != null) {
        _appointments = response.data!;
      } else {
        _error = response.error;
      }
    });
  }

  List<Appointment> get _upcomingAppointments =>
      _appointments.where((a) => a.isUpcoming).toList();

  List<Appointment> get _historyAppointments =>
      _appointments.where((a) => !a.isUpcoming).toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Appointments'),
        backgroundColor: const Color(0xFF1a5c96),
        foregroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(text: 'Book'),
            Tab(text: 'Upcoming'),
            Tab(text: 'History'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _BookAppointmentTab(onBooked: _loadAppointments),
          _AppointmentListTab(
            appointments: _upcomingAppointments,
            isLoading: _isLoading,
            error: _error,
            onRefresh: _loadAppointments,
            emptyMessage: 'No upcoming appointments',
            emptyIcon: Icons.calendar_today_outlined,
          ),
          _AppointmentListTab(
            appointments: _historyAppointments,
            isLoading: _isLoading,
            error: _error,
            onRefresh: _loadAppointments,
            emptyMessage: 'No appointment history',
            emptyIcon: Icons.history,
          ),
        ],
      ),
    );
  }
}

/// Tab for booking appointments
class _BookAppointmentTab extends StatefulWidget {
  final VoidCallback onBooked;

  const _BookAppointmentTab({required this.onBooked});

  @override
  State<_BookAppointmentTab> createState() => _BookAppointmentTabState();
}

class _BookAppointmentTabState extends State<_BookAppointmentTab> {
  final _formKey = GlobalKey<FormState>();
  final _problemController = TextEditingController();

  String? _selectedDepartment;
  int? _selectedDoctorId;
  DateTime? _selectedDate;
  String? _selectedTime;
  List<Doctor> _doctors = [];
  List<Doctor> _filteredDoctors = [];
  bool _isLoading = false;
  bool _isLoadingDoctors = true;
  User? _user;

  @override
  void initState() {
    super.initState();
    _user = AuthService.getCurrentUser();
    _loadDoctors();
  }

  @override
  void dispose() {
    _problemController.dispose();
    super.dispose();
  }

  Future<void> _loadDoctors() async {
    final response = await ApiService.getDoctors();
    setState(() {
      _isLoadingDoctors = false;
      if (response.success && response.data != null) {
        _doctors = response.data!;
      }
    });
  }

  void _filterDoctors(String? department) {
    setState(() {
      if (department == null) {
        _filteredDoctors = [];
      } else {
        _filteredDoctors = _doctors
            .where((d) => d.specializedIn == department && d.isAvailable)
            .toList();
      }
      _selectedDoctorId = null;
    });
  }

  Future<void> _selectDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now.add(const Duration(days: 1)),
      firstDate: now,
      lastDate: now.add(const Duration(days: 30)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: Color(0xFF1a5c96),
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() => _selectedDate = picked);
    }
  }

  Future<void> _bookAppointment() async {
    if (!_formKey.currentState!.validate()) return;

    if (_selectedDate == null) {
      _showSnackBar('Please select a date', isError: true);
      return;
    }
    if (_selectedTime == null) {
      _showSnackBar('Please select a time slot', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    final appointment = Appointment(
      studentId: _user?.studentId ?? '',
      studentName: _user?.fullName ?? '',
      phone: _user?.phone ?? '',
      email: _user?.email ?? '',
      studentDepartment: _user?.department ?? '',
      medicalDepartment: _selectedDepartment!,
      doctorId: _selectedDoctorId,
      appointmentDate: DateFormat('yyyy-MM-dd').format(_selectedDate!),
      appointmentTime: _selectedTime,
      problemDescription: _problemController.text.trim(),
    );

    final response = await ApiService.bookAppointment(appointment);

    setState(() => _isLoading = false);

    if (response.success) {
      _showSnackBar('Appointment booked successfully!');
      _resetForm();
      widget.onBooked();
    } else {
      _showSnackBar(response.error ?? 'Failed to book appointment', isError: true);
    }
  }

  void _resetForm() {
    _formKey.currentState?.reset();
    _problemController.clear();
    setState(() {
      _selectedDepartment = null;
      _selectedDoctorId = null;
      _selectedDate = null;
      _selectedTime = null;
      _filteredDoctors = [];
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
            // Patient info card
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Patient Information',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1a5c96),
                      ),
                    ),
                    const SizedBox(height: 12),
                    _InfoRow(label: 'Name', value: _user?.fullName ?? 'N/A'),
                    _InfoRow(label: 'Student ID', value: _user?.studentId ?? 'N/A'),
                    _InfoRow(label: 'Phone', value: _user?.phone ?? 'N/A'),
                    _InfoRow(label: 'Email', value: _user?.email ?? 'N/A'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Medical department
            CustomDropdown<String>(
              value: _selectedDepartment,
              label: 'Medical Department',
              prefixIcon: Icons.medical_services,
              items: MedicalSpecialty.all
                  .map((e) => DropdownMenuItem(
                        value: e.key,
                        child: Text(e.value),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() => _selectedDepartment = value);
                _filterDoctors(value);
              },
              validator: (v) => v == null ? 'Please select a department' : null,
            ),
            const SizedBox(height: 16),

            // Doctor selection
            if (_isLoadingDoctors)
              const Center(child: CircularProgressIndicator())
            else if (_selectedDepartment != null)
              CustomDropdown<int>(
                value: _selectedDoctorId,
                label: 'Preferred Doctor (Optional)',
                prefixIcon: Icons.person,
                items: [
                  const DropdownMenuItem(
                    value: null,
                    child: Text('Any available doctor'),
                  ),
                  ..._filteredDoctors.map((d) => DropdownMenuItem(
                        value: d.id,
                        child: Text('Dr. ${d.name}'),
                      )),
                ],
                onChanged: (v) => setState(() => _selectedDoctorId = v),
              ),
            const SizedBox(height: 16),

            // Date selection
            InkWell(
              onTap: _selectDate,
              borderRadius: BorderRadius.circular(12),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: 'Appointment Date',
                  prefixIcon: const Icon(Icons.calendar_today),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: Text(
                  _selectedDate != null
                      ? DateFormat('EEEE, MMM d, yyyy').format(_selectedDate!)
                      : 'Select a date',
                  style: TextStyle(
                    color: _selectedDate != null ? Colors.black : Colors.grey,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Time slots
            const Text(
              'Select Time Slot',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: TimeSlot.slots.map((slot) {
                final isSelected = _selectedTime == slot;
                return ChoiceChip(
                  label: Text(slot),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() => _selectedTime = selected ? slot : null);
                  },
                  selectedColor: const Color(0xFF1a5c96),
                  labelStyle: TextStyle(
                    color: isSelected ? Colors.white : Colors.black,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            // Problem description
            CustomTextField(
              controller: _problemController,
              label: 'Describe Your Problem',
              hint: 'Please describe your symptoms or reason for visit...',
              prefixIcon: Icons.description,
              maxLines: 4,
              validator: (v) {
                if (v?.isEmpty ?? true) return 'Please describe your problem';
                if (v!.length < 10) return 'Please provide more details';
                return null;
              },
            ),
            const SizedBox(height: 24),

            // Submit button
            PrimaryButton(
              text: 'Book Appointment',
              icon: Icons.check_circle,
              onPressed: _bookAppointment,
              isLoading: _isLoading,
            ),
          ],
        ),
      ),
    );
  }
}

/// Tab for displaying appointment list
class _AppointmentListTab extends StatelessWidget {
  final List<Appointment> appointments;
  final bool isLoading;
  final String? error;
  final VoidCallback onRefresh;
  final String emptyMessage;
  final IconData emptyIcon;

  const _AppointmentListTab({
    required this.appointments,
    required this.isLoading,
    required this.error,
    required this.onRefresh,
    required this.emptyMessage,
    required this.emptyIcon,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 48, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text(error!, style: TextStyle(color: Colors.grey.shade600)),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (appointments.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(emptyIcon, size: 64, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text(
              emptyMessage,
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: appointments.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: AppointmentCard(appointment: appointments[index]),
          );
        },
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
