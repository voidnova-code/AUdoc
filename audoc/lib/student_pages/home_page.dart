import 'package:flutter/material.dart';
import 'appointment_page.dart';

// ── Data models ────────────────────────────────────────────────
class _Specialty {
  final String icon;
  final String label;
  const _Specialty(this.icon, this.label);
}

class _Doctor {
  final String name;
  final String specialty;
  final double rating;
  final int reviews;
  final Color avatarColor;
  const _Doctor({
    required this.name,
    required this.specialty,
    required this.rating,
    required this.reviews,
    required this.avatarColor,
  });
}

// ── Home page ──────────────────────────────────────────────────
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _navIndex = 0;
  int _selectedSpecialty = 0;

  static const _primaryBlue = Color(0xFF1a73e8);
  static const _lightBlue = Color(0xFFe8f0fe);

  final List<_Specialty> _specialties = const [
    _Specialty('🩺', 'General'),
    _Specialty('🫀', 'Cardiology'),
    _Specialty('🧠', 'Neurology'),
    _Specialty('🦴', 'Orthopedics'),
    _Specialty('👶', 'Pediatrics'),
    _Specialty('🧴', 'Dermatology'),
    _Specialty('🦷', 'Dentistry'),
    _Specialty('👁️', 'Eye Care'),
  ];

  final List<_Doctor> _doctors = const [
    _Doctor(
      name: 'Dr. Sarah Mitchell',
      specialty: 'Cardiologist',
      rating: 4.9,
      reviews: 320,
      avatarColor: Color(0xFF4A90D9),
    ),
    _Doctor(
      name: 'Dr. James Patel',
      specialty: 'Neurologist',
      rating: 4.8,
      reviews: 215,
      avatarColor: Color(0xFF6B8E6B),
    ),
    _Doctor(
      name: 'Dr. Emily Nguyen',
      specialty: 'Dermatologist',
      rating: 4.9,
      reviews: 410,
      avatarColor: Color(0xFFD4886A),
    ),
    _Doctor(
      name: 'Dr. Robert Osei',
      specialty: 'Orthopedic',
      rating: 4.7,
      reviews: 280,
      avatarColor: Color(0xFF8E6BAE),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FF),
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // ── App Bar ──────────────────────────────────────
            SliverToBoxAdapter(child: _buildTopBar()),

            // ── Search bar ───────────────────────────────────
            SliverToBoxAdapter(child: _buildSearchBar()),

            // ── Hero banner ──────────────────────────────────
            SliverToBoxAdapter(child: _buildHeroBanner()),

            // ── Specialties ──────────────────────────────────
            SliverToBoxAdapter(
              child: _buildSectionHeader('Specialties', 'See All'),
            ),
            SliverToBoxAdapter(child: _buildSpecialtyRow()),

            // ── Top Doctors ──────────────────────────────────
            SliverToBoxAdapter(
              child: _buildSectionHeader('Top Doctors', 'See All'),
            ),
            SliverToBoxAdapter(child: _buildDoctorRow()),

            // ── Upcoming appointment ─────────────────────────
            SliverToBoxAdapter(
              child: _buildSectionHeader('Next Appointment', null),
            ),
            SliverToBoxAdapter(child: _buildAppointmentCard()),

            const SliverToBoxAdapter(child: SizedBox(height: 20)),
          ],
        ),
      ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  // ── Top bar ─────────────────────────────────────────────────
  Widget _buildTopBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 18, 16, 4),
      child: Row(
        children: [
          // Avatar
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: _lightBlue,
              shape: BoxShape.circle,
              border: Border.all(color: _primaryBlue, width: 1.5),
            ),
            child: const Icon(Icons.person, color: _primaryBlue, size: 24),
          ),
          const SizedBox(width: 12),
          // Greeting
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Good Morning 👋',
                  style: TextStyle(fontSize: 13, color: Colors.grey),
                ),
                Text(
                  'Find Your Doctor',
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1a1a2e),
                  ),
                ),
              ],
            ),
          ),
          // Notification icon
          Stack(
            children: [
              IconButton(
                onPressed: () {},
                icon: const Icon(
                  Icons.notifications_outlined,
                  color: Color(0xFF1a1a2e),
                  size: 26,
                ),
              ),
              Positioned(
                top: 8,
                right: 8,
                child: Container(
                  width: 9,
                  height: 9,
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ── Search bar ───────────────────────────────────────────────
  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: TextField(
        decoration: InputDecoration(
          hintText: 'Search doctors, specialties…',
          hintStyle: const TextStyle(color: Colors.grey, fontSize: 14),
          prefixIcon: const Icon(Icons.search, color: _primaryBlue),
          suffixIcon: Container(
            margin: const EdgeInsets.all(6),
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: _primaryBlue,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.tune, color: Colors.white, size: 18),
          ),
          filled: true,
          fillColor: Colors.white,
          contentPadding: const EdgeInsets.symmetric(
            vertical: 14,
            horizontal: 16,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(14),
            borderSide: BorderSide.none,
          ),
        ),
      ),
    );
  }

  // ── Hero banner ──────────────────────────────────────────────
  Widget _buildHeroBanner() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1a73e8), Color(0xFF1558b0)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Your Health,\nOur Priority',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Book a certified doctor\nin minutes.',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 14),
                ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: _primaryBlue,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 10,
                    ),
                    elevation: 0,
                  ),
                  child: const Text(
                    'Book Now',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),
          // Decorative icon
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.white.withAlpha(30),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.local_hospital,
              color: Colors.white,
              size: 44,
            ),
          ),
        ],
      ),
    );
  }

  // ── Section header ───────────────────────────────────────────
  Widget _buildSectionHeader(String title, String? action) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 18, 20, 10),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1a1a2e),
            ),
          ),
          if (action != null)
            GestureDetector(
              onTap: () {},
              child: Text(
                action,
                style: const TextStyle(
                  color: _primaryBlue,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
        ],
      ),
    );
  }

  // ── Specialty chips row ──────────────────────────────────────
  Widget _buildSpecialtyRow() {
    return SizedBox(
      height: 88,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        scrollDirection: Axis.horizontal,
        itemCount: _specialties.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (context, i) {
          final selected = _selectedSpecialty == i;
          final sp = _specialties[i];
          return GestureDetector(
            onTap: () => setState(() => _selectedSpecialty = i),
            child: Container(
              width: 72,
              decoration: BoxDecoration(
                color: selected ? _primaryBlue : Colors.white,
                borderRadius: BorderRadius.circular(14),
                boxShadow: [
                  BoxShadow(
                    color: selected
                        ? _primaryBlue.withAlpha(77)
                        : Colors.black.withAlpha(13),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(sp.icon, style: const TextStyle(fontSize: 26)),
                  const SizedBox(height: 4),
                  Text(
                    sp.label,
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: selected ? Colors.white : Colors.black87,
                    ),
                    textAlign: TextAlign.center,
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

  // ── Doctor cards row ─────────────────────────────────────────
  Widget _buildDoctorRow() {
    return SizedBox(
      height: 210,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        scrollDirection: Axis.horizontal,
        itemCount: _doctors.length,
        separatorBuilder: (_, __) => const SizedBox(width: 14),
        itemBuilder: (context, i) => _DoctorCard(doctor: _doctors[i]),
      ),
    );
  }

  // ── Upcoming appointment card ────────────────────────────────
  Widget _buildAppointmentCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      padding: const EdgeInsets.all(18),
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
      child: Row(
        children: [
          // Date badge
          Container(
            width: 54,
            height: 60,
            decoration: BoxDecoration(
              color: _lightBlue,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  '15',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: _primaryBlue,
                  ),
                ),
                Text(
                  'Mar',
                  style: TextStyle(fontSize: 11, color: _primaryBlue),
                ),
              ],
            ),
          ),
          const SizedBox(width: 14),
          // Info
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Dr. Sarah Mitchell',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                    color: Color(0xFF1a1a2e),
                  ),
                ),
                SizedBox(height: 3),
                Text(
                  'Cardiologist · In-Person',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
                SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.access_time, size: 13, color: _primaryBlue),
                    SizedBox(width: 4),
                    Text(
                      '10:30 AM',
                      style: TextStyle(
                        fontSize: 12,
                        color: _primaryBlue,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Status badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
            decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              'Confirmed',
              style: TextStyle(
                color: Color(0xFF388E3C),
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Bottom navigation bar ────────────────────────────────────
  Widget _buildBottomNav() {
    return BottomNavigationBar(
      currentIndex: _navIndex,
      onTap: (i) {
        if (i == 1) {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const AppointmentPage()),
          );
          return;
        }
        setState(() => _navIndex = i);
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
}

// ── Doctor card widget ──────────────────────────────────────────
class _DoctorCard extends StatelessWidget {
  final _Doctor doctor;
  const _DoctorCard({required this.doctor});

  static const _primaryBlue = Color(0xFF1a73e8);
  static const _lightBlue = Color(0xFFe8f0fe);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 150,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(13),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Avatar circle
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: doctor.avatarColor.withAlpha(38),
              shape: BoxShape.circle,
            ),
            child: Icon(Icons.person, color: doctor.avatarColor, size: 36),
          ),
          const SizedBox(height: 10),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Text(
              doctor.name,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 13,
                color: Color(0xFF1a1a2e),
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: _lightBlue,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              doctor.specialty,
              style: const TextStyle(
                color: _primaryBlue,
                fontSize: 10,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.star, color: Colors.amber, size: 13),
              const SizedBox(width: 2),
              Text(
                '${doctor.rating}',
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1a1a2e),
                ),
              ),
              Text(
                ' (${doctor.reviews})',
                style: const TextStyle(fontSize: 10, color: Colors.grey),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
