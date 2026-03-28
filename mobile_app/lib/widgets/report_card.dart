import 'dart:ui';
import 'package:flutter/material.dart';
import '../utils/theme.dart';

class ReportCard extends StatelessWidget {
  final Map<String, dynamic> report;
  final VoidCallback onTap;

  const ReportCard({super.key, required this.report, required this.onTap});

  @override
  Widget build(BuildContext context) {
    String summary = report['final_report'] ?? report['diagnosis_reasoning'] ?? "Pending synthesis...";
    double confidence = (report['confidence_calibration']?['overall_confidence'] ?? 0).toDouble();

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(20),
          decoration: MedRagTheme.glassDecoration,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Icon(Icons.description_rounded, color: MedRagTheme.primaryCyan, size: 22),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: confidence > 70 ? MedRagTheme.primaryCyan.withOpacity(0.1) : MedRagTheme.secondaryCoral.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: confidence > 70 ? MedRagTheme.primaryCyan.withOpacity(0.3) : MedRagTheme.secondaryCoral.withOpacity(0.3)),
                    ),
                    child: Text(
                      '${confidence.toStringAsFixed(1)}% Confidence',
                      style: TextStyle(
                        color: confidence > 70 ? MedRagTheme.primaryCyan : MedRagTheme.secondaryCoral,
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  )
                ],
              ),
              const SizedBox(height: 16),
              Text(
                summary,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.white,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.access_time, size: 14, color: MedRagTheme.textMuted),
                  const SizedBox(width: 4),
                  Text(
                    'Generated Today', // Future timestamp binding
                    style: TextStyle(fontSize: 12, color: MedRagTheme.textMuted),
                  )
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}
