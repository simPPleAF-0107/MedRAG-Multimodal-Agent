import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../providers/report_provider.dart';
import '../providers/user_provider.dart';
import '../widgets/risk_score_widget.dart';
import '../widgets/report_card.dart';
import '../utils/ux_utils.dart';
import '../utils/theme.dart';

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
    String userEmail = context.watch<UserProvider>().email ?? 'Unknown User';

    return Scaffold(
      body: isDoctor ? _buildDoctorDashboard(userEmail) : _buildPatientDashboard(),
    );
  }

  Widget _buildDoctorDashboard(String email) {
    final List<Map<String, dynamic>> mockPatients = [
      {'name': 'John Doe', 'risk': 'High', 'score': 84, 'last_visit': '2 days ago'},
      {'name': 'Jane Smith', 'risk': 'Moderate', 'score': 52, 'last_visit': '1 week ago'},
      {'name': 'Bob User', 'risk': 'Low', 'score': 12, 'last_visit': '1 month ago'},
      {'name': 'Alice Wong', 'risk': 'Low', 'score': 8, 'last_visit': '3 months ago'},
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
                  colors: [MedRagTheme.backgroundDark, MedRagTheme.primaryCyan.withOpacity(0.1)],
                )
              ),
              child: Stack(
                children: [
                   Positioned(
                     right: -50, top: -50,
                     child: Container(
                       width: 200, height: 200,
                       decoration: BoxDecoration(shape: BoxShape.circle, color: MedRagTheme.primaryCyan.withOpacity(0.05)),
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
                Text('Welcome, Provider', style: Theme.of(context).textTheme.displayMedium),
                const SizedBox(height: 8),
                Text(email, style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Theme.of(context).primaryColor)),
                const SizedBox(height: 32),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Your Patients', style: Theme.of(context).textTheme.titleLarge),
                    Text('${mockPatients.length} Total', style: TextStyle(color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5))),
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
                        color: MedRagTheme.primaryCyan.withOpacity(0.1),
                        shape: BoxShape.circle,
                        border: Border.all(color: MedRagTheme.primaryCyan.withOpacity(0.3)),
                      ),
                      child: Text(p['name'][0], style: const TextStyle(color: MedRagTheme.primaryCyan, fontWeight: FontWeight.bold, fontSize: 18)),
                    ),
                    title: Text(p['name'], style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white, fontWeight: FontWeight.bold)),
                    subtitle: Text('Last Visit: ${p['last_visit']}', style: TextStyle(color: MedRagTheme.textMuted)),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text('Score: ${p['score']}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 16)),
                        Text('${p['risk']}', style: TextStyle(
                          color: p['risk'] == 'High' ? Colors.redAccent 
                               : p['risk'] == 'Moderate' ? Colors.orangeAccent 
                               : Colors.greenAccent,
                          fontWeight: FontWeight.bold,
                          fontSize: 12
                        )),
                      ],
                    ),
                    onTap: () {
                      UxUtils.hapticLight();
                      UxUtils.showToast(context, 'Mock: Opening record for ${p['name']}');
                    },
                  ),
                ).animate().fadeIn(delay: (100 * index).ms, duration: 400.ms).slideX(begin: 0.1, end: 0, curve: Curves.easeOut);
              },
              childCount: mockPatients.length,
            ),
          ),
        ),
        const SliverPadding(padding: EdgeInsets.only(bottom: 100)),
      ],
    );
  }

  Widget _buildPatientDashboard() {
    return Consumer<ReportProvider>(
      builder: (context, provider, child) {
        final isLoading = provider.isLoading && provider.patientHistory == null;
        final data = provider.patientHistory;
        final name = data != null ? '${data['first_name']}' : 'Patient';
        final reports = (data?['reports'] as List?) ?? [];

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
                backgroundColor: MedRagTheme.backgroundDark.withOpacity(0.9),
                title: Text('Health Overview', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
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
                          : Text(name, style: Theme.of(context).textTheme.displayLarge?.copyWith(color: Colors.white)).animate().fadeIn(duration: 500.ms).slideX(begin: -0.1, end: 0),
                      const SizedBox(height: 32),
                      
                      isLoading
                          ? UxUtils.loadingSkeleton(height: 120)
                          : const RiskScoreWidget(score: 12, level: "Low").animate().shimmer(duration: 1.seconds, color: Colors.white12).fadeIn(duration: 500.ms),
                      
                      const SizedBox(height: 32),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Your Diagnoses', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                          TextButton(
                            onPressed: () { UxUtils.hapticLight(); }, 
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
                                UxUtils.showToast(context, 'Report locked. Open Reports tab.');
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
}
