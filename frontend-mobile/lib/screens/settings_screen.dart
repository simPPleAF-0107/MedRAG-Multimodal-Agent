import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:ui' as blur_filter;
import '../providers/settings_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final settings = Provider.of<SettingsProvider>(context);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A), // Obsidian background
      body: Stack(
        children: [
          // Ambient blobs
          Positioned(
            top: -50,
            left: -50,
            child: Container(
              width: 300,
              height: 300,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0x3300D4FF), // Clinical Cyan opacity
              ),
              child: BackdropFilter(
                filter: ColorFilter.mode(Colors.black.withValues(alpha: 0.1), BlendMode.dstATop),
                child: Container(color: Colors.transparent),
              ),
            ),
          ),
          Positioned(
            bottom: -100,
            right: -50,
            child: Container(
              width: 400,
              height: 400,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Color(0x1110E8A0), // Emerald overlay
              ),
            ),
          ),

          SafeArea(
            child: CustomScrollView(
              slivers: [
                SliverAppBar(
                  expandedHeight: 120.0,
                  backgroundColor: Colors.transparent,
                  elevation: 0,
                  pinned: true,
                  flexibleSpace: FlexibleSpaceBar(
                    titlePadding: const EdgeInsets.only(left: 20, bottom: 16),
                    title: const Text(
                      'System Configuration',
                      style: TextStyle(
                        fontFamily: 'Inter',
                        fontWeight: FontWeight.w900,
                        letterSpacing: -1.0,
                        color: Colors.white,
                        shadows: [Shadow(color: Colors.black26, blurRadius: 10)],
                      ),
                    ),
                    background: Container(color: Colors.transparent),
                  ),
                ),
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildSectionHeader('Appearance', Icons.color_lens_rounded),
                        const SizedBox(height: 16),
                        _buildGlassCard(
                          child: Column(
                            children: [
                              SwitchListTile(
                                activeTrackColor: const Color(0xFF00D4FF),
                                activeThumbColor: Colors.white,
                                title: const Text('Dark Mode', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                subtitle: const Text('Toggle obsidian spatial theme', style: TextStyle(color: Colors.white60, fontSize: 12)),
                                value: settings.themeMode == ThemeMode.dark,
                                onChanged: (val) => settings.toggleTheme(val),
                              ),
                              const Divider(color: Colors.white10),
                              SwitchListTile(
                                activeTrackColor: const Color(0xFF10E8A0),
                                activeThumbColor: Colors.white,
                                title: const Text('Push Notifications', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                subtitle: const Text('Alerts for diagnostic reports', style: TextStyle(color: Colors.white60, fontSize: 12)),
                                value: settings.notificationsEnabled,
                                onChanged: (val) => settings.toggleNotifications(val),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 32),
                        _buildSectionHeader('Agent Parameters', Icons.memory_rounded),
                        const SizedBox(height: 16),
                        _buildGlassCard(
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    const Text('Diagnostic Temperature', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                    Text(settings.llmTemp.toStringAsFixed(1), style: const TextStyle(color: Color(0xFF00D4FF), fontWeight: FontWeight.bold)),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Slider(
                                  value: settings.llmTemp,
                                  min: 0.0,
                                  max: 1.0,
                                  divisions: 10,
                                  activeColor: const Color(0xFF00D4FF),
                                  inactiveColor: Colors.white24,
                                  onChanged: (val) => settings.setLlmTemp(val),
                                ),
                                const Text('Lower matches rigid FDA protocols; Higher allows exploratory associations.', style: TextStyle(color: Colors.white54, fontSize: 11)),
                                const SizedBox(height: 24),
                                const Text('Self-Correction Strictness', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                const SizedBox(height: 12),
                                Row(
                                  children: [
                                    _buildPillButton('low', settings),
                                    const SizedBox(width: 8),
                                    _buildPillButton('medium', settings),
                                    const SizedBox(width: 8),
                                    _buildPillButton('high', settings),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: const Color(0xFF00D4FF), size: 24),
        const SizedBox(width: 12),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.w700,
            letterSpacing: -0.5,
          ),
        ),
      ],
    );
  }

  Widget _buildGlassCard({required Widget child}) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: BackdropFilter(
        filter: blur_filter.ImageFilter.blur(sigmaX: 20, sigmaY: 20),
        child: Container(
          width: double.infinity,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                const Color(0xFFffffff).withValues(alpha: 0.05),
                const Color(0xFFFFFFFF).withValues(alpha: 0.01),
              ],
              stops: const [0.1, 1],
            ),
          ),
          child: child,
        ),
      ),
    );
  }

  Widget _buildPillButton(String level, SettingsProvider settings) {
    final isSelected = settings.agentStrictness == level;
    return Expanded(
      child: GestureDetector(
        onTap: () => settings.setAgentStrictness(level),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0x3300D4FF) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? const Color(0xFF00D4FF) : Colors.white12,
              width: 1,
            ),
            boxShadow: isSelected ? [const BoxShadow(color: Color(0x3300D4FF), blurRadius: 10)] : [],
          ),
          child: Center(
            child: Text(
              level.characters.first.toUpperCase() + level.substring(1),
              style: TextStyle(
                color: isSelected ? const Color(0xFF00D4FF) : Colors.white54,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
