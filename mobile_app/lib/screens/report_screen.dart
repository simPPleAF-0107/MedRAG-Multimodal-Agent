import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/report_provider.dart';

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
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.search_off, size: 64, color: Colors.grey.shade400),
                  const SizedBox(height: 16),
                  Text('No Active Report', style: TextStyle(fontSize: 18, color: Colors.grey.shade600)),
                ],
              ),
            ),
          );
        }

        final confidence = (report['confidence_calibration']?['overall_confidence'] ?? 0).toDouble();
        final finalReportText = report['final_report'] ?? report['diagnosis_reasoning'] ?? 'No synthesis available.';
        final evidence = report['retrieved_context_used'] ?? 'No vector context returned.';

        return Scaffold(
          appBar: AppBar(title: const Text('Diagnostic Inference Report')),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Confidence Module
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: confidence > 70 ? Colors.green.shade50 : Colors.orange.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: confidence > 70 ? Colors.green.shade200 : Colors.orange.shade200),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Engine Confidence', style: TextStyle(fontWeight: FontWeight.bold)),
                      Text(
                        '${confidence.toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: confidence > 70 ? Colors.green.shade700 : Colors.orange.shade700,
                        ),
                      )
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Synthesis
                const Text('Synthesized Clinical Evaluation', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(finalReportText, style: const TextStyle(fontSize: 15, height: 1.5)),
                ),
                const SizedBox(height: 24),

                // Evidence Context
                const Text('Cited Evidence Sources', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    evidence, 
                    style: TextStyle(fontFamily: 'monospace', fontSize: 12, color: Colors.grey.shade800)
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
