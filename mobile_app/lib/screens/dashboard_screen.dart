import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/report_provider.dart';
import '../providers/user_provider.dart';
import '../widgets/risk_score_widget.dart';
import '../widgets/report_card.dart';
import '../utils/ux_utils.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  
  @override
  void initState() {
    super.initState();
    // Fetch initial state if empty. Using hardcoded patient '1' for prototype.
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
      appBar: AppBar(
        title: Text(isDoctor ? 'Clinical Command Center' : 'Patient Overview'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined), 
            onPressed: () {
              UxUtils.hapticLight();
              UxUtils.showToast(context, 'No new notifications');
            }
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            onPressed: () {
              UxUtils.hapticMedium();
              context.read<UserProvider>().logout();
            },
          )
        ],
      ),
      body: isDoctor ? _buildDoctorDashboard(userEmail) : _buildPatientDashboard(),
    );
  }

  Widget _buildDoctorDashboard(String email) {
    // Mock patient list for doctors
    final List<Map<String, dynamic>> mockPatients = [
      {'name': 'John Doe', 'risk': 'High', 'score': 84, 'last_visit': '2 days ago'},
      {'name': 'Jane Smith', 'risk': 'Moderate', 'score': 52, 'last_visit': '1 week ago'},
      {'name': 'Bob User', 'risk': 'Low', 'score': 12, 'last_visit': '1 month ago'},
      {'name': 'Alice Wong', 'risk': 'Low', 'score': 8, 'last_visit': '3 months ago'},
    ];

    return ListView(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      children: [
        Text(
          'Welcome, Provider',
          style: Theme.of(context).textTheme.displayMedium,
        ),
        const SizedBox(height: 8),
        Text(
          email,
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Theme.of(context).primaryColor,
          ),
        ),
        const SizedBox(height: 32),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Your Patients', style: Theme.of(context).textTheme.titleLarge),
            Text('${mockPatients.length} Total', style: TextStyle(color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5))),
          ],
        ),
        const SizedBox(height: 16),
        ...mockPatients.map((p) => Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            leading: CircleAvatar(
              backgroundColor: Theme.of(context).primaryColor.withOpacity(0.2),
              child: Text(p['name'][0], style: TextStyle(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold)),
            ),
            title: Text(p['name'], style: Theme.of(context).textTheme.titleMedium),
            subtitle: Text('Last Visit: ${p['last_visit']}'),
            trailing: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('Risk: ${p['score']}', style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: p['risk'] == 'High' ? Colors.redAccent 
                       : p['risk'] == 'Moderate' ? Colors.orangeAccent 
                       : Colors.greenAccent
                )),
              ],
            ),
            onTap: () {
              UxUtils.hapticLight();
              UxUtils.showToast(context, 'Mock: Opening specialized record for ${p['name']}...');
            },
          ),
        )),
      ],
    );
  }

  Widget _buildPatientDashboard() {
    return Consumer<ReportProvider>(
      builder: (context, provider, child) {
        final isLoading = provider.isLoading && provider.patientHistory == null;
        final data = provider.patientHistory;
        final name = data != null ? '${data['first_name']} ${data['last_name']}' : 'Patient';
        final reports = (data?['reports'] as List?) ?? [];

        return RefreshIndicator(
          onRefresh: () async {
            UxUtils.hapticLight();
            await provider.loadPatientHistory(context.read<UserProvider>().userId ?? "1");
          },
          color: Theme.of(context).primaryColor,
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
            physics: const AlwaysScrollableScrollPhysics(),
            children: [
              Text(
                'Welcome back,',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 4),
              isLoading
                  ? Padding(
                      padding: const EdgeInsets.only(top: 8, bottom: 8),
                      child: UxUtils.loadingSkeleton(width: 200, height: 32, borderRadius: 8),
                    )
                  : Text(
                      name,
                      style: Theme.of(context).textTheme.displayMedium,
                    ),
              const SizedBox(height: 32),
              
              // Risk Score Module
              isLoading
                  ? UxUtils.loadingSkeleton(height: 120)
                  : const RiskScoreWidget(score: 12, level: "Low"), // Update mock score to reflect typical patient
              
              const SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Your Diagnoses',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  TextButton(
                    onPressed: () {
                      UxUtils.hapticLight();
                    }, 
                    child: const Text('View All')
                  ),
                ],
              ),
              const SizedBox(height: 16),
              
              // Reports List
              if (isLoading)
                 Column(
                   children: List.generate(3, (index) => Padding(
                     padding: const EdgeInsets.only(bottom: 12.0),
                     child: UxUtils.loadingSkeleton(height: 80),
                   )),
                 )
              else if (reports.isEmpty)
                 UxUtils.emptyState(
                   'No Reports Found', 
                   'There are no recent diagnostic reports in your history.',
                   icon: Icons.description_outlined
                 )
              else
                 ...reports.take(3).map((report) => Padding(
                   padding: const EdgeInsets.only(bottom: 12.0),
                   child: ReportCard(
                      report: report,
                      onTap: () {
                        UxUtils.hapticMedium();
                        provider.setLatestReport(report);
                        UxUtils.showToast(context, 'Report locked. Open Reports tab.');
                      },
                   ),
                 ))
            ],
          ),
        );
      }
    );
  }
}
