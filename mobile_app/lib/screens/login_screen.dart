import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/user_provider.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _handleLogin() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) return;

    setState(() => _isLoading = true);

    try {
      final res = await ApiService().login(_emailController.text, _passwordController.text);
      if (mounted && res['status'] == 'success') {
         context.read<UserProvider>().setUser(res['user_id'].toString(), res['email']);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
               Icon(Icons.monitor_heart, size: 80, color: Colors.blue.shade600),
               const SizedBox(height: 24),
               const Text(
                 'MedRAG Mobile', 
                 textAlign: TextAlign.center,
                 style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold)
               ),
               const SizedBox(height: 8),
               Text(
                 'Research-Grade Clinical UI', 
                 textAlign: TextAlign.center,
                 style: TextStyle(fontSize: 16, color: Colors.grey.shade600)
               ),
               const SizedBox(height: 48),
               TextField(
                 controller: _emailController,
                 decoration: InputDecoration(
                   labelText: 'Email',
                   prefixIcon: const Icon(Icons.email),
                   border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                 ),
                 keyboardType: TextInputType.emailAddress,
               ),
               const SizedBox(height: 16),
               TextField(
                 controller: _passwordController,
                 decoration: InputDecoration(
                   labelText: 'Password',
                   prefixIcon: const Icon(Icons.lock),
                   border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                 ),
                 obscureText: true,
               ),
               const SizedBox(height: 32),
               ElevatedButton(
                 onPressed: _isLoading ? null : _handleLogin,
                 style: ElevatedButton.styleFrom(
                   padding: const EdgeInsets.symmetric(vertical: 16),
                   shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                   backgroundColor: Colors.blue.shade600,
                 ),
                 child: _isLoading 
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Text('Sign In', style: TextStyle(fontSize: 16, color: Colors.white)),
               )
            ],
          ),
        ),
      ),
    );
  }
}
