import 'package:flutter/material.dart';
import 'appointment_page.dart';

// ── Available doctors ──────────────────────────────────────────
class _BookableDoctor {
  final String name;
  final String specialty;
  final Color avatarColor;
  const _BookableDoctor(this.name, this.specialty, this.avatarColor);
}

const _kDoctors = [
  _BookableDoctor('Dr. Sarah Mitchell', 'Cardiologist', Color(0xFF4A90D9)),
  _BookableDoctor('Dr. James Patel', 'Neurologist', Color(0xFF6B8E6B)),
  _BookableDoctor('Dr. Emily Nguyen', 'Dermatologist', Color(0xFFD4886A)),
  _BookableDoctor('Dr. Robert Osei', 'Orthopedic', Color(0xFF8E6BAE)),
  _BookableDoctor('Dr. Aisha Khan', 'Pediatrician', Color(0xFFE8A838)),
  _BookableDoctor('Dr. Lucas Rivera', 'General', Color(0xFF4ABFB8)),
];

const _kTimeSlots = [
  '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
  '11:00 AM', '11:30 AM', '01:00 PM', '01:30 PM',
  '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM',
  '04:00 PM', '04:30 PM', '05:00 PM', '05:30 PM',
];

const _kMonths = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

const _kDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

// ── Book appointment page ──────────────────────────────────────
class BookAppointmentPage extends StatefulWidget {
  /// When non-null, the form is pre-filled for a reschedule.
  final Appointment? existing;
  const BookAppointmentPage({super.key, this.existing});

  @override
  State<BookAppointmentPage> createState() => _BookAppointmentPageState();
}

class _BookAppointmentPageState extends State<BookAppointmentPage> {
  static const _primaryBlue = Color(0xFF1a73e8);
  static const _lightBlue = Color(0xFFe8f0fe);

  int _selectedDoctorIdx = 0;
  late DateTime _selectedDate;
  String? _selectedTime;
  String _visitType = 'In-Person';

  // The list of upcoming dates shown in the strip (today + 29 days)
  late final List<DateTime> _dates;

  @override
  void initState() {
    super.initState();
    final today = DateTime.now();
    _dates = List.generate(30, (i) => today.add(Duration(days: i)));
    _selectedDate = _dates[0];

    // Pre-fill if rescheduling
    if (widget.existing != null) {
      final e = widget.existing!;
      _visitType = e.type;
      _selectedTime = e.time;
      final idx = _kDoctors.indexWhere((d) => d.name == e.doctorName);
      if (idx >= 0) _selectedDoctorIdx = idx;
    }
  }

  bool get _canConfirm => _selectedTime != null;

  void _confirm() {
    if (!_canConfirm) return;
    final doctor = _kDoctors[_selectedDoctorIdx];
    final result = Appointment(
      doctorName: doctor.name,
      specialty: doctor.specialty,
      date: _selectedDate.day.toString().padLeft(2, '0'),
      month: _kMonths[_selectedDate.month - 1],
      time: _selectedTime!,
      type: _visitType,
      status: AppointmentStatus.upcoming,
      avatarColor: doctor.avatarColor,
    );
    Navigator.pop(context, result);
  }

