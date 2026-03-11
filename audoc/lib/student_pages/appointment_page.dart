import 'package:flutter/material.dart';
import 'book_appointment_page.dart';

// ── Public data model ───────────────────────────────────────────
enum AppointmentStatus { upcoming, completed, cancelled }

class Appointment {
  final String doctorName;
  final String specialty;
  final String date;
  final String month;
  final String time;
  final String type; // 'In-Person' or 'Video Call'
  final AppointmentStatus status;
  final Color avatarColor;

  const Appointment({
    required this.doctorName,
    required this.specialty,
    required this.date,
    required this.month,
    required this.time,
    required this.type,
    required this.status,
    required this.avatarColor,
  });

  Appointment copyWith({
    AppointmentStatus? status,
    String? date,
    String? month,
    String? time,
    String? type,
  }) {
    return Appointment(
      doctorName: doctorName,
      specialty: specialty,
      date: date ?? this.date,
      month: month ?? this.month,
      time: time ?? this.time,
      type: type ?? this.type,
      status: status ?? this.status,
      avatarColor: avatarColor,
    );
  }
}

// ── Appointment page ───────────────────────────────────────────
class AppointmentPage extends StatefulWidget {
  const AppointmentPage({super.key});

  @override
  State<AppointmentPage> createState() => _AppointmentPageState();
}

