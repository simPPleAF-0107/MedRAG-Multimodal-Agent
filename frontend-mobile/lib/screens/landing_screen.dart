import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../utils/theme.dart';
import 'login_screen.dart';

class LandingScreen extends StatelessWidget {
  const LandingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFF04060C),
      body: Stack(
        children: [
          // ── Ambient background orbs ──
          Positioned(
            top: size.height * 0.15,
            left: -80,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: MedRagTheme.primaryCyan.withValues(alpha: 0.08),
              ),
            )
                .animate(onPlay: (c) => c.repeat(reverse: true))
                .moveX(end: 60, duration: 6.seconds)
                .moveY(end: 30, duration: 8.seconds),
          ),
          Positioned(
            bottom: size.height * 0.1,
            right: -100,
            child: Container(
              width: 400,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF3B82F6).withValues(alpha: 0.06),
              ),
            )
                .animate(onPlay: (c) => c.repeat(reverse: true))
                .moveY(end: 80, duration: 7.seconds),
          ),

          // ── Main scrollable content ──
          SafeArea(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 28),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(height: 60),

                    // ── Logo ──
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(24),
                        gradient: const LinearGradient(
                          colors: [Color(0xFF00D4FF), Color(0xFF3B82F6)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color:
                                MedRagTheme.primaryCyan.withValues(alpha: 0.25),
                            blurRadius: 30,
                            spreadRadius: 4,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.monitor_heart_rounded,
                        size: 48,
                        color: Colors.white,
                      ),
                    )
                        .animate()
                        .scale(
                          begin: const Offset(0.5, 0.5),
                          end: const Offset(1.0, 1.0),
                          duration: 800.ms,
                          curve: Curves.elasticOut,
                        )
                        .fadeIn(duration: 600.ms),

                    const SizedBox(height: 32),

                    // ── Trust Badge ──
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 8),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(20),
                        color: Colors.white.withValues(alpha: 0.04),
                        border: Border.all(
                            color: Colors.white.withValues(alpha: 0.08)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.auto_awesome,
                            size: 14,
                            color: MedRagTheme.primaryCyan,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'BUILT FOR CLINICIANS',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w800,
                              letterSpacing: 2,
                              color: MedRagTheme.primaryCyan,
                            ),
                          ),
                        ],
                      ),
                    )
                        .animate()
                        .fadeIn(delay: 300.ms)
                        .slideY(begin: 0.2, end: 0),

                    const SizedBox(height: 28),

                    // ── Headline ──
                    RichText(
                      textAlign: TextAlign.center,
                      text: TextSpan(
                        style: const TextStyle(
                          fontSize: 38,
                          fontWeight: FontWeight.w900,
                          height: 1.1,
                          letterSpacing: -1.5,
                          color: Colors.white,
                        ),
                        children: [
                          const TextSpan(text: 'Your AI Medical\n'),
                          TextSpan(
                            text: 'Intelligence ',
                            style: TextStyle(
                              foreground: Paint()
                                ..shader = const LinearGradient(
                                  colors: [
                                    Color(0xFF00D4FF),
                                    Color(0xFF3B82F6),
                                    Color(0xFF6366F1)
                                  ],
                                ).createShader(
                                    const Rect.fromLTWH(0, 0, 280, 50)),
                            ),
                          ),
                          const TextSpan(text: 'System.'),
                        ],
                      ),
                    )
                        .animate()
                        .fadeIn(delay: 400.ms, duration: 600.ms)
                        .slideY(begin: 0.15, end: 0),

                    const SizedBox(height: 20),

                    // ── Subheading ──
                    Text(
                      'MedRAG combines advanced retrieval, multimodal AI, and clinical reasoning for faster, safer medical insights.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 15,
                        height: 1.6,
                        fontWeight: FontWeight.w500,
                        color: Colors.white.withValues(alpha: 0.45),
                      ),
                    ).animate().fadeIn(delay: 500.ms),

                    const SizedBox(height: 12),

                    Text(
                      'Instant. Reliable. Multimodal.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                        color: MedRagTheme.primaryCyan.withValues(alpha: 0.6),
                      ),
                    ).animate().fadeIn(delay: 600.ms),

                    const SizedBox(height: 40),

                    // ── CTA Buttons ──
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: () => _navigateToLogin(context),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(18)),
                          padding: EdgeInsets.zero,
                        ),
                        child: Ink(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(18),
                            gradient: const LinearGradient(
                              colors: [Color(0xFF00D4FF), Color(0xFF3B82F6)],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: MedRagTheme.primaryCyan
                                    .withValues(alpha: 0.3),
                                blurRadius: 20,
                                spreadRadius: 2,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: Container(
                            alignment: Alignment.center,
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  'Get Started',
                                  style: TextStyle(
                                    fontSize: 17,
                                    fontWeight: FontWeight.w800,
                                    color: Color(0xFF04060C),
                                    letterSpacing: 0.5,
                                  ),
                                ),
                                SizedBox(width: 8),
                                Icon(Icons.arrow_forward_rounded,
                                    color: Color(0xFF04060C), size: 20),
                              ],
                            ),
                          ),
                        ),
                      ),
                    )
                        .animate()
                        .fadeIn(delay: 700.ms)
                        .slideY(begin: 0.2, end: 0),

                    const SizedBox(height: 16),

                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: OutlinedButton(
                        onPressed: () {},
                        style: OutlinedButton.styleFrom(
                          side: BorderSide(
                              color: Colors.white.withValues(alpha: 0.1)),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(18)),
                        ),
                        child: Text(
                          'View Demo',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            color: Colors.white.withValues(alpha: 0.7),
                          ),
                        ),
                      ),
                    ).animate().fadeIn(delay: 800.ms),

                    const SizedBox(height: 48),

                    // ── Trust Badges Row ──
                    Wrap(
                      spacing: 24,
                      runSpacing: 12,
                      alignment: WrapAlignment.center,
                      children: [
                        _trustBadge(Icons.shield_outlined, 'HIPAA Aligned'),
                        _trustBadge(Icons.lock_outline, 'Encrypted'),
                        _trustBadge(Icons.bolt, 'Real-Time'),
                        _trustBadge(Icons.psychology_outlined, '34K+ Nodes'),
                      ],
                    ).animate().fadeIn(delay: 900.ms),

                    const SizedBox(height: 56),

                    // ── Feature Cards ──
                    _sectionHeader(
                        'FEATURES', 'From Symptoms to\nMedical Insight'),

                    const SizedBox(height: 24),

                    _featureCard(
                      Icons.text_snippet_outlined,
                      'Text Analysis',
                      'Symptoms, clinical notes — parsed against 34K+ knowledge nodes.',
                    ),
                    const SizedBox(height: 12),
                    _featureCard(
                      Icons.image_outlined,
                      'Medical Imaging',
                      'X-rays, CT scans processed through multimodal CLIP embeddings.',
                    ),
                    const SizedBox(height: 12),
                    _featureCard(
                      Icons.mic_outlined,
                      'Voice Input',
                      'Patient descriptions via audio, transcribed into the pipeline.',
                    ),

                    const SizedBox(height: 56),

                    // ── How It Works ──
                    _sectionHeader('PIPELINE', 'How It Works'),
                    const SizedBox(height: 24),

                    Row(
                      children: [
                        _stepCircle('01', 'Input'),
                        const Expanded(
                            child:
                                Divider(color: Colors.white10, thickness: 1)),
                        _stepCircle('02', 'AI'),
                        const Expanded(
                            child:
                                Divider(color: Colors.white10, thickness: 1)),
                        _stepCircle('03', 'Safety'),
                        const Expanded(
                            child:
                                Divider(color: Colors.white10, thickness: 1)),
                        _stepCircle('04', 'Output'),
                      ],
                    ),

                    const SizedBox(height: 56),

                    // ── Security ──
                    _sectionHeader('SECURITY', 'Your Data. Protected.'),
                    const SizedBox(height: 24),

                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      alignment: WrapAlignment.center,
                      children: [
                        _securityBadge(Icons.lock, 'End-to-End Secure'),
                        _securityBadge(Icons.verified_user, 'JWT Auth'),
                        _securityBadge(Icons.visibility_off, 'No AI Exposure'),
                        _securityBadge(
                            Icons.admin_panel_settings, 'Privacy-First'),
                      ],
                    ),

                    const SizedBox(height: 56),

                    // ── Final CTA ──
                    Icon(Icons.auto_awesome,
                        color: MedRagTheme.primaryCyan, size: 28),
                    const SizedBox(height: 16),
                    const Text(
                      'Start Your AI-Powered\nMedical Experience',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.w900,
                        height: 1.15,
                        letterSpacing: -0.5,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 20),

                    SizedBox(
                      width: double.infinity,
                      height: 54,
                      child: ElevatedButton(
                        onPressed: () => _navigateToLogin(context),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: MedRagTheme.primaryCyan,
                          foregroundColor: const Color(0xFF04060C),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16)),
                        ),
                        child: const Text('Login',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w800)),
                      ),
                    ),

                    const SizedBox(height: 40),

                    // ── Footer ──
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(10),
                            gradient: const LinearGradient(
                              colors: [Color(0xFF00D4FF), Color(0xFF3B82F6)],
                            ),
                          ),
                          child: const Icon(Icons.monitor_heart_rounded,
                              size: 16, color: Colors.white),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          'MedRAG',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w800,
                            color: Colors.white.withValues(alpha: 0.6),
                            letterSpacing: 1,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '© 2026',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.white.withValues(alpha: 0.25),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _navigateToLogin(BuildContext context) {
    Navigator.of(context).push(
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) =>
            const LoginScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(opacity: animation, child: child);
        },
        transitionDuration: const Duration(milliseconds: 400),
      ),
    );
  }

  Widget _trustBadge(IconData icon, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon,
            size: 14, color: MedRagTheme.primaryCyan.withValues(alpha: 0.5)),
        const SizedBox(width: 6),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.w700,
            letterSpacing: 1.5,
            color: Colors.white.withValues(alpha: 0.35),
          ),
        ),
      ],
    );
  }

  Widget _sectionHeader(String label, String title) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w800,
            letterSpacing: 3,
            color: MedRagTheme.primaryCyan,
          ),
        ),
        const SizedBox(height: 10),
        Text(
          title,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.w900,
            height: 1.15,
            letterSpacing: -0.5,
            color: Colors.white,
          ),
        ),
      ],
    );
  }

  Widget _featureCard(IconData icon, String title, String desc) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: Colors.white.withValues(alpha: 0.03),
        border: Border.all(color: Colors.white.withValues(alpha: 0.06)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
              border: Border.all(
                  color: MedRagTheme.primaryCyan.withValues(alpha: 0.2)),
            ),
            child: Icon(icon, size: 24, color: MedRagTheme.primaryCyan),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Colors.white)),
                const SizedBox(height: 4),
                Text(
                  desc,
                  style: TextStyle(
                      fontSize: 13,
                      height: 1.4,
                      color: Colors.white.withValues(alpha: 0.4)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _stepCircle(String num, String label) {
    return Column(
      children: [
        Container(
          width: 52,
          height: 52,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
            border: Border.all(
                color: MedRagTheme.primaryCyan.withValues(alpha: 0.2)),
          ),
          child: Center(
            child: Text(
              num,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w800,
                color: MedRagTheme.primaryCyan,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: Colors.white.withValues(alpha: 0.5),
          ),
        ),
      ],
    );
  }

  Widget _securityBadge(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        color: Colors.white.withValues(alpha: 0.02),
        border: Border.all(color: Colors.white.withValues(alpha: 0.05)),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: MedRagTheme.primaryCyan.withValues(alpha: 0.1),
              border: Border.all(
                  color: MedRagTheme.primaryCyan.withValues(alpha: 0.2)),
            ),
            child: Icon(icon, size: 20, color: MedRagTheme.primaryCyan),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.white.withValues(alpha: 0.6),
            ),
          ),
        ],
      ),
    );
  }
}
