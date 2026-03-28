import 'dart:ui';
import 'package:flutter/material.dart';
import '../utils/theme.dart';

class RiskScoreWidget extends StatelessWidget {
  final int score;
  final String level;

  const RiskScoreWidget({super.key, required this.score, required this.level});

  Color _getColor() {
    if (score < 40) return MedRagTheme.primaryCyan; // Success Green / Cyan
    if (score < 70) return const Color(0xFFF59E0B); // Warning Orange
    return MedRagTheme.secondaryCoral; // Error Red / Coral
  }

  @override
  Widget build(BuildContext context) {
    final color = _getColor();
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
      decoration: BoxDecoration(
        color: MedRagTheme.surfaceDark.withOpacity(0.7),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.5), width: 1.5),
         boxShadow: [
           BoxShadow(
             color: color.withOpacity(0.15),
             blurRadius: 15,
             offset: const Offset(0, 0),
           )
         ]
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Clinical Risk Profile',
                    style: TextStyle(
                      color: MedRagTheme.textMuted,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.5,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    level.toUpperCase(),
                    style: TextStyle(
                      color: color,
                      fontSize: 24,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.5,
                    ),
                  ),
                ],
              ),
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: MedRagTheme.backgroundDark.withOpacity(0.8),
                  border: Border.all(color: color, width: 2),
                  boxShadow: [BoxShadow(color: color.withOpacity(0.5), blurRadius: 10)],
                ),
                child: Center(
                  child: Text(
                    score.toString(),
                    style: TextStyle(
                      color: color,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