  @override
  Widget build(BuildContext context) {
    final isReschedule = widget.existing != null;
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FF),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 20),
          color: const Color(0xFF1a1a2e),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          isReschedule ? 'Reschedule Appointment' : 'Book Appointment',
          style: const TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1a1a2e),
          ),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _sectionLabel('Select Doctor'),
                  _buildDoctorPicker(),
                  _sectionLabel('Select Date'),
                  _buildDateStrip(),
                  _sectionLabel('Select Time'),
                  _buildTimeGrid(),
                  _sectionLabel('Visit Type'),
                  _buildVisitTypeToggle(),
                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
          _buildConfirmButton(),
        ],
      ),
    );
  }

  // ── Section label ────────────────────────────────────────────
  Widget _sectionLabel(String text) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 10),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 15,
          fontWeight: FontWeight.bold,
          color: Color(0xFF1a1a2e),
        ),
      ),
    );
  }

  // ── Doctor picker ────────────────────────────────────────────
  Widget _buildDoctorPicker() {
    return SizedBox(
      height: 110,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        scrollDirection: Axis.horizontal,
        itemCount: _kDoctors.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (context, i) {
          final doc = _kDoctors[i];
          final selected = _selectedDoctorIdx == i;
          return GestureDetector(
            onTap: () => setState(() => _selectedDoctorIdx = i),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              width: 90,
              padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
              decoration: BoxDecoration(
                color: selected ? _primaryBlue : Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: selected
                        ? _primaryBlue.withAlpha(80)
                        : Colors.black.withAlpha(13),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
                border: Border.all(
                  color: selected ? _primaryBlue : Colors.transparent,
                  width: 1.5,
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: doc.avatarColor.withAlpha(selected ? 60 : 38),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(Icons.person,
                        color: selected ? Colors.white : doc.avatarColor,
                        size: 22),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    doc.name.replaceFirst('Dr. ', ''),
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: selected ? Colors.white : const Color(0xFF1a1a2e),
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Date strip ───────────────────────────────────────────────
  Widget _buildDateStrip() {
    return SizedBox(
      height: 80,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        scrollDirection: Axis.horizontal,
        itemCount: _dates.length,
        separatorBuilder: (_, __) => const SizedBox(width: 10),
        itemBuilder: (context, i) {
          final date = _dates[i];
          final selected = _selectedDate.day == date.day &&
              _selectedDate.month == date.month;
          final dayName = _kDays[date.weekday - 1];
          return GestureDetector(
            onTap: () => setState(() {
              _selectedDate = date;
              _selectedTime = null; // reset time when date changes
            }),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              width: 54,
              decoration: BoxDecoration(
                color: selected ? _primaryBlue : Colors.white,
                borderRadius: BorderRadius.circular(14),
                boxShadow: [
                  BoxShadow(
                    color: selected
                        ? _primaryBlue.withAlpha(80)
                        : Colors.black.withAlpha(13),
                    blurRadius: 6,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    dayName,
                    style: TextStyle(
                      fontSize: 11,
                      color: selected ? Colors.white70 : Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${date.day}',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: selected ? Colors.white : const Color(0xFF1a1a2e),
                    ),
                  ),
                  Text(
                    _kMonths[date.month - 1],
                    style: TextStyle(
                      fontSize: 10,
                      color: selected ? Colors.white70 : Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Time slot grid ───────────────────────────────────────────
  Widget _buildTimeGrid() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Wrap(
        spacing: 10,
        runSpacing: 10,
        children: _kTimeSlots.map((slot) {
          final selected = _selectedTime == slot;
          return GestureDetector(
            onTap: () => setState(() => _selectedTime = slot),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: selected ? _primaryBlue : Colors.white,
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: selected
                        ? _primaryBlue.withAlpha(80)
                        : Colors.black.withAlpha(13),
                    blurRadius: 6,
                    offset: const Offset(0, 3),
                  ),
                ],
                border: Border.all(
                  color: selected ? _primaryBlue : const Color(0xFFE8E8E8),
                ),
              ),
              child: Text(
                slot,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: selected ? Colors.white : Colors.black87,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ── Visit type toggle ────────────────────────────────────────
  Widget _buildVisitTypeToggle() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: ['In-Person', 'Video Call'].map((type) {
          final selected = _visitType == type;
          final icon = type == 'Video Call'
              ? Icons.videocam_outlined
              : Icons.local_hospital_outlined;
          return Expanded(
            child: GestureDetector(
              onTap: () => setState(() => _visitType = type),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                margin: EdgeInsets.only(
                  right: type == 'In-Person' ? 8 : 0,
                ),
                padding: const EdgeInsets.symmetric(vertical: 14),
                decoration: BoxDecoration(
                  color: selected ? _primaryBlue : Colors.white,
                  borderRadius: BorderRadius.circular(14),
                  boxShadow: [
                    BoxShadow(
                      color: selected
                          ? _primaryBlue.withAlpha(80)
                          : Colors.black.withAlpha(13),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                  border: Border.all(
                    color: selected ? _primaryBlue : const Color(0xFFE8E8E8),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(icon,
                        color: selected ? Colors.white : Colors.grey,
                        size: 18),
                    const SizedBox(width: 8),
                    Text(
                      type,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color:
                            selected ? Colors.white : const Color(0xFF1a1a2e),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  // ── Confirm button ───────────────────────────────────────────
  Widget _buildConfirmButton() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      child: Column(
        children: [
          if (_selectedTime != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.info_outline,
                      size: 14, color: Colors.grey),
                  const SizedBox(width: 6),
                  Text(
                    '${_kDoctors[_selectedDoctorIdx].name} · '
                    '${_selectedDate.day} ${_kMonths[_selectedDate.month - 1]} · '
                    '$_selectedTime',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _canConfirm ? _confirm : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: _primaryBlue,
                disabledBackgroundColor: _lightBlue,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
                padding: const EdgeInsets.symmetric(vertical: 16),
                elevation: 0,
              ),
              child: Text(
                widget.existing != null
                    ? 'Confirm Reschedule'
                    : 'Confirm Booking',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
