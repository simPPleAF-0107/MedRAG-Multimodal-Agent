import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/user_provider.dart';
import '../services/api_service.dart';
import '../utils/ux_utils.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _identifierController = TextEditingController(); // email or phone
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _selectedRole = 'patient'; // default

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
         context.read<UserProvider>().setUser(res['user_id'].toString(), res['email'], res['role']);
      }
    } catch (e) {
      if (mounted) {
        UxUtils.showToast(context, 'Login Failed: \n${e.toString()}', isError: true);
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
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
               const SizedBox(height: 20),
               Icon(Icons.monitor_heart_rounded, size: 84, color: Theme.of(context).primaryColor),
               const SizedBox(height: 32),
               Text(
                 'MedRAG', 
                 textAlign: TextAlign.center,
                 style: Theme.of(context).textTheme.displayLarge?.copyWith(
                   color: Theme.of(context).primaryColor,
                 ),
               ),
               const SizedBox(height: 12),
               Text(
                 'Secure Clinical Portal', 
                 textAlign: TextAlign.center,
                 style: Theme.of(context).textTheme.titleMedium?.copyWith(
                   color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                 ),
               ),
               const SizedBox(height: 40),

               // Role Toggle
               Row(
                 children: [
                   Expanded(
                     child: _buildRoleButton('patient', 'Patient', Icons.person_rounded),
                   ),
                   const SizedBox(width: 16),
                   Expanded(
                     child: _buildRoleButton('doctor', 'Doctor', Icons.medical_services_rounded),
                   ),
                 ],
               ),
               
               const SizedBox(height: 32),
               TextField(
                 controller: _identifierController,
                 textInputAction: TextInputAction.next,
                 decoration: const InputDecoration(
                   labelText: 'Email or Phone Number',
                   prefixIcon: Icon(Icons.perm_contact_calendar_rounded),
                 ),
                 keyboardType: TextInputType.emailAddress,
               ),
               const SizedBox(height: 20),
               TextField(
                 controller: _passwordController,
                 textInputAction: TextInputAction.done,
                 onSubmitted: (_) => _handleLogin(),
                 decoration: const InputDecoration(
                   labelText: 'Password',
                   prefixIcon: Icon(Icons.lock_outline_rounded),
                 ),
                 obscureText: true,
               ),
               const SizedBox(height: 40),
               SizedBox(
                 height: 56,
                 child: ElevatedButton(
                   onPressed: _isLoading ? null : _handleLogin,
                   child: _isLoading 
                      ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2.5))
                      : const Text('Sign In', style: TextStyle(fontSize: 18, letterSpacing: 0.5)),
                 ),
               ),
               const SizedBox(height: 24),
               
               if (_selectedRole == 'patient')
                 TextButton(
                   onPressed: () {
                     Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RegisterScreen()));
                   },
                   child: const Text('New Patient? Create an Account'),
                 )
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRoleButton(String role, String label, IconData icon) {
    bool isSelected = _selectedRole == role;
    return InkWell(
      onTap: () {
        UxUtils.hapticLight();
        setState(() => _selectedRole = role);
      },
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? Theme.of(context).primaryColor.withOpacity(0.1) : Colors.transparent,
          border: Border.all(
            color: isSelected ? Theme.of(context).primaryColor : Colors.grey.withOpacity(0.3),
            width: 2
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          children: [
            Icon(icon, color: isSelected ? Theme.of(context).primaryColor : Colors.grey),
            const SizedBox(height: 8),
            Text(label, style: TextStyle(
              color: isSelected ? Theme.of(context).primaryColor : Colors.grey,
              fontWeight: FontWeight.bold
            )),
          ],
        ),
      ),
    );
  }
}
