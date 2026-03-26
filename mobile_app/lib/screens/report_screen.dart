import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/report_provider.dart';
import '../utils/ux_utils.dart';

class ReportScreen extends StatelessWidget {
  const ReportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ReportProvider>(
      builder: (context, provider, child) {
        final report = provider.latestReport;

        if (report == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('Diagnostic Inference Report')),
            body: UxUtils.emptyState(
              'No Active Report',
              'Select a report from the Dashboard or run the Pipeline to view synthesis here.',
              icon: Icons.search_off_rounded,
            ),
          );
        }

        final confidence = (report['confidence_calibration']?['overall_confidence'] ?? 0).toDouble();
        final finalReportText = report['final_report'] ?? report['diagnosis_reasoning'] ?? 'No synthesis available.';
        final evidence = report['retrieved_context_used'] ?? 'No vector context returned.';

        return Scaffold(
          appBar: AppBar(title: const Text('Diagnostic Inference Report')),
          body: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Confidence Module
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: confidence > 70 ? const Color(0xFF10B981).withOpacity(0.05) : const Color(0xFFF59E0B).withOpacity(0.05),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: confidence > 70 ? const Color(0xFF10B981).withOpacity(0.3) : const Color(0xFFF59E0B).withOpacity(0.3),
                      width: 1.5
                    ),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Engine Confidence', style: Theme.of(context).textTheme.titleMedium),
                      Text(
                        '${confidence.toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.5,
                          color: confidence > 70 ? const Color(0xFF047857) : const Color(0xFFB45309),
                        ),
                      )
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // Synthesis
                Text('Synthesized Clinical Evaluation', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardTheme.color,
                    border: Border.all(color: Colors.grey.shade200),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.02),
                        blurRadius: 10,
                        offset: const Offset(0, 4)
                      )
                    ]
                  ),
                  child: Text(finalReportText, style: Theme.of(context).textTheme.bodyLarge),
                ),
                const SizedBox(height: 32),

                // Evidence Context
                Text('Cited Evidence Sources', style: Theme.of(context).textTheme.titleLarge),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: Text(
                    evidence, 
                    style: TextStyle(fontFamily: 'monospace', fontSize: 13, color: Colors.grey.shade700, height: 1.5)
                  ),
                )
              ],
            ),
          ),
        );
      },
    );
  }
}