class _AppointmentPageState extends State<AppointmentPage>
    with SingleTickerProviderStateMixin {
  static const _primaryBlue = Color(0xFF1a73e8);
  static const _lightBlue = Color(0xFFe8f0fe);

  late TabController _tabController;

  // Mutable — new bookings / cancellations update this list
  List<Appointment> _appointments = [
    // Upcoming
    const Appointment(
      doctorName: 'Dr. Sarah Mitchell',
      specialty: 'Cardiologist',
      date: '15',
      month: 'Mar',
      time: '10:30 AM',
      type: 'In-Person',
      status: AppointmentStatus.upcoming,
      avatarColor: Color(0xFF4A90D9),
    ),
    const Appointment(
      doctorName: 'Dr. James Patel',
      specialty: 'Neurologist',
      date: '22',
      month: 'Mar',
      time: '02:00 PM',
      type: 'Video Call',
      status: AppointmentStatus.upcoming,
      avatarColor: Color(0xFF6B8E6B),
    ),
    const Appointment(
      doctorName: 'Dr. Emily Nguyen',
      specialty: 'Dermatologist',
      date: '28',
      month: 'Mar',
      time: '11:00 AM',
      type: 'In-Person',
      status: AppointmentStatus.upcoming,
      avatarColor: Color(0xFFD4886A),
    ),
    // Completed
    const Appointment(
      doctorName: 'Dr. Robert Osei',
      specialty: 'Orthopedic',
      date: '02',
      month: 'Feb',
      time: '09:00 AM',
      type: 'In-Person',
      status: AppointmentStatus.completed,
      avatarColor: Color(0xFF8E6BAE),
    ),
    const Appointment(
      doctorName: 'Dr. Sarah Mitchell',
      specialty: 'Cardiologist',
      date: '18',
      month: 'Jan',
      time: '03:30 PM',
      type: 'Video Call',
      status: AppointmentStatus.completed,
      avatarColor: Color(0xFF4A90D9),
    ),
    // Cancelled
    const Appointment(
      doctorName: 'Dr. James Patel',
      specialty: 'Neurologist',
      date: '10',
      month: 'Feb',
      time: '01:00 PM',
      type: 'In-Person',
      status: AppointmentStatus.cancelled,
      avatarColor: Color(0xFF6B8E6B),
    ),
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  List<Appointment> _filtered(AppointmentStatus status) =>
      _appointments.where((a) => a.status == status).toList();

  // ── Actions ──────────────────────────────────────────────────
  void _cancelAppointment(Appointment appt) {
    setState(() {
      final idx = _appointments.indexOf(appt);
      if (idx >= 0) {
        _appointments[idx] = appt.copyWith(status: AppointmentStatus.cancelled);
      }
    });
  }

  Future<void> _openBooking({Appointment? existing}) async {
    final result = await Navigator.push<Appointment>(
      context,
      MaterialPageRoute(
        builder: (_) => BookAppointmentPage(existing: existing),
      ),
    );
    if (result == null) return;
    setState(() {
      if (existing != null) {
        final idx = _appointments.indexOf(existing);
        if (idx >= 0) {
          _appointments[idx] = result;
        }
      } else {
        _appointments.add(result);
      }
    });
    // Jump to Upcoming tab so the user sees the new/rescheduled appointment
    _tabController.animateTo(0);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FF),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            _buildTabBar(),
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildList(_filtered(AppointmentStatus.upcoming)),
                  _buildList(_filtered(AppointmentStatus.completed)),
                  _buildList(_filtered(AppointmentStatus.cancelled)),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomNav(context),
    );
  }

  // ── Bottom navigation bar ────────────────────────────────────
  Widget _buildBottomNav(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: 1,
      onTap: (i) {
        if (i == 0) Navigator.pop(context);
      },
      type: BottomNavigationBarType.fixed,
      selectedItemColor: _primaryBlue,
      unselectedItemColor: Colors.grey,
      backgroundColor: Colors.white,
      elevation: 12,
      selectedLabelStyle: const TextStyle(
        fontWeight: FontWeight.w600,
        fontSize: 11,
      ),
      unselectedLabelStyle: const TextStyle(fontSize: 11),
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home_outlined),
          activeIcon: Icon(Icons.home),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.calendar_today_outlined),
          activeIcon: Icon(Icons.calendar_today),
          label: 'Appointments',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.medical_services_outlined),
          activeIcon: Icon(Icons.medical_services),
          label: 'Doctors',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.person_outline),
          activeIcon: Icon(Icons.person),
          label: 'Profile',
        ),
      ],
    );
  }

  // ── Header ───────────────────────────────────────────────────
  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
      child: Row(
        children: [
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'My Appointments',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1a1a2e),
                  ),
                ),
                SizedBox(height: 2),
                Text(
                  'Track and manage your visits',
                  style: TextStyle(fontSize: 13, color: Colors.grey),
                ),
              ],
            ),
          ),
          // New appointment button
          GestureDetector(
            onTap: () => _openBooking(),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
              decoration: BoxDecoration(
                color: _primaryBlue,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Row(
                children: [
                  Icon(Icons.add, color: Colors.white, size: 16),
                  SizedBox(width: 4),
                  Text(
                    'New',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Tab bar ──────────────────────────────────────────────────
  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(13),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: TabBar(
        controller: _tabController,
        dividerColor: Colors.transparent,
        indicatorSize: TabBarIndicatorSize.tab,
        indicator: BoxDecoration(
          color: _primaryBlue,
          borderRadius: BorderRadius.circular(12),
        ),
        labelColor: Colors.white,
        unselectedLabelColor: Colors.grey,
        labelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
        unselectedLabelStyle: const TextStyle(
          fontWeight: FontWeight.w500,
          fontSize: 13,
        ),
        tabs: [
          _tab('Upcoming', _filtered(AppointmentStatus.upcoming).length),
          _tab('Completed', _filtered(AppointmentStatus.completed).length),
          _tab('Cancelled', _filtered(AppointmentStatus.cancelled).length),
        ],
      ),
    );
  }

  Tab _tab(String label, int count) => Tab(
    child: Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(label),
        const SizedBox(width: 5),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(60),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text('$count', style: const TextStyle(fontSize: 11)),
        ),
      ],
    ),
  );

  // ── Appointment list ─────────────────────────────────────────
  Widget _buildList(List<Appointment> items) {
    if (items.isEmpty) return _buildEmptyState();
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
      itemCount: items.length,
      separatorBuilder: (_, __) => const SizedBox(height: 14),
      itemBuilder: (context, i) => _AppointmentCard(
        appointment: items[i],
        onCancel: () => _cancelAppointment(items[i]),
        onReschedule: () => _openBooking(existing: items[i]),
      ),
    );
  }

  // ── Empty state ──────────────────────────────────────────────
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: const BoxDecoration(
              color: _lightBlue,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.calendar_today_outlined,
              color: _primaryBlue,
              size: 36,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'No appointments here',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1a1a2e),
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Book a doctor to get started',
            style: TextStyle(fontSize: 13, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

// ── Appointment card widget ──────────────────────────────────────
class _AppointmentCard extends StatelessWidget {
  final Appointment appointment;
  final VoidCallback onCancel;
  final VoidCallback onReschedule;

  const _AppointmentCard({
    required this.appointment,
    required this.onCancel,
    required this.onReschedule,
  });

  static const _primaryBlue = Color(0xFF1a73e8);
  static const _lightBlue = Color(0xFFe8f0fe);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(13),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Date badge
              Container(
                width: 54,
                height: 60,
                decoration: BoxDecoration(
                  color: _lightBlue,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      appointment.date,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: _primaryBlue,
                      ),
                    ),
                    Text(
                      appointment.month,
                      style: const TextStyle(fontSize: 11, color: _primaryBlue),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 14),
              // Doctor info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      appointment.doctorName,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                        color: Color(0xFF1a1a2e),
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      '${appointment.specialty} · ${appointment.type}',
                      style: const TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    const SizedBox(height: 7),
                    Row(
                      children: [
                        const Icon(
                          Icons.access_time,
                          size: 13,
                          color: _primaryBlue,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          appointment.time,
                          style: const TextStyle(
                            fontSize: 12,
                            color: _primaryBlue,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(width: 10),
                        Icon(
                          appointment.type == 'Video Call'
                              ? Icons.videocam_outlined
                              : Icons.local_hospital_outlined,
                          size: 13,
                          color: Colors.grey,
                        ),
                        const SizedBox(width: 3),
                        Text(
                          appointment.type,
                          style: const TextStyle(
                            fontSize: 11,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Status pill
              _buildStatusBadge(appointment.status),
            ],
          ),
          // Action buttons (only for upcoming)
          if (appointment.status == AppointmentStatus.upcoming) ...[
            const SizedBox(height: 14),
            const Divider(height: 1, color: Color(0xFFF0F0F0)),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _confirmCancel(context),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Color(0xFFE0E0E0)),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 10),
                    ),
                    child: const Text(
                      'Cancel',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton(
                    onPressed: onReschedule,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _primaryBlue,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      elevation: 0,
                    ),
                    child: const Text(
                      'Reschedule',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  void _confirmCancel(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text(
          'Cancel Appointment',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
        ),
        content: Text(
          'Cancel your appointment with ${appointment.doctorName} on '
          '${appointment.date} ${appointment.month} at ${appointment.time}?',
          style: const TextStyle(fontSize: 14, color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Keep it'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              onCancel();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFD32F2F),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              elevation: 0,
            ),
            child: const Text('Yes, Cancel'),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(AppointmentStatus status) {
    late Color bg;
    late Color fg;
    late String label;

    switch (status) {
      case AppointmentStatus.upcoming:
        bg = const Color(0xFFE3F2FD);
        fg = _primaryBlue;
        label = 'Upcoming';
      case AppointmentStatus.completed:
        bg = const Color(0xFFE8F5E9);
        fg = const Color(0xFF388E3C);
        label = 'Completed';
      case AppointmentStatus.cancelled:
        bg = const Color(0xFFFFEBEE);
        fg = const Color(0xFFD32F2F);
        label = 'Cancelled';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(color: fg, fontSize: 11, fontWeight: FontWeight.bold),
      ),
    );
  }
}
