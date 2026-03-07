import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/report_provider.dart';
import '../widgets/risk_score_widget.dart';
import '../widgets/report_card.dart';

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
    return Consumer<ReportProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading && provider.patientHistory == null) {
          return const Center(child: CircularProgressIndicator());
        }

        final data = provider.patientHistory;
        final name = data != null ? '${data['first_name']} ${data['last_name']}' : 'Patient';
        final reports = (data?['reports'] as List?) ?? [];

        return Scaffold(
          appBar: AppBar(
            title: const Text('Patient Overview'),
            actions: [
              IconButton(icon: const Icon(Icons.notifications_none), onPressed: () {})
            ],
          ),
          body: RefreshIndicator(
            onRefresh: () => provider.loadPatientHistory("1"),
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text(
                  'Welcome, Dr. Smith',
                  style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
                ),
                Text(
                  'Viewing $name',
                  style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                
                // Risk Score Module
                const RiskScoreWidget(score: 68, level: "High"), // Hardcoded prototype risk score
                
                const SizedBox(height: 32),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Recent Diagnoses',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    TextButton(
                      onPressed: () {}, 
                      child: const Text('View All')
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                
                // Reports List
                if (reports.isEmpty)
                   Container(
                     padding: const EdgeInsets.all(24),
                     alignment: Alignment.center,
                     color: Colors.grey.shade100,
                     child: const Text('No recent reports available.', style: TextStyle(color: Colors.grey)),
                   )
                else
                   ...reports.take(3).map((report) => ReportCard(
                     report: report,
                     onTap: () {
                        // Normally this would navigate to a specific report detail view, 
                        // but per requirements we just send them to the general Reports tab
                        provider.setLatestReport(report);
                        ScaffoldMessenger.of(context).showSnackBar(
                           const SnackBar(content: Text('Report locked. Open Reports tab.'))
                        );
                     },
                   ))
              ],
            ),
          ),
        );
      }
    );
  }
}
