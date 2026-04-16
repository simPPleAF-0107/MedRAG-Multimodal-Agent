import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../providers/user_provider.dart';
import '../utils/theme.dart';
import '../utils/ux_utils.dart';

class PatientProfileScreen extends StatefulWidget {
  final Map<String, dynamic>? initialData;

  const PatientProfileScreen({super.key, this.initialData});

  @override
  State<PatientProfileScreen> createState() => _PatientProfileScreenState();
}

class _PatientProfileScreenState extends State<PatientProfileScreen> {
  late Future<Map<String, dynamic>> _profileFuture;

  @override
  void initState() {
    super.initState();
    _profileFuture = _fetchMockProfile();
  }

  Future<Map<String, dynamic>> _fetchMockProfile() async {
    final userProvider = context.read<UserProvider>();
    final userId = userProvider.userId;
    final userName = userProvider.name;
    final userEmail = userProvider.email;

    // Simulating network delay to fetch detailed medical profile
    await Future.delayed(const Duration(milliseconds: 600));

    String? id = widget.initialData?['id']?.toString() ?? userId?.toString();
    
    // Default fallback stub profile matching Web Prototype
    final defaultProfile = {
      'name': userName ?? widget.initialData?['name'] ?? 'Unknown Patient',
      'email': userEmail ?? widget.initialData?['email'] ?? 'test@example.com',
      'age': 58,
      'sex': 'Male',
      'bloodType': 'O+',
      'phone': '+1 (555) 123-4567',
      'address': '142 Maple Ave, Springfield, IL',
      'emergencyContact': {'name': 'Mary Doe', 'relation': 'Spouse', 'phone': '+1 (555) 123-4568'},
      'conditions': ['Hypertension (Stage 2)', 'Type 2 Diabetes', 'Hyperlipidemia'],
      'allergies': ['Penicillin', 'Sulfa Drugs'],
      'medications': [
        {'name': 'Lisinopril', 'dose': '20mg', 'freq': 'Once daily', 'purpose': 'Blood Pressure'},
        {'name': 'Metformin', 'dose': '500mg', 'freq': 'Twice daily', 'purpose': 'Blood Sugar'},
      ],
      'vitals': {'bp': '148/92', 'heartRate': 82, 'temp': '98.6°F', 'weight': '198 lbs', 'height': '5\'10"', 'bmi': 28.4, 'spO2': '96%'},
    };

    // Use Web mock profiles for parity
    final mockProfiles = {
      '1': defaultProfile,
      '4': defaultProfile, // John Doe Map ID from api_service
      '5': {
        'name': 'Jane Smith', 'age': 34, 'sex': 'Female', 'bloodType': 'A+',
        'email': 'jane.smith@email.com', 'phone': '+1 (555) 234-5678',
        'address': '88 Oak Street, Chicago, IL',
        'emergencyContact': {'name': 'Robert Smith', 'relation': 'Brother', 'phone': '+1 (555) 234-5679'},
        'conditions': ['Generalized Anxiety Disorder', 'Iron Deficiency Anemia (resolved)'],
        'allergies': ['Latex', 'Ibuprofen'],
        'medications': [
            {'name': 'Sertraline', 'dose': '50mg', 'freq': 'Once daily', 'purpose': 'Anxiety'},
            {'name': 'Vitamin D3', 'dose': '2000 IU', 'freq': 'Once daily', 'purpose': 'Supplement'},
        ],
        'vitals': {'bp': '118/74', 'heartRate': 72, 'temp': '98.4°F', 'weight': '138 lbs', 'height': '5\'6"', 'bmi': 22.3, 'spO2': '99%'},
      },
      '6': {
        'name': 'Bob User', 'age': 71, 'sex': 'Male', 'bloodType': 'B-',
        'email': 'bob.user@email.com', 'phone': '+1 (555) 345-6789',
        'address': '305 Pine Lane, Evanston, IL',
        'emergencyContact': {'name': 'Susan User', 'relation': 'Daughter', 'phone': '+1 (555) 345-6790'},
        'conditions': ['Congestive Heart Failure', 'Atrial Fibrillation', 'Chronic Kidney Disease'],
        'allergies': ['ACE Inhibitors (cough)'],
        'medications': [
            {'name': 'Carvedilol', 'dose': '25mg', 'freq': 'Twice daily', 'purpose': 'Heart Failure'},
            {'name': 'Furosemide', 'dose': '40mg', 'freq': 'Once daily', 'purpose': 'Fluid Retention'},
            {'name': 'Apixaban', 'dose': '5mg', 'freq': 'Twice daily', 'purpose': 'Anticoagulation'},
        ],
        'vitals': {'bp': '156/96', 'heartRate': 98, 'temp': '98.8°F', 'weight': '215 lbs', 'height': '5\'8"', 'bmi': 32.7, 'spO2': '91%'},
      },
      '7': {
        'name': 'Alice Wong', 'age': 28, 'sex': 'Female', 'bloodType': 'AB+',
        'email': 'alice.w@email.com', 'phone': '+1 (555) 456-7890',
        'address': '1200 Lakeshore Dr, Unit 12C, Chicago, IL',
        'emergencyContact': {'name': 'David Wong', 'relation': 'Father', 'phone': '+1 (555) 456-7891'},
        'conditions': ['Migraine with Aura', 'Mild Asthma'],
        'allergies': ['Shellfish'],
        'medications': [
            {'name': 'Topiramate', 'dose': '25mg', 'freq': 'Once daily', 'purpose': 'Migraine Prevention'},
            {'name': 'Montelukast', 'dose': '10mg', 'freq': 'Once daily', 'purpose': 'Asthma Maintenance'},
        ],
        'vitals': {'bp': '112/68', 'heartRate': 66, 'temp': '98.2°F', 'weight': '125 lbs', 'height': '5\'4"', 'bmi': 21.5, 'spO2': '99%'},
      }
    };

    return mockProfiles[id] ?? defaultProfile;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text('Clinical Profile'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: ClipRRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(color: MedRagTheme.backgroundDark.withValues(alpha: 0.8)),
          ),
        ),
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _profileFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: MedRagTheme.primaryCyan));
          }
          if (snapshot.hasError || !snapshot.hasData) {
            return Center(child: Text('Failed to load profile.', style: TextStyle(color: MedRagTheme.secondaryCoral)));
          }

          final p = snapshot.data!;
          return RefreshIndicator(
            onRefresh: () async {
              UxUtils.hapticLight();
              setState(() {
                _profileFuture = _fetchMockProfile();
              });
            },
            color: MedRagTheme.primaryCyan,
            backgroundColor: MedRagTheme.surfaceDark,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top + kToolbarHeight + 16, bottom: 40, left: 20, right: 20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header
                  Row(
                    children: [
                      Container(
                        width: 80, height: 80,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: MedRagTheme.primaryCyan.withValues(alpha: 0.15),
                          border: Border.all(color: MedRagTheme.primaryCyan.withValues(alpha: 0.4), width: 2),
                          boxShadow: MedRagTheme.neonShadow,
                        ),
                        child: Center(
                          child: Text(
                            p['name'][0].toUpperCase(),
                            style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: MedRagTheme.primaryCyan),
                          ),
                        ),
                      ),
                      const SizedBox(width: 20),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(p['name'], style: Theme.of(context).textTheme.displaySmall?.copyWith(fontSize: 26)),
                            const SizedBox(height: 4),
                            Text('${p['age']} yrs • ${p['sex']} • Blood: ${p['bloodType']}', 
                                style: const TextStyle(color: Colors.white70, fontSize: 16)),
                          ],
                        ),
                      )
                    ],
                  ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.1),

                  const SizedBox(height: 32),

                  // Vitals Grid
                  Text('Current Vitals', style: Theme.of(context).textTheme.titleLarge).animate().fadeIn(delay: 100.ms),
                  const SizedBox(height: 16),
                  GridView.count(
                    crossAxisCount: 3,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                    childAspectRatio: 1.1,
                    physics: const NeverScrollableScrollPhysics(),
                    shrinkWrap: true,
                    children: [
                      _buildVitalCard('BP', p['vitals']['bp'], Icons.favorite, Colors.redAccent),
                      _buildVitalCard('HR', '${p['vitals']['heartRate']} bpm', Icons.monitor_heart, Colors.purpleAccent),
                      _buildVitalCard('SpO2', p['vitals']['spO2'], Icons.air, Colors.blueAccent),
                      _buildVitalCard('Weight', p['vitals']['weight'], Icons.fitness_center, Colors.orangeAccent),
                      _buildVitalCard('Height', p['vitals']['height'], Icons.height, Colors.greenAccent),
                      _buildVitalCard('Temp', p['vitals']['temp'], Icons.thermostat, Colors.amber),
                    ],
                  ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.1),

                  const SizedBox(height: 32),

                  // Conditions & Allergies
                  _buildSectionContainer(
                    title: 'Active Conditions',
                    icon: Icons.personal_injury_rounded,
                    color: MedRagTheme.secondaryCoral,
                    children: (p['conditions'] as List).map<Widget>((c) => _buildListItem(c, Icons.circle, MedRagTheme.secondaryCoral)).toList(),
                  ).animate().fadeIn(delay: 300.ms),

                  const SizedBox(height: 16),

                  _buildSectionContainer(
                    title: 'Allergies',
                    icon: Icons.warning_rounded,
                    color: Colors.amber,
                    children: (p['allergies'] as List).map<Widget>((a) => _buildListItem(a, Icons.coronavirus_rounded, Colors.amber)).toList(),
                  ).animate().fadeIn(delay: 400.ms),

                  const SizedBox(height: 16),

                  _buildSectionContainer(
                    title: 'Medications',
                    icon: Icons.medication_liquid_rounded,
                    color: MedRagTheme.primaryCyan,
                    children: (p['medications'] as List).map<Widget>((m) => _buildMedicationItem(m)).toList(),
                  ).animate().fadeIn(delay: 500.ms),

                  const SizedBox(height: 32),
                  
                  // Contact Info
                  Text('Contact Information', style: Theme.of(context).textTheme.titleLarge).animate().fadeIn(delay: 600.ms),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: MedRagTheme.glassDecoration,
                    child: Column(
                      children: [
                        ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: const Icon(Icons.email_outlined, color: Colors.white70),
                          title: Text(p['email'], style: const TextStyle(color: Colors.white)),
                        ),
                        ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: const Icon(Icons.phone_outlined, color: Colors.white70),
                          title: Text(p['phone'], style: const TextStyle(color: Colors.white)),
                        ),
                        ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: const Icon(Icons.home_outlined, color: Colors.white70),
                          title: Text(p['address'], style: const TextStyle(color: Colors.white)),
                        ),
                        const Divider(color: Colors.white24, height: 32),
                        const Text('Emergency Contact', style: TextStyle(color: MedRagTheme.primaryCyan, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 8),
                         ListTile(
                          contentPadding: EdgeInsets.zero,
                          title: Text(p['emergencyContact']['name'], style: const TextStyle(color: Colors.white)),
                          subtitle: Text(p['emergencyContact']['relation'], style: const TextStyle(color: Colors.white54)),
                          trailing: Text(p['emergencyContact']['phone'], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                  ).animate().fadeIn(delay: 600.ms).slideY(begin: 0.1),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildVitalCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: MedRagTheme.surfaceDark.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 6),
          Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13), textAlign: TextAlign.center),
          const SizedBox(height: 2),
          Text(title, style: TextStyle(color: MedRagTheme.textMuted, fontSize: 10), textAlign: TextAlign.center),
        ],
      ),
    );
  }

  Widget _buildSectionContainer({required String title, required IconData icon, required Color color, required List<Widget> children}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: MedRagTheme.glassDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 22),
              const SizedBox(width: 10),
              Text(title, style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 16),
          ...children,
        ],
      ),
    );
  }

  Widget _buildListItem(String text, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 4.0),
            child: Icon(icon, size: 12, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(child: Text(text, style: const TextStyle(color: Colors.white, fontSize: 15))),
        ],
      ),
    );
  }

  Widget _buildMedicationItem(Map<String, dynamic> med) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.medication, color: MedRagTheme.primaryCyan, size: 20),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${med['name']} ${med['dose']}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                const SizedBox(height: 2),
                Text(med['freq'], style: TextStyle(color: MedRagTheme.textMuted, fontSize: 13)),
              ],
            ),
          ),
          Text(med['purpose'], style: TextStyle(color: MedRagTheme.textMuted, fontSize: 12)),
        ],
      ),
    );
  }
}
