import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';

import 'providers/user_provider.dart';
import 'providers/report_provider.dart';

import 'utils/theme.dart';
import 'utils/ux_utils.dart';

import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/upload_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/report_screen.dart';
import 'screens/tracker_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => UserProvider()),
        ChangeNotifierProvider(create: (_) => ReportProvider()),
      ],
      child: const MedRAGApp(),
    ),
  );
}

class MedRAGApp extends StatelessWidget {
  const MedRAGApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        FocusManager.instance.primaryFocus?.unfocus();
      },
      child: MaterialApp(
        title: 'MedRAG Mobile',
        theme: MedRagTheme.lightTheme,
        debugShowCheckedModeBanner: false,
        home: Consumer<UserProvider>(
          builder: (context, user, _) {
            return user.isAuthenticated ? const MainNavigation() : const LoginScreen();
          }
        ),
      ),
    );
  }
}

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const DashboardScreen(),
    const UploadScreen(),
    const ChatScreen(),
    const ReportScreen(),
    const TrackerScreen(),
  ];

  final List<IconData> _icons = [
    Icons.dashboard_rounded,
    Icons.psychology_rounded,
    Icons.chat_bubble_rounded,
    Icons.description_rounded,
    Icons.query_stats_rounded,
  ];

  final List<String> _labels = [
    'Dash',
    'Upload',
    'Agent',
    'Logs',
    'Track',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        switchInCurve: Curves.easeOutCubic,
        switchOutCurve: Curves.easeInCubic,
        transitionBuilder: (Widget child, Animation<double> animation) {
          return FadeTransition(
            opacity: animation,
            child: SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0.0, 0.05),
                end: Offset.zero,
              ).animate(animation),
              child: child,
            ),
          );
        },
        child: Container(
          key: ValueKey<int>(_currentIndex),
          child: _screens[_currentIndex],
        ),
      ),
      bottomNavigationBar: Container(
        margin: const EdgeInsets.only(left: 20, right: 20, bottom: 24),
        height: 70,
        decoration: MedRagTheme.glassDecoration.copyWith(
          borderRadius: BorderRadius.circular(35),
          boxShadow: MedRagTheme.neonShadow,
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(35),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(_icons.length, (index) {
                final isSelected = _currentIndex == index;
                return GestureDetector(
                  onTap: () {
                    if (_currentIndex != index) {
                      UxUtils.hapticLight();
                      setState(() => _currentIndex = index);
                    }
                  },
                  behavior: HitTestBehavior.opaque,
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    curve: Curves.easeOutBack,
                    padding: EdgeInsets.symmetric(
                      horizontal: isSelected ? 18 : 10,
                      vertical: 12,
                    ),
                    decoration: BoxDecoration(
                      color: isSelected 
                        ? MedRagTheme.primaryCyan.withOpacity(0.15) 
                        : Colors.transparent,
                      borderRadius: BorderRadius.circular(20),
                      border: isSelected 
                        ? Border.all(color: MedRagTheme.primaryCyan.withOpacity(0.5)) 
                        : Border.all(color: Colors.transparent),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _icons[index],
                          color: isSelected ? MedRagTheme.primaryCyan : MedRagTheme.textMuted,
                          size: isSelected ? 26 : 24,
                        ).animate(target: isSelected ? 1 : 0)
                         .scale(end: const Offset(1.1, 1.1), duration: 200.ms, curve: Curves.easeOutBack)
                         .tint(color: MedRagTheme.primaryCyan),
                        
                        if (isSelected) 
                           Padding(
                             padding: const EdgeInsets.only(left: 6.0),
                             child: Text(
                               _labels[index],
                               style: TextStyle(
                                 color: MedRagTheme.primaryCyan,
                                 fontWeight: FontWeight.bold,
                                 fontSize: 13,
                               ),
                             ).animate().fade(duration: 200.ms).slideX(begin: -0.2, end: 0),
                           )
                      ],
                    ),
                  ),
                );
              }),
            ),
          ),
        ),
      ).animate().slideY(begin: 1.0, end: 0.0, duration: 600.ms, curve: Curves.easeOutCubic),
    );
  }
}
