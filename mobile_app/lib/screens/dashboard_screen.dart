import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../providers/report_provider.dart';
import '../providers/user_provider.dart';
import '../widgets/risk_score_widget.dart';
import '../widgets/report_card.dart';
import '../utils/ux_utils.dart';
import '../utils/theme.dart';
import '../main.dart';
import 'patient_profile_screen.dart';
import 'appointment_booking_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (context.read<ReportProvider>().patientHistory == null) {
         context.read<ReportProvider>().loadPatientHistory("1");
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    bool isDoctor = context.watch<UserProvider>().isDoctor;
    String userName = context.watch<UserProvider>().name ?? context.watch<UserProvider>().email ?? 'User';

    return Scaffold(
      body: isDoctor ? _buildDoctorDashboard(userName) : _buildPatientDashboard(userName),
    );
  }

  Widget _buildDoctorDashboard(String displayName) {
    final List<Map<String, dynamic>> mockPatients = [
      {'id': '4', 'name': 'John Doe', 'risk': 68, 'lastVisit': '2026-03-20', 'status': 'High Risk'},
      {'id': '5', 'name': 'Jane Smith', 'risk': 42, 'lastVisit': '2026-03-15', 'status': 'Stable'},
      {'id': '6', 'name': 'Bob User', 'risk': 85, 'lastVisit': '2026-03-21', 'status': 'Critical'},
      {'id': '7', 'name': 'Alice Wong', 'risk': 25, 'lastVisit': '2026-03-10', 'status': 'Stable'},
    ];

    return CustomScrollView(
      slivers: [
        SliverAppBar(
          expandedHeight: 180,
          floating: false,
          pinned: true,
          backgroundColor: MedRagTheme.backgroundDark,
          flexibleSpace: FlexibleSpaceBar(
            titlePadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            title: Text('Clinical Command', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            background: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [MedRagTheme.backgroundDark, MedRagTheme.primaryCyan.withValues(alpha: 0.1)],
                )
              ),
              child: Stack(
                children: [
                   Positioned(
                     right: -50, top: -50,
                     child: Container(
                       width: 200, height: 200,
                       decoration: BoxDecoration(shape: BoxShape.circle, color: MedRagTheme.primaryCyan.withValues(alpha: 0.05)),
                     ).animate(onPlay: (controller) => controller.repeat()).moveX(end: 30, duration: 3.seconds, curve: Curves.easeInOutSine),
                   )
                ],
              ),
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.notifications_outlined), 
              onPressed: () { UxUtils.hapticLight(); UxUtils.showToast(context, 'No new notifications'); }
            ),
            IconButton(
              icon: const Icon(Icons.logout_rounded),
              onPressed: () { UxUtils.hapticMedium(); context.read<UserProvider>().logout(); }
            )
          ],
        ),
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Welcome, $displayName', style: Theme.of(context).textTheme.displayMedium),
                const SizedBox(height: 24),

                // Quick Stats Row
                Row(
                  children: [
                    Expanded(child: _buildStatCard('Total Patients', '${mockPatients.length}', Icons.people_alt_rounded, MedRagTheme.primaryCyan)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildStatCard('High Risk', '${mockPatients.where((p) => p['status'] == 'High Risk' || p['status'] == 'Critical').length}', Icons.warning_rounded, MedRagTheme.secondaryCoral)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildStatCard('Stable', '${mockPatients.where((p) => p['status'] == 'Stable').length}', Icons.check_circle_rounded, const Color(0xFF34D399))),
                  ],
                ).animate().fadeIn(delay: 100.ms).slideY(begin: 0.2, end: 0),

                const SizedBox(height: 32),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Your Patients', style: Theme.of(context).textTheme.titleLarge),
                    Text('${mockPatients.length} Total', style: TextStyle(color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5))),
                  ],
                ),
              ],
            ).animate().fadeIn(duration: 500.ms).slideY(begin: 0.1, end: 0, curve: Curves.easeOutQuad),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 0),
          sliver: SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final p = mockPatients[index];
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: MedRagTheme.glassDecoration,
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
                    leading: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
                        shape: BoxShape.circle,
                        border: Border.all(color: MedRagTheme.primaryCyan.withValues(alpha: 0.3)),
                      ),
                      child: Text(p['name'][0], style: const TextStyle(color: MedRagTheme.primaryCyan, fontWeight: FontWeight.bold, fontSize: 18)),
                    ),
                    title: Text(p['name'], style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white, fontWeight: FontWeight.bold)),
                    subtitle: Text('Last Visit: ${p['lastVisit']}', style: TextStyle(color: MedRagTheme.textMuted)),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('Score: ${p['risk']}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 16)),
                        Text('${p['status']}', style: TextStyle(
                          color: p['status'] == 'High Risk' || p['status'] == 'Critical' ? Colors.redAccent 
                               : p['status'] == 'Moderate' ? Colors.orangeAccent 
                               : Colors.greenAccent,
                          fontWeight: FontWeight.bold,
                          fontSize: 12
                        )),
                      ],
                    ),
                    onTap: () {
                      UxUtils.hapticLight();
                      _showPatientDetailSheet(context, p);
                    },
                  ),
                ).animate().fadeIn(delay: (100 * index).ms, duration: 400.ms).slideX(begin: 0.1, end: 0, curve: Curves.easeOut);
              },
              childCount: mockPatients.length,
            ),
          ),
        ),
        const SliverPadding(padding: EdgeInsets.only(bottom: 120)),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(color: color, fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(color: MedRagTheme.textMuted, fontSize: 11), textAlign: TextAlign.center),
        ],
      ),
    );
  }

  void _showPatientDetailSheet(BuildContext context, Map<String, dynamic> patient) {
    final riskColor = patient['status'] == 'High Risk' || patient['status'] == 'Critical'
        ? Colors.redAccent
        : patient['status'] == 'Moderate'
            ? Colors.orangeAccent
            : Colors.greenAccent;

    showModalBottomSheet(
      context: context,
      backgroundColor: MedRagTheme.surfaceDark,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40, height: 4,
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                    border: Border.all(color: MedRagTheme.primaryCyan.withValues(alpha: 0.3)),
                  ),
                  child: Text(
                    patient['name'][0],
                    style: const TextStyle(color: MedRagTheme.primaryCyan, fontWeight: FontWeight.bold, fontSize: 24),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(patient['name'], style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text('Last Visit: ${patient['lastVisit']}', style: TextStyle(color: MedRagTheme.textMuted)),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Column(
                    children: [
                      const Text('Risk Level', style: TextStyle(color: MedRagTheme.textMuted, fontSize: 12)),
                      const SizedBox(height: 8),
                      Text(patient['status'], style: TextStyle(color: riskColor, fontWeight: FontWeight.bold, fontSize: 18)),
                    ],
                  ),
                  Container(width: 1, height: 40, color: Colors.white.withValues(alpha: 0.1)),
                  Column(
                    children: [
                      const Text('Risk Score', style: TextStyle(color: MedRagTheme.textMuted, fontSize: 12)),
                      const SizedBox(height: 8),
                      Text('${patient['risk']}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  UxUtils.hapticLight();
                  Navigator.of(context).push(MaterialPageRoute(
                    builder: (context) => PatientProfileScreen(initialData: patient)
                  ));
                },
                icon: const Icon(Icons.open_in_new_rounded, size: 18),
                label: const Text('View Full Profile'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPatientDashboard(String loggedInName) {
    return Consumer<ReportProvider>(
      builder: (context, provider, child) {
        final isLoading = provider.isLoading && provider.patientHistory == null;
        final reports = (provider.patientHistory?['reports'] as List?) ?? [];

        // Compute dynamic risk from reports
        int riskScore = 12;
        String riskLevel = 'Low';
        if (reports.isNotEmpty) {
          final avgConfidence = reports
              .map((r) => (r['confidence_calibration']?['overall_confidence'] ?? 50).toDouble())
              .reduce((a, b) => a + b) / reports.length;
          riskScore = (100 - avgConfidence).round().clamp(0, 100);
          riskLevel = riskScore < 30 ? 'Low' : riskScore < 60 ? 'Moderate' : 'High';
        }

        return RefreshIndicator(
          onRefresh: () async {
            UxUtils.hapticLight();
            await provider.loadPatientHistory(context.read<UserProvider>().userId ?? "1");
          },
          color: MedRagTheme.primaryCyan,
          backgroundColor: MedRagTheme.surfaceDark,
          child: CustomScrollView(
            physics: const BouncingScrollPhysics(parent: AlwaysScrollableScrollPhysics()),
            slivers: [
              SliverAppBar(
                expandedHeight: 120,
                floating: false,
                pinned: true,
                backgroundColor: MedRagTheme.backgroundDark.withValues(alpha: 0.9),
                title: Text('Health Overview', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.person_outline_rounded), 
                    onPressed: () { 
                      UxUtils.hapticLight(); 
                      Navigator.of(context).push(MaterialPageRoute(builder: (_) => const PatientProfileScreen()));
                    }
                  ),
                  IconButton(
                    icon: const Icon(Icons.notifications_outlined), 
                    onPressed: () { UxUtils.hapticLight(); UxUtils.showToast(context, 'No new notifications'); }
                  ),
                  IconButton(
                    icon: const Icon(Icons.logout_rounded),
                    onPressed: () { UxUtils.hapticMedium(); context.read<UserProvider>().logout(); }
                  )
                ],
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome back,',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: MedRagTheme.primaryCyan, fontWeight: FontWeight.w600),
                      ).animate().fadeIn(duration: 400.ms).slideY(begin: -0.2, end: 0),
                      const SizedBox(height: 4),
                      isLoading
                          ? Padding(padding: const EdgeInsets.symmetric(vertical: 8), child: UxUtils.loadingSkeleton(width: 200, height: 36, borderRadius: 8))
                          : Text(loggedInName, style: Theme.of(context).textTheme.displayLarge?.copyWith(color: Colors.white)).animate().fadeIn(duration: 500.ms).slideX(begin: -0.1, end: 0),
                      const SizedBox(height: 32),
                      
                      isLoading
                          ? UxUtils.loadingSkeleton(height: 120)
                          : RiskScoreWidget(score: riskScore, level: riskLevel).animate().shimmer(duration: 1.seconds, color: Colors.white12).fadeIn(duration: 500.ms),
                      
                      const SizedBox(height: 28),

                      // Quick Action Cards
                      Text('Quick Actions', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold))
                        .animate().fadeIn(delay: 150.ms),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(child: _buildQuickAction(context, 'Run\nDiagnosis', Icons.psychology_rounded, MedRagTheme.primaryCyan, 1)),
                          const SizedBox(width: 12),
                          Expanded(child: _buildQuickAction(context, 'Appointments', Icons.calendar_month_rounded, MedRagTheme.secondaryCoral, null, customScreen: const AppointmentBookingScreen())),
                          const SizedBox(width: 12),
                          Expanded(child: _buildQuickAction(context, 'Track\nHealth', Icons.query_stats_rounded, const Color(0xFF34D399), 4)),
                        ],
                      ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.2, end: 0),

                      const SizedBox(height: 32),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Your Diagnoses', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                          TextButton(
                            onPressed: () {
                              UxUtils.hapticLight();
                              MainNavigation.navKey.currentState?.switchTab(3);
                            }, 
                            child: const Text('View All')
                          ),
                        ],
                      ).animate().fadeIn(delay: 200.ms).slideY(begin: 0.2, end: 0),
                      const SizedBox(height: 16),
                    ],
                  ),
                ),
              ),
              if (isLoading)
                 SliverList(
                   delegate: SliverChildBuilderDelegate(
                     (context, index) => Padding(
                       padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
                       child: UxUtils.loadingSkeleton(height: 80),
                     ),
                     childCount: 3,
                   ),
                 )
              else if (reports.isEmpty)
                 SliverToBoxAdapter(
                   child: Padding(
                     padding: const EdgeInsets.symmetric(horizontal: 20),
                     child: UxUtils.emptyState(
                       'No Reports Found', 
                       'There are no recent diagnostic reports in your history.',
                       icon: Icons.description_outlined
                     ).animate().fadeIn().scale(begin: const Offset(0.9, 0.9)),
                   ),
                 )
              else
                 SliverPadding(
                   padding: const EdgeInsets.symmetric(horizontal: 20),
                   sliver: SliverList(
                     delegate: SliverChildBuilderDelegate(
                       (context, index) {
                         if (index >= 3) return null; // Show max 3 for dashboard
                         final report = reports[index];
                         return Padding(
                           padding: const EdgeInsets.only(bottom: 12.0),
                           child: ReportCard(
                              report: report,
                              onTap: () {
                                UxUtils.hapticMedium();
                                provider.setLatestReport(report);
                                MainNavigation.navKey.currentState?.switchTab(3);
                              },
                           ),
                         ).animate().fadeIn(delay: (200 + index * 100).ms, duration: 400.ms).slideY(begin: 0.1, end: 0, curve: Curves.easeOut);
                       },
                       childCount: reports.length > 3 ? 3 : reports.length,
                     ),
                   ),
                 ),
                 
              const SliverPadding(padding: EdgeInsets.only(bottom: 120)),
            ],
          ),
        );
      }
    );
  }

  Widget _buildQuickAction(BuildContext context, String label, IconData icon, Color color, int? tabIndex, {Widget? customScreen}) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          UxUtils.hapticLight();
          if (customScreen != null) {
            Navigator.of(context).push(MaterialPageRoute(builder: (_) => customScreen));
          } else if (tabIndex != null) {
            MainNavigation.navKey.currentState?.switchTab(tabIndex);
          }
        },
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 12),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: color.withValues(alpha: 0.2)),
          ),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 22),
              ),
              const SizedBox(height: 10),
              Text(
                label,
                textAlign: TextAlign.center,
                style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600, height: 1.3),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
