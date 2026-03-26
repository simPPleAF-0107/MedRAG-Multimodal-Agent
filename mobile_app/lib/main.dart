import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

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
        // Dismiss keyboard globally when tapping outside input fields
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -5),
            )
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            if (_currentIndex != index) {
              UxUtils.hapticLight();
              setState(() => _currentIndex = index);
            }
          },
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.dashboard_rounded), label: 'Dashboard'),
            BottomNavigationBarItem(icon: Icon(Icons.psychology_rounded), label: 'RAG Engine'),
            BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_rounded), label: 'Agent'),
            BottomNavigationBarItem(icon: Icon(Icons.description_rounded), label: 'Reports'),
            BottomNavigationBarItem(icon: Icon(Icons.query_stats_rounded), label: 'Trackers'),
          ],
        ),
      ),
    );
  }
}
