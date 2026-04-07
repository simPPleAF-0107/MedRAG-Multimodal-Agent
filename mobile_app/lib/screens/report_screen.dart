import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../providers/report_provider.dart';
import '../utils/ux_utils.dart';
import '../utils/theme.dart';

class ReportScreen extends StatelessWidget {
  const ReportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<ReportProvider>(
      builder: (context, provider, child) {
        final report = provider.latestReport;
        final allReports = (provider.patientHistory?['reports'] as List?) ?? [];

        return Scaffold(
          appBar: AppBar(title: const Text('Diagnostic Inference Report')),
          body: report == null && allReports.isEmpty
              ? UxUtils.emptyState(
                  'No Active Report',
                  'Select a report from the Dashboard or run the Pipeline to view synthesis here.',
                  icon: Icons.search_off_rounded,
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Active Report Detail
                      if (report != null) ...[
                        _buildActiveReport(context, report),
                        const SizedBox(height: 32),
                      ],

                      // All Reports History
                      if (allReports.isNotEmpty) ...[
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              report != null ? 'Report History' : 'All Reports',
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            Text(
                              '${allReports.length} total',
                              style: TextStyle(color: MedRagTheme.textMuted, fontSize: 13),
                            ),
                          ],
                        ).animate().fadeIn(delay: 200.ms),
                        const SizedBox(height: 16),
                        ...allReports.asMap().entries.map((entry) {
                          final idx = entry.key;
                          final r = entry.value as Map<String, dynamic>;
                          final isActive = report != null && r == report;
                          return _buildReportListItem(context, r, provider, isActive, idx);
                        }),
                      ],

                      // Bottom padding for floating nav
                      const SizedBox(height: 100),
                    ],
                  ),
                ),
        );
      },
    );
  }

  Widget _buildActiveReport(BuildContext context, Map<String, dynamic> report) {
    // Backend returns confidence_score as 0.0-1.0 float; convert to percentage
    final rawConf = report['confidence_score'] ?? report['confidence_calibration']?['overall_confidence'] ?? 0;
    final confidence = (rawConf is double && rawConf <= 1.0)
        ? rawConf * 100
        : (rawConf as num).toDouble();
    final finalReportText = report['final_report'] ?? report['diagnosis'] ?? report['diagnosis_reasoning'] ?? 'No synthesis available.';
    final evidence = report['retrieved_context_used'] ?? report['evidence'] ?? 'No vector context returned.';
    final isHighConf = confidence > 70;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Confidence Module
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: isHighConf ? const Color(0xFF10B981).withValues(alpha: 0.08) : const Color(0xFFF59E0B).withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: isHighConf ? const Color(0xFF10B981).withValues(alpha: 0.3) : const Color(0xFFF59E0B).withValues(alpha: 0.3),
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
                  color: isHighConf ? const Color(0xFF34D399) : const Color(0xFFFBBF24),
                ),
              )
            ],
          ),
        ).animate().fadeIn().slideY(begin: 0.1, end: 0),
        const SizedBox(height: 24),

        // Synthesis
        Text('Synthesized Clinical Evaluation', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Theme.of(context).cardTheme.color,
            border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.1),
                blurRadius: 10,
                offset: const Offset(0, 4)
              )
            ]
          ),
          child: Text(finalReportText, style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.6)),
        ).animate().fadeIn(delay: 100.ms),
        const SizedBox(height: 24),

        // Evidence Context
        Text('Cited Evidence Sources', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
          ),
          child: Text(
            evidence, 
            style: TextStyle(fontFamily: 'monospace', fontSize: 13, color: Colors.white.withValues(alpha: 0.6), height: 1.5)
          ),
        ).animate().fadeIn(delay: 200.ms),
      ],
    );
  }

  Widget _buildReportListItem(BuildContext context, Map<String, dynamic> r, ReportProvider provider, bool isActive, int index) {
    final rawConf = r['confidence_score'] ?? r['confidence_calibration']?['overall_confidence'] ?? 0;
    final confidence = (rawConf is double && rawConf <= 1.0)
        ? rawConf * 100
        : (rawConf as num).toDouble();
    final summary = r['final_report'] ?? r['diagnosis'] ?? r['diagnosis_reasoning'] ?? 'Pending...';
    final title = r['title'] ?? r['chief_complaint'] ?? 'Report ${index + 1}';
    final date = r['date'] ?? r['created_at'] ?? 'Unknown date';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            UxUtils.hapticLight();
            provider.setLatestReport(r);
          },
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isActive ? MedRagTheme.primaryCyan.withValues(alpha: 0.08) : Colors.white.withValues(alpha: 0.03),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isActive ? MedRagTheme.primaryCyan.withValues(alpha: 0.4) : Colors.white.withValues(alpha: 0.08),
                width: isActive ? 1.5 : 1,
              ),
            ),
            child: Row(
              children: [
                // Left icon
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    isActive ? Icons.description_rounded : Icons.description_outlined,
                    color: isActive ? MedRagTheme.primaryCyan : MedRagTheme.textMuted,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 14),
                // Content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: isActive ? MedRagTheme.primaryCyan : Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        summary,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(color: MedRagTheme.textMuted, fontSize: 12),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        date,
                        style: TextStyle(color: MedRagTheme.textMuted.withValues(alpha: 0.6), fontSize: 11),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                // Confidence badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: confidence > 70 ? const Color(0xFF34D399).withValues(alpha: 0.1) : const Color(0xFFFBBF24).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${confidence.toStringAsFixed(0)}%',
                    style: TextStyle(
                      color: confidence > 70 ? const Color(0xFF34D399) : const Color(0xFFFBBF24),
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    ).animate().fadeIn(delay: (100 * index).ms, duration: 300.ms).slideX(begin: 0.05, end: 0);
  }
}
