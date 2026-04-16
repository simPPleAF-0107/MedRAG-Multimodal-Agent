import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../providers/user_provider.dart';
import '../services/api_service.dart';
import '../utils/theme.dart';
import '../utils/ux_utils.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _identifierController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _selectedRole = 'patient';

  Future<void> _handleLogin() async {
    FocusScope.of(context).unfocus();
    if (_identifierController.text.isEmpty || _passwordController.text.isEmpty) {
      UxUtils.showToast(context, 'Please enter credentials', isError: true);
      return;
    }

    UxUtils.hapticLight();
    setState(() => _isLoading = true);

    try {
      final res = await ApiService().login(
        identifier: _identifierController.text, 
        password: _passwordController.text,
        role: _selectedRole,
      );
      if (mounted && res['status'] == 'success') {
         UxUtils.hapticMedium();
         context.read<UserProvider>().setUser(res['user_id'].toString(), res['email'], res['role'], userName: res['name'], userSex: res['sex']);
      }
    } catch (e) {
      if (mounted) {
        UxUtils.showToast(context, 'Login Failed: \n$e', isError: true);
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      body: Stack(
        children: [
          // Background Glows
          Positioned(
            top: -50,
            left: -100,
            child: Container(
              width: 300, height: 300,
              decoration: BoxDecoration(shape: BoxShape.circle, color: MedRagTheme.primaryCyan.withValues(alpha: 0.15)),
            ).animate(onPlay: (controller) => controller.repeat(reverse: true)).moveX(end: 100, duration: 5.seconds),
          ),
          Positioned(
            bottom: -50,
            right: -100,
            child: Container(
              width: 300, height: 300,
              decoration: BoxDecoration(shape: BoxShape.circle, color: MedRagTheme.secondaryCoral.withValues(alpha: 0.1)),
            ).animate(onPlay: (controller) => controller.repeat(reverse: true)).moveY(end: 100, duration: 4.seconds),
          ),
          
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
                child: Container(
                  padding: const EdgeInsets.all(24),
                  decoration: MedRagTheme.glassDecoration,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(20),
                    child: BackdropFilter(
                      filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const SizedBox(height: 10),
                          Hero(
                            tag: 'app_logo',
                            child: Icon(Icons.monitor_heart_rounded, size: 84, color: Theme.of(context).primaryColor),
                          ).animate().scale(delay: 200.ms, duration: 600.ms, curve: Curves.elasticOut),
                          const SizedBox(height: 24),
                          Text(
                            'MedRAG', 
                            textAlign: TextAlign.center,
                            style: Theme.of(context).textTheme.displayLarge?.copyWith(
                              color: Theme.of(context).primaryColor,
                            ),
                          ).animate().fadeIn(delay: 300.ms).slideY(begin: 0.2, end: 0),
                          const SizedBox(height: 8),
                          Text(
                            'Secure Clinical Portal', 
                            textAlign: TextAlign.center,
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                            ),
                          ).animate().fadeIn(delay: 400.ms),
                          const SizedBox(height: 40),

                          Row(
                            children: [
                              Expanded(child: _buildRoleButton('patient', 'Patient', Icons.person_rounded)),
                              const SizedBox(width: 16),
                              Expanded(child: _buildRoleButton('doctor', 'Doctor', Icons.medical_services_rounded)),
                            ],
                          ).animate().fadeIn(delay: 500.ms).slideX(begin: 0.1, end: 0),
                          const SizedBox(height: 32),
                          
                          TextField(
                            controller: _identifierController,
                            textInputAction: TextInputAction.next,
                            decoration: const InputDecoration(labelText: 'Email or Phone Number', prefixIcon: Icon(Icons.perm_contact_calendar_rounded)),
                            keyboardType: TextInputType.emailAddress,
                          ).animate().fadeIn(delay: 600.ms).slideX(begin: -0.1, end: 0),
                          const SizedBox(height: 20),
                          TextField(
                            controller: _passwordController,
                            textInputAction: TextInputAction.done,
                            onSubmitted: (_) => _handleLogin(),
                            decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline_rounded)),
                            obscureText: true,
                          ).animate().fadeIn(delay: 700.ms).slideX(begin: -0.1, end: 0),
                          const SizedBox(height: 32),
                          
                          SizedBox(
                            height: 56,
                            child: ElevatedButton(
                              onPressed: _isLoading ? null : _handleLogin,
                              child: _isLoading 
                                 ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: MedRagTheme.backgroundDark, strokeWidth: 2.5))
                                 : const Text('Sign In', style: TextStyle(fontSize: 18, letterSpacing: 0.5)),
                            ),
                          ).animate().fadeIn(delay: 800.ms).scale(begin: const Offset(0.9, 0.9)),
                          const SizedBox(height: 24),
                          
                          if (_selectedRole == 'patient')
                            TextButton(
                              onPressed: () {
                                Navigator.of(context).push(PageRouteBuilder(
                                  pageBuilder: (context, animation, secondaryAnimation) => const RegisterScreen(),
                                  transitionsBuilder: (context, animation, secondaryAnimation, child) {
                                    return FadeTransition(opacity: animation, child: child);
                                  },
                                ));
                              },
                              child: const Text('New Patient? Create an Account'),
                            ).animate().fadeIn(delay: 900.ms)
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRoleButton(String role, String label, IconData icon) {
    bool isSelected = _selectedRole == role;
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOutCubic,
      child: InkWell(
        onTap: () {
          UxUtils.hapticLight();
          setState(() => _selectedRole = role);
        },
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: isSelected ? Theme.of(context).primaryColor.withValues(alpha: 0.15) : Colors.white.withValues(alpha: 0.05),
            border: Border.all(
              color: isSelected ? Theme.of(context).primaryColor : Colors.white.withValues(alpha: 0.1),
              width: isSelected ? 2 : 1
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: isSelected ? MedRagTheme.neonShadow : [],
          ),
          child: Column(
            children: [
              Icon(icon, color: isSelected ? Theme.of(context).primaryColor : MedRagTheme.textMuted),
              const SizedBox(height: 8),
              Text(label, style: TextStyle(
                color: isSelected ? Theme.of(context).primaryColor : MedRagTheme.textMuted,
                fontWeight: FontWeight.bold
              )),
            ],
          ),
        ),
      ),
    );
  }
}
